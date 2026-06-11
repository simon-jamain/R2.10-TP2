# Service 2 — Fonctions Statistiques JSON

API REST Flask pour effectuer des calculs statistiques sur des données passées en JSON.

- **Port** : 5002
- **Dépendances** : Flask, NumPy, SciPy

## Installation

```bash
cd service2_statistiques
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
python app.py
```

## Routes disponibles

### POST /stats/describe
Calcule les statistiques descriptives d'un tableau de valeurs.

**Requête :**
```json
{"data": [12.5, 15.3, 8.7, 21.0, 13.2, 9.8, 17.6, 11.4]}
```

**Réponse (200 OK) :**
```json
{
  "operation": "description",
  "resultat": {
    "n": 8, "moyenne": 13.6875, "mediane": 12.85,
    "ecart_type": 4.1101, "variance": 16.8927,
    "minimum": 8.7, "maximum": 21.0,
    "q1": 11.0, "q3": 15.875, "etendue": 12.3
  }
}
```

---