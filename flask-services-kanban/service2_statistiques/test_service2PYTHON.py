import unittest
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import app

class TestDescribe(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_describe_ok(self):
        r = self.client.post('/stats/describe',
            json={"data": [12.5, 15.3, 8.7, 21.0, 13.2, 9.8, 17.6, 11.4]})
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['operation'], 'description')
        self.assertEqual(data['resultat']['n'], 8)
        self.assertAlmostEqual(data['resultat']['moyenne'], 13.6875, places=2)

    def test_describe_manque_cle(self):
        r = self.client.post('/stats/describe', json={"mauvaise_cle": [1, 2, 3]})
        self.assertEqual(r.status_code, 400)

    def test_describe_une_seule_valeur(self):
        r = self.client.post('/stats/describe', json={"data": [42]})
        self.assertEqual(r.status_code, 400)

    def test_describe_liste_vide(self):
        r = self.client.post('/stats/describe', json={"data": []})
        self.assertEqual(r.status_code, 400)

    def test_correlation_ok(self):
        r = self.client.post('/stats/correlation',
            json={"x": [1, 2, 3, 4, 5], "y": [2, 4, 5, 4, 5]})
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['operation'], 'correlation_pearson')
        self.assertIn('r', data['resultat'])
        self.assertIn('interpretation', data['resultat'])

    def test_correlation_tailles_differentes(self):
        r = self.client.post('/stats/correlation',
            json={"x": [1, 2, 3], "y": [4, 5]})
        self.assertEqual(r.status_code, 400)

    def test_correlation_manque_x(self):
        r = self.client.post('/stats/correlation',
            json={"y": [1, 2, 3]})
        self.assertEqual(r.status_code, 400)

    def test_correlation_forte_positive(self):
        r = self.client.post('/stats/correlation',
            json={"x": [1, 2, 3, 4, 5], "y": [1, 2, 3, 4, 5]})
        data = r.get_json()
        self.assertEqual(data['resultat']['interpretation'], 'forte')
        self.assertAlmostEqual(data['resultat']['r'], 1.0, places=2)

    def test_normalite_distribution_normale(self):
        r = self.client.post('/stats/test_normalite',
            json={"data": [12.5, 15.3, 8.7, 21.0, 13.2, 9.8, 17.6, 11.4]})
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['operation'], 'test_normalite_shapiro_wilk')
        self.assertIn('est_normale', data['resultat'])

    def test_normalite_manque_cle(self):
        r = self.client.post('/stats/test_normalite',
            json={"mauvaise_cle": [1, 2, 3]})
        self.assertEqual(r.status_code, 400)

    def test_normalite_une_valeur(self):
        r = self.client.post('/stats/test_normalite',
            json={"data": [1]})
        self.assertEqual(r.status_code, 400)

if __name__ == '__main__':
    unittest.main(verbosity=2)