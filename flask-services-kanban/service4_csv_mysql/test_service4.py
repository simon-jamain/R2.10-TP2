# Tests unitaires Python — Service 4 : Upload CSV vers MySQL
# Prérequis : pip install requests
# Lancer avec : python test_service4.py

import requests

# Adresse de base du service Flask
BASE = "http://localhost:5004"

# ─── Test 1 : envoyer le fichier CSV de démonstration ────────────
# On envoie le fichier donnees_exemple.csv au service
# Le service doit l'insérer dans MySQL et retourner un statut success
with open("../data/donnees_exemple.csv", "rb") as f:
    res = requests.post(BASE + "/upload/csv", files={"file": f})
print("Test 1 - upload donnees_exemple.csv")
print("Status :", res.status_code)  # On attend 201
print("Résultat :", res.json())
print()

# ─── Test 2 : lister les séries disponibles ──────────────────────
# On appelle GET /upload/series pour voir les séries chargées
res = requests.get(BASE + "/upload/series")
print("Test 2 - lister les séries")
print("Status :", res.status_code)  # On attend 200
print("Résultat :", res.json())
print()

# ─── Test 3 : envoyer un fichier qui n'est pas un CSV ────────────
# Le service doit refuser et retourner une erreur 400
with open("../data/donnees_exemple.csv", "rb") as f:
    res = requests.post(BASE + "/upload/csv", files={"file": ("test.txt", f)})
print("Test 3 - fichier non CSV (400 attendu)")
print("Status :", res.status_code)  # On attend 400
print("Résultat :", res.json())
print()

# ─── Test 4 : envoyer une requête sans fichier ───────────────────
# Le service doit retourner une erreur 400
res = requests.post(BASE + "/upload/csv")
print("Test 4 - aucun fichier envoyé (400 attendu)")
print("Status :", res.status_code)  # On attend 400
print("Résultat :", res.json())