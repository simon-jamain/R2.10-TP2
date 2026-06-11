from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

def parse_matrix(data, key):     
    """Convertit une liste de listes en tableau NumPy."""     
    try:
        return np.array(data[key], dtype=float)
    except (KeyError, ValueError) as e:
        raise ValueError(f"Matrice '{key}' invalide : {e}")

@app.route('/matrices/determinant', methods=['POST'])
def determinant_matrix():
    data = request.get_json()

    try:
        A = parse_matrix(data, 'A')

        if A.shape[0] != A.shape[1]:
            return jsonify({'erreur': 'La matrice doit etre carree'}), 400

        det = np.linalg.det(A)
        return jsonify({'operation': 'determinant', 'resultat': round(det, 6)})

    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5001)
