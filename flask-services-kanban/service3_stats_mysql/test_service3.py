# Tests unitaires Python — Service 3 : Stats MySQL
# Prérequis : pip install requests
# Lancer avec : python test_service3.py

import requests

# Adresse de base du service Flask
BASE = "http://localhost:5003"

# ─── Test 1 : décrire les statistiques de serie_A ────────────────
# On appelle GET /db/stats/describe avec le paramètre serie=serie_A
# Le service doit retourner les stats (moyenne, médiane, etc.) depuis MySQL
res = requests.get(BASE + "/db/stats/describe", params={"serie": "serie_A"})
print("Test 1 - describe serie_A")
print("Status :", res.status_code)  # On attend 200
print("Résultat :", res.json())
print()

# ─── Test 2 : corrélation entre serie_A et serie_B ───────────────
# On appelle GET /db/stats/correlation avec serie_x et serie_y
# Le service doit retourner le coefficient de corrélation de Pearson
res = requests.get(BASE + "/db/stats/correlation", params={"serie_x": "serie_A", "serie_y": "serie_B"})
print("Test 2 - correlation serie_A / serie_B")
print("Status :", res.status_code)  # On attend 200
print("Résultat :", res.json())
print()

# ─── Test 3 : série inexistante ──────────────────────────────────
# On demande une série qui n'existe pas dans la base
# Le service doit retourner une erreur 404
res = requests.get(BASE + "/db/stats/describe", params={"serie": "serie_inexistante"})
print("Test 3 - série inexistante (404 attendu)")
print("Status :", res.status_code)  # On attend 404
print("Résultat :", res.json())
print()

# ─── Test 4 : paramètre manquant ─────────────────────────────────
# On appelle la route sans passer le paramètre 'serie'
# Le service doit retourner une erreur 400
res = requests.get(BASE + "/db/stats/describe")
print("Test 4 - paramètre manquant (400 attendu)")
print("Status :", res.status_code)  # On attend 400
print("Résultat :", res.json())
