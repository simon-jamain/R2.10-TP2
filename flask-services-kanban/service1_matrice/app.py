from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

def parse_matrix(data, key):     
    """Convertit une liste de listes en tableau NumPy."""     
    try:
        return np.array(data[key], dtype=float)
    except (KeyError, ValueError) as e:
        raise ValueError(f"Matrice '{key}' invalide : {e}")

@app.route('/matrices/add', methods=['POST'])
def add_matrices():
    """Additionne deux matrices A et B de mêmes dimensions."""
    data = request.get_json()

    try:
        A = parse_matrix(data, 'A')
        B = parse_matrix(data, 'B')

        if A.shape != B.shape:
            return jsonify({
                'erreur': f'Dimensions incompatibles : {A.shape} ≠ {B.shape}'
            }), 400

        return jsonify({
            'operation': 'addition',
            'resultat': (A + B).tolist()
        }), 200

    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5001)
