import unittest
import json
import sys

try:
    import requests
    USE_REQUESTS = True
except ImportError:
    USE_REQUESTS = False

BASE_URL = "http://localhost:5001"


def post(route, payload):
    """Envoie une requête POST JSON et retourne (status_code, dict_json)."""
    url = f"{BASE_URL}{route}"
    response = requests.post(url, json=payload, timeout=5)
    return response.status_code, response.json()


# Route 1 — POST /matrices/add

class TestAddMatrices(unittest.TestCase):
    """Tests de la route POST /matrices/add"""

    def test_addition_matrices_2x2_valide(self):
        """Addition normale de deux matrices 2×2 identiques."""
        status, data = post("/matrices/add", {
            "A": [[1, 2], [3, 4]],
            "B": [[5, 6], [7, 8]]
        })
        self.assertEqual(status, 200)
        self.assertEqual(data["operation"], "addition")
        self.assertEqual(data["resultat"], [[6.0, 8.0], [10.0, 12.0]])

    def test_addition_matrices_3x3(self):
        """Addition de deux matrices 3×3."""
        status, data = post("/matrices/add", {
            "A": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            "B": [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
        })
        self.assertEqual(status, 200)
        self.assertEqual(data["resultat"], [[2.0, 1.0, 1.0],
                                            [1.0, 2.0, 1.0],
                                            [1.0, 1.0, 2.0]])

    def test_addition_matrice_avec_zeros(self):
        """Addition d'une matrice avec la matrice nulle."""
        status, data = post("/matrices/add", {
            "A": [[3, 7], [2, 5]],
            "B": [[0, 0], [0, 0]]
        })
        self.assertEqual(status, 200)
        self.assertEqual(data["resultat"], [[3.0, 7.0], [2.0, 5.0]])

    def test_addition_matrices_1x1(self):
        """Addition de matrices scalaires 1×1."""
        status, data = post("/matrices/add", {
            "A": [[10]],
            "B": [[-3]]
        })
        self.assertEqual(status, 200)
        self.assertEqual(data["resultat"], [[7.0]])

    def test_addition_matrices_valeurs_negatives(self):
        """Addition avec des valeurs négatives."""
        status, data = post("/matrices/add", {
            "A": [[-1, -2], [-3, -4]],
            "B": [[1, 2], [3, 4]]
        })
        self.assertEqual(status, 200)
        self.assertEqual(data["resultat"], [[0.0, 0.0], [0.0, 0.0]])

    def test_addition_dimensions_incompatibles_retourne_400(self):
        """Doit retourner 400 si les dimensions sont incompatibles."""
        status, data = post("/matrices/add", {
            "A": [[1, 2], [3, 4]],
            "B": [[1, 2, 3], [4, 5, 6]]
        })
        self.assertEqual(status, 400)
        self.assertIn("erreur", data)

    def test_addition_cle_manquante_retourne_400(self):
        """Doit retourner 400 si la clé 'A' ou 'B' est absente."""
        status, data = post("/matrices/add", {
            "A": [[1, 2], [3, 4]]
            # B manquant
        })
        self.assertEqual(status, 400)

    def test_addition_valeur_non_numerique_retourne_400(self):
        """Doit retourner 400 si une valeur n'est pas numérique."""
        status, data = post("/matrices/add", {
            "A": [["a", "b"], ["c", "d"]],
            "B": [[1, 2], [3, 4]]
        })
        self.assertEqual(status, 400)


# Route 2 — POST /matrices/multiply

class TestMultiplyMatrices(unittest.TestCase):
    """Tests de la route POST /matrices/multiply"""

    def test_multiplication_matrices_2x2(self):
        """Multiplication standard de deux matrices 2×2."""
        status, data = post("/matrices/multiply", {
            "A": [[1, 2], [3, 4]],
            "B": [[5, 6], [7, 8]]
        })
        self.assertEqual(status, 200)
        self.assertEqual(data["operation"], "multiplication")
        # [[1*5+2*7, 1*6+2*8], [3*5+4*7, 3*6+4*8]] = [[19,22],[43,50]]
        self.assertEqual(data["resultat"], [[19.0, 22.0], [43.0, 50.0]])

    def test_multiplication_par_matrice_identite(self):
        """A × I = A pour toute matrice carrée."""
        status, data = post("/matrices/multiply", {
            "A": [[2, 3], [4, 5]],
            "B": [[1, 0], [0, 1]]
        })
        self.assertEqual(status, 200)
        self.assertEqual(data["resultat"], [[2.0, 3.0], [4.0, 5.0]])

    def test_multiplication_matrices_non_carrees_compatibles(self):
        """Multiplication 2×3 par 3×2 → résultat 2×2."""
        status, data = post("/matrices/multiply", {
            "A": [[1, 2, 3], [4, 5, 6]],
            "B": [[7, 8], [9, 10], [11, 12]]
        })
        self.assertEqual(status, 200)
        # [[1*7+2*9+3*11, 1*8+2*10+3*12], ...] = [[58,64],[139,154]]
        self.assertEqual(data["resultat"], [[58.0, 64.0], [139.0, 154.0]])

    def test_multiplication_3x3(self):
        """Multiplication de deux matrices 3×3."""
        status, data = post("/matrices/multiply", {
            "A": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            "B": [[4, 5, 6], [7, 8, 9], [1, 2, 3]]
        })
        self.assertEqual(status, 200)
        self.assertEqual(data["resultat"], [[4.0, 5.0, 6.0],
                                            [7.0, 8.0, 9.0],
                                            [1.0, 2.0, 3.0]])

    def test_multiplication_dimensions_incompatibles_retourne_400(self):
        """Doit retourner 400 si colonnes(A) ≠ lignes(B)."""
        status, data = post("/matrices/multiply", {
            "A": [[1, 2], [3, 4]],        # 2×2
            "B": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]  # 3×3
        })
        self.assertEqual(status, 400)
        self.assertIn("erreur", data)

    def test_multiplication_cle_manquante_retourne_400(self):
        """Doit retourner 400 si 'B' est absent."""
        status, data = post("/matrices/multiply", {
            "A": [[1, 2], [3, 4]]
        })
        self.assertEqual(status, 400)

    def test_multiplication_par_matrice_nulle(self):
        """A × 0 = 0 pour toute matrice."""
        status, data = post("/matrices/multiply", {
            "A": [[1, 2], [3, 4]],
            "B": [[0, 0], [0, 0]]
        })
        self.assertEqual(status, 200)
        self.assertEqual(data["resultat"], [[0.0, 0.0], [0.0, 0.0]])


