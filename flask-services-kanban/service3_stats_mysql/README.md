# Service 3 — Statistiques depuis MySQL

## Description
API REST Flask qui lit des données depuis une base MySQL et retourne des statistiques descriptives et de corrélation.

## Installation

```bash
cd service3_stats_mysql
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
```

## Configuration

Créer un fichier `.env` dans ce dossier :

```
DB_HOST=localhost 
DB_PORT=3306 
DB_USER=flask_user 
DB_PASSWORD=mdp
DB_NAME=flask_stats 
```

## Lancer le service

```bash
python app.py
```

Le service tourne sur **http://localhost:5003**

---

## Routes disponibles

### GET /db/stats/describe

Retourne les statistiques descriptives d'une série depuis MySQL.

**Paramètre URL :**
| Paramètre | Type | Obligatoire | Description |
|-----------|------|-------------|-------------|
| serie | string | Oui | Nom de la série à analyser |

**Exemple :**
```bash
curl "http://localhost:5003/db/stats/describe?serie=serie_A"
```

**Réponse (200 OK) :**
```json
{
  "source": "mysql",
  "resultat": {
    "serie": "serie_A",
    "n": 5,
    "moyenne": 14.14,
    "mediane": 13.2,
    "ecart_type": 4.4517,
    "minimum": 8.7,
    "maximum": 21.0
  }
}
```

**Erreurs possibles :**
- `400` : paramètre `serie` manquant
- `404` : série introuvable dans la base
- `500` : erreur de connexion MySQL

---

### GET /db/stats/correlation

Calcule le coefficient de corrélation de Pearson entre deux séries depuis MySQL.

**Paramètres URL :**
| Paramètre | Type | Obligatoire | Description |
|-----------|------|-------------|-------------|
| serie_x | string | Oui | Nom de la première série |
| serie_y | string | Oui | Nom de la deuxième série |

**Exemple :**
```bash
curl "http://localhost:5003/db/stats/correlation?serie_x=serie_A&serie_y=serie_B"
```

**Réponse (200 OK) :**
```json
{
  "source": "mysql",
  "series": {
    "x": "serie_A",
    "y": "serie_B",
    "n_points": 5
  },
  "resultat": {
    "r": 0.9123,
    "p_value": 0.030,
    "significatif": true
  }
}
```

**Erreurs possibles :**
- `400` : paramètres `serie_x` ou `serie_y` manquants
- `404` : une des séries introuvable dans la base
- `500` : erreur de connexion MySQL

---

## Tests

**Test HTML/JS** — ouvrir dans le navigateur :
```
test_service3.html
```

**Test Python** :
```bash
pip install requests
python test_service3.py
```