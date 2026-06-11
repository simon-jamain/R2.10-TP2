from flask import Flask, request, jsonify
import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import os
import io

load_dotenv()

app = Flask(__name__)

# ── Constantes ────────────────────────────────────────────────────────────────

COLONNES_REQUISES   = {'nom_serie', 'valeur'}
COLONNES_VALIDES    = {'nom_serie', 'valeur', 'categorie', 'date_mesure'}
TAILLE_MAX_OCTETS   = 5 * 1024 * 1024  # 5 Mo

# ── Connexion MySQL ───────────────────────────────────────────────────────────

def get_connection():
    """Retourne une connexion MySQL à partir des variables d'environnement."""
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

# ── Route : Upload CSV ────────────────────────────────────────────────────────

@app.route('/upload/csv', methods=['POST'])
def upload_csv():

    # 1. Vérifier la présence du fichier
    if 'file' not in request.files:
        return jsonify({'erreur': 'Aucun fichier envoyé (clé "file" manquante)'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'erreur': 'Nom de fichier vide'}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({'erreur': 'Seuls les fichiers .csv sont acceptés'}), 400

    # 2. Lire et valider le contenu CSV
    try:
        content = file.read()

        if len(content) > TAILLE_MAX_OCTETS:
            return jsonify({'erreur': 'Fichier trop volumineux (max 5 Mo)'}), 413

        df = pd.read_csv(io.BytesIO(content))

    except Exception as e:
        return jsonify({'erreur': f'Lecture CSV impossible : {e}'}), 400

    # 3. Vérifier les colonnes obligatoires
    colonnes_manquantes = COLONNES_REQUISES - set(df.columns)
    if colonnes_manquantes:
        return jsonify({
            'erreur'    : 'Colonnes obligatoires manquantes',
            'manquantes': list(colonnes_manquantes)
        }), 400

    # 4. Nettoyer les données
    df = df[[c for c in df.columns if c in COLONNES_VALIDES]]

    df['valeur']      = pd.to_numeric(df['valeur'], errors='coerce')
    lignes_invalides  = int(df['valeur'].isna().sum())

    df.dropna(subset=['valeur'], inplace=True)

    if df.empty:
        return jsonify({'erreur': 'Aucune ligne valide dans le CSV'}), 400

    # 5. Insérer dans MySQL
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        insertions = 0
        for _, row in df.iterrows():
            cursor.execute(
                'INSERT INTO donnees (nom_serie, valeur, categorie, date_mesure)'
                ' VALUES (%s, %s, %s, %s)',
                (
                    str(row['nom_serie']),
                    float(row['valeur']),
                    str(row['categorie'])  if 'categorie'   in df.columns else None,
                    str(row['date_mesure']) if 'date_mesure' in df.columns else None,
                )
            )
            insertions += 1

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        return jsonify({'erreur': 'Erreur base de données', 'detail': str(e)}), 500

    # 6. Réponse succès
    return jsonify({
        'statut'                  : 'success',
        'lignes_inserees'         : insertions,
        'lignes_invalides_ignorees': lignes_invalides,
        'message'                 : f'{insertions} ligne(s) chargée(s) dans la table donnees'
    }), 201


# ── Lancement ─────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, port=5004)
