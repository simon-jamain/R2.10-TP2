from flask import Flask, request, jsonify
import pandas as pd           # Pour lire et manipuler le fichier CSV
import mysql.connector        # Pour se connecter à MySQL
from dotenv import load_dotenv
import os
import io                     # Pour lire le fichier CSV depuis la mémoire

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

app = Flask(__name__)

# ── Constantes ────────────────────────────────────────────────────────────────

# Colonnes qui doivent obligatoirement être présentes dans le CSV
COLONNES_REQUISES = {'nom_serie', 'valeur'}

# Colonnes acceptées dans le CSV (les autres seront ignorées)
COLONNES_VALIDES  = {'nom_serie', 'valeur', 'categorie', 'date_mesure'}

# Taille maximale du fichier CSV autorisée : 5 Mo
TAILLE_MAX_OCTETS = 5 * 1024 * 1024  # 5 Mo

# ── Connexion MySQL ───────────────────────────────────────────────────────────

def get_connection():
    """Retourne une connexion MySQL à partir des variables d'environnement."""
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

# ── Route 1 : Upload CSV ──────────────────────────────────────────────────────

@app.route('/upload/csv', methods=['POST'])
def upload_csv():

    # 1. Vérifier que le fichier est bien présent dans la requête
    if 'file' not in request.files:
        return jsonify({'erreur': 'Aucun fichier envoyé (clé "file" manquante)'}), 400

    file = request.files['file']

    # 2. Vérifier que le nom du fichier n'est pas vide
    if file.filename == '':
        return jsonify({'erreur': 'Nom de fichier vide'}), 400

    # 3. Vérifier que c'est bien un fichier CSV
    if not file.filename.endswith('.csv'):
        return jsonify({'erreur': 'Seuls les fichiers .csv sont acceptés'}), 400

    # 4. Lire et valider le contenu CSV
    try:
        content = file.read()

        # Vérifier que le fichier ne dépasse pas 5 Mo
        if len(content) > TAILLE_MAX_OCTETS:
            return jsonify({'erreur': 'Fichier trop volumineux (max 5 Mo)'}), 413

        # Charger le contenu CSV dans un DataFrame pandas
        df = pd.read_csv(io.BytesIO(content))

    except Exception as e:
        return jsonify({'erreur': f'Lecture CSV impossible : {e}'}), 400

    # 5. Vérifier que les colonnes obligatoires sont présentes
    colonnes_manquantes = COLONNES_REQUISES - set(df.columns)
    if colonnes_manquantes:
        return jsonify({
            'erreur'    : 'Colonnes obligatoires manquantes',
            'manquantes': list(colonnes_manquantes)
        }), 400

    # 6. Nettoyer les données
    # Garder uniquement les colonnes valides
    df = df[[c for c in df.columns if c in COLONNES_VALIDES]]

    # Convertir la colonne valeur en nombre, les valeurs invalides deviennent NaN
    df['valeur']     = pd.to_numeric(df['valeur'], errors='coerce')

    # Compter les lignes invalides avant de les supprimer
    lignes_invalides = int(df['valeur'].isna().sum())

    # Supprimer les lignes avec une valeur manquante
    df.dropna(subset=['valeur'], inplace=True)

    # Si toutes les lignes sont invalides, on arrête
    if df.empty:
        return jsonify({'erreur': 'Aucune ligne valide dans le CSV'}), 400

    # 7. Insérer les lignes valides dans MySQL
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
                    # Si la colonne existe on prend la valeur, sinon on met None
                    str(row['categorie'])   if 'categorie'   in df.columns else None,
                    str(row['date_mesure']) if 'date_mesure' in df.columns else None,
                )
            )
            insertions += 1

        # Valider toutes les insertions en une seule fois
        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        return jsonify({'erreur': 'Erreur base de données', 'detail': str(e)}), 500

    # 8. Retourner un résumé de l'opération
    return jsonify({
        'statut'                   : 'success',
        'lignes_inserees'          : insertions,
        'lignes_invalides_ignorees': lignes_invalides,
        'message'                  : f'{insertions} ligne(s) chargée(s) dans la table donnees'
    }), 201

# ── Route 2 : Lister les séries (bonus) ──────────────────────────────────────

@app.route('/upload/series', methods=['GET'])
def list_series():
    """Retourne la liste des séries chargées et leur nombre de points."""
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        # Récupère pour chaque série : le nombre de points, la date de début et de fin
        cursor.execute(
            'SELECT nom_serie, COUNT(*) AS n, MIN(date_mesure), MAX(date_mesure)'
            ' FROM donnees GROUP BY nom_serie ORDER BY nom_serie'
        )

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # Formater les résultats en liste de dictionnaires
        series = [
            {
                'serie'    : r[0],
                'n_points' : r[1],
                'debut'    : str(r[2]),
                'fin'      : str(r[3])
            }
            for r in rows
        ]

        return jsonify({'series': series, 'total': len(series)})

    except Exception as e:
        return jsonify({'erreur': 'Erreur base de données', 'detail': str(e)}), 500

# ── Lancement ─────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, port=5004)