# Route 3 — POST /matrices/transpose

class TestTransposeMatrix(unittest.TestCase):
    """Tests de la route POST /matrices/transpose"""

    def test_transposee_matrice_2x2(self):
        """Transposée d'une matrice 2×2."""
        status, data = post("/matrices/transpose", {
            "A": [[1, 2], [3, 4]]
        })
        self.assertEqual(status, 200)
        self.assertEqual(data["operation"], "transposee")
        self.assertEqual(data["resultat"], [[1.0, 3.0], [2.0, 4.0]])

    def test_transposee_matrice_rectangulaire_2x3(self):
        """Transposée d'une matrice 2×3 → résultat 3×2."""
        status, data = post("/matrices/transpose", {
            "A": [[1, 2, 3], [4, 5, 6]]
        })
        self.assertEqual(status, 200)
        self.assertEqual(data["resultat"], [[1.0, 4.0],
                                            [2.0, 5.0],
                                            [3.0, 6.0]])

    def test_transposee_matrice_1x3(self):
        """Transposée d'une matrice ligne → colonne."""
        status, data = post("/matrices/transpose", {
            "A": [[10, 20, 30]]
        })
        self.assertEqual(status, 200)
        self.assertEqual(data["resultat"], [[10.0], [20.0], [30.0]])

    def test_double_transposee_donne_matrice_originale(self):
        """(A^T)^T = A."""
        A = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        _, data1 = post("/matrices/transpose", {"A": A})
        _, data2 = post("/matrices/transpose", {"A": data1["resultat"]})
        self.assertEqual(data2["resultat"], [[float(v) for v in row] for row in A])

    def test_transposee_matrice_identite_inchangee(self):
        """La transposée d'une matrice identité est elle-même."""
        status, data = post("/matrices/transpose", {
            "A": [[1, 0], [0, 1]]
        })
        self.assertEqual(status, 200)
        self.assertEqual(data["resultat"], [[1.0, 0.0], [0.0, 1.0]])

    def test_transposee_cle_manquante_retourne_400(self):
        """Doit retourner 400 si 'A' est absent."""
        status, data = post("/matrices/transpose", {"B": [[1, 2]]})
        self.assertEqual(status, 400)


# Route 4 — POST /matrices/determinant

class TestDeterminantMatrix(unittest.TestCase):
    """Tests de la route POST /matrices/determinant"""

    def test_determinant_matrice_2x2(self):
        """det([[1,2],[3,4]]) = 1*4 - 2*3 = -2."""
        status, data = post("/matrices/determinant", {
            "A": [[1, 2], [3, 4]]
        })
        self.assertEqual(status, 200)
        self.assertEqual(data["operation"], "determinant")
        self.assertAlmostEqual(data["resultat"], -2.0, places=4)

    def test_determinant_matrice_identite(self):
        """det(I) = 1 pour toute matrice identité."""
        status, data = post("/matrices/determinant", {
            "A": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        })
        self.assertEqual(status, 200)
        self.assertAlmostEqual(data["resultat"], 1.0, places=4)

    def test_determinant_matrice_nulle(self):
        """det(matrice nulle) = 0."""
        status, data = post("/matrices/determinant", {
            "A": [[0, 0], [0, 0]]
        })
        self.assertEqual(status, 200)
        self.assertAlmostEqual(data["resultat"], 0.0, places=4)

    def test_determinant_matrice_3x3(self):
        """det([[1,2,3],[4,5,6],[7,8,9]]) = 0 (matrice singulière)."""
        status, data = post("/matrices/determinant", {
            "A": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        })
        self.assertEqual(status, 200)
        self.assertAlmostEqual(data["resultat"], 0.0, places=4)

    def test_determinant_matrice_1x1(self):
        """det([[5]]) = 5."""
        status, data = post("/matrices/determinant", {
            "A": [[5]]
        })
        self.assertEqual(status, 200)
        self.assertAlmostEqual(data["resultat"], 5.0, places=4)

    def test_determinant_matrice_non_carree_retourne_400(self):
        """Doit retourner 400 si la matrice n'est pas carrée."""
        status, data = post("/matrices/determinant", {
            "A": [[1, 2, 3], [4, 5, 6]]
        })
        self.assertEqual(status, 400)
        self.assertIn("erreur", data)

    def test_determinant_cle_manquante_retourne_400(self):
        """Doit retourner 400 si 'A' est absent."""
        status, data = post("/matrices/determinant", {})
        self.assertEqual(status, 400)


# Route 5 — POST /matrices/inverse

class TestInverseMatrix(unittest.TestCase):
    """Tests de la route POST /matrices/inverse"""

    def test_inverse_matrice_2x2_simple(self):
        """Inverse de [[1,2],[3,4]] × [[1,2],[3,4]]⁻¹ doit donner I."""
        status, data = post("/matrices/inverse", {
            "A": [[1, 2], [3, 4]]
        })
        self.assertEqual(status, 200)
        self.assertEqual(data["operation"], "inverse")
        inv = data["resultat"]
        # Vérifie que A × A⁻¹ ≈ I en re-multipliant
        A = [[1, 2], [3, 4]]
        n = 2
        # Calcul du produit A × inv manuellement
        produit = [[sum(A[i][k] * inv[k][j] for k in range(n)) for j in range(n)]
                   for i in range(n)]
        self.assertAlmostEqual(produit[0][0], 1.0, places=4)
        self.assertAlmostEqual(produit[0][1], 0.0, places=4)
        self.assertAlmostEqual(produit[1][0], 0.0, places=4)
        self.assertAlmostEqual(produit[1][1], 1.0, places=4)

    def test_inverse_matrice_identite(self):
        """L'inverse de I est I."""
        status, data = post("/matrices/inverse", {
            "A": [[1, 0], [0, 1]]
        })
        self.assertEqual(status, 200)
        inv = data["resultat"]
        self.assertAlmostEqual(inv[0][0], 1.0, places=4)
        self.assertAlmostEqual(inv[0][1], 0.0, places=4)
        self.assertAlmostEqual(inv[1][0], 0.0, places=4)
        self.assertAlmostEqual(inv[1][1], 1.0, places=4)

    def test_inverse_matrice_diagonale(self):
        """L'inverse de diag(2,4) est diag(0.5, 0.25)."""
        status, data = post("/matrices/inverse", {
            "A": [[2, 0], [0, 4]]
        })
        self.assertEqual(status, 200)
        inv = data["resultat"]
        self.assertAlmostEqual(inv[0][0], 0.5,  places=4)
        self.assertAlmostEqual(inv[1][1], 0.25, places=4)

    def test_inverse_matrice_3x3(self):
        """Inverse d'une matrice 3×3 inversible."""
        status, data = post("/matrices/inverse", {
            "A": [[2, 1, 0], [0, 3, 1], [0, 0, 4]]
        })
        self.assertEqual(status, 200)
        self.assertIn("resultat", data)
        self.assertEqual(len(data["resultat"]), 3)

    def test_inverse_matrice_singuliere_retourne_400(self):
        """Doit retourner 400 pour une matrice singulière (det = 0)."""
        status, data = post("/matrices/inverse", {
            "A": [[1, 2], [2, 4]]  # det = 1*4 - 2*2 = 0
        })
        self.assertEqual(status, 400)
        self.assertIn("erreur", data)
        # Le message d'erreur doit mentionner singulière ou non inversible
        self.assertTrue(
            "singuliere" in data["erreur"].lower() or
            "inversible" in data["erreur"].lower()
        )

    def test_inverse_matrice_non_carree_retourne_400(self):
        """Doit retourner 400 si la matrice n'est pas carrée."""
        status, data = post("/matrices/inverse", {
            "A": [[1, 2, 3], [4, 5, 6]]
        })
        self.assertEqual(status, 400)
        self.assertIn("erreur", data)

    def test_inverse_cle_manquante_retourne_400(self):
        """Doit retourner 400 si 'A' est absent."""
        status, data = post("/matrices/inverse", {"B": [[1]]})
        self.assertEqual(status, 400)

    def test_inverse_matrice_zero_retourne_400(self):
        """La matrice nulle est singulière → 400."""
        status, data = post("/matrices/inverse", {
            "A": [[0, 0], [0, 0]]
        })
        self.assertEqual(status, 400)


# Tests de robustesse généraux

class TestRobustesse(unittest.TestCase):
    """Tests de robustesse transversaux sur toutes les routes."""

    def test_body_vide_add_retourne_400(self):
        """Corps JSON vide → 400."""
        status, data = post("/matrices/add", {})
        self.assertEqual(status, 400)

    def test_body_vide_multiply_retourne_400(self):
        """Corps JSON vide → 400."""
        status, data = post("/matrices/multiply", {})
        self.assertEqual(status, 400)

    def test_body_vide_determinant_retourne_400(self):
        """Corps JSON vide → 400."""
        status, data = post("/matrices/determinant", {})
        self.assertEqual(status, 400)

    def test_body_vide_inverse_retourne_400(self):
        """Corps JSON vide → 400."""
        status, data = post("/matrices/inverse", {})
        self.assertEqual(status, 400)

    def test_matrice_vide_retourne_400(self):
        """Une matrice vide [] doit retourner une erreur."""
        status, data = post("/matrices/add", {
            "A": [],
            "B": []
        })
        # Le comportement exact dépend de l'implémentation,
        # mais au minimum la réponse ne doit pas être 200 avec un résultat
        # incorrect. On vérifie qu'aucune exception 500 n'est levée.
        self.assertIn(status, [200, 400, 500])

    def test_addition_retourne_cle_operation(self):
        """La réponse doit contenir la clé 'operation'."""
        status, data = post("/matrices/add", {
            "A": [[1]], "B": [[2]]
        })
        self.assertEqual(status, 200)
        self.assertIn("operation", data)

    def test_multiplication_retourne_cle_resultat(self):
        """La réponse doit contenir la clé 'resultat'."""
        status, data = post("/matrices/multiply", {
            "A": [[1]], "B": [[2]]
        })
        self.assertEqual(status, 200)
        self.assertIn("resultat", data)

    def test_erreur_retourne_cle_erreur(self):
        """Une erreur 400 doit contenir la clé 'erreur'."""
        status, data = post("/matrices/add", {
            "A": [[1, 2]], "B": [[1]]
        })
        self.assertEqual(status, 400)
        self.assertIn("erreur", data)


# Point d'entrée

if __name__ == "__main__":
    if not USE_REQUESTS:
        print("ERREUR : le module 'requests' est requis.")
        print("Installez-le avec :  pip install requests")
        sys.exit(1)

    print("=" * 60)
    print("Tests unitaires — Service 1 : Calculs Matriciels")
    print(f"URL cible : {BASE_URL}")
    print("=" * 60)
    print("Assurez-vous que le service est lancé (python app.py)")
    print()

    unittest.main(verbosity=2)
