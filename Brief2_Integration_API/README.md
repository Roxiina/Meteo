# Cyclone Tracker - Module d'Intégration API Open-Meteo

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Description

Module Python pour l'intégration et l'analyse des données météorologiques et marines de l'API Open-Meteo, avec détection automatique des conditions cycloniques dans l'océan Indien.

Ce projet fait partie du **Brief 2** du parcours de formation et démontre :
- 🌐 L'intégration d'APIs REST externes
- 🔄 La gestion d'erreurs et retry logic
- 🧪 Les tests unitaires et d'intégration
- 🏗️ Une architecture modulaire en 3 couches
- 📊 L'analyse de données météorologiques complexes

## ✨ Fonctionnalités

- **Prévisions Météorologiques** : Récupération des données météo sur 16 jours (température, pression, vent)
- **Données Marines** : Accès aux prévisions marines sur 7 jours (vagues, courants, SST)
- **Détection Cyclonique** : Algorithme d'analyse automatique des conditions cycloniques
- **Classification** : 4 catégories (Aucun, Dépression Tropicale, Tempête Tropicale, Cyclone)
- **Retry Logic** : Gestion automatique des échecs avec backoff exponentiel
- **Validation** : Validation complète des paramètres et données
- **Logging** : Traçabilité complète des opérations
- **Tests** : 41 tests (unitaires + intégration) avec 60%+ de couverture

## 🏗️ Architecture

```
Brief2_Integration_API/
├── src/
│   ├── config/           # Configuration et settings
│   │   └── settings.py   # Classe Settings avec validation
│   ├── utils/            # Utilitaires
│   │   ├── error_handler.py   # 7 exceptions personnalisées
│   │   └── api_client.py      # Client HTTP avec retry
│   ├── services/         # Services métier
│   │   ├── weather_service.py      # API Weather Forecast
│   │   ├── marine_service.py       # API Marine Weather
│   │   └── cyclone_detector.py    # Détection cyclonique
│   └── main.py           # Application démo
├── tests/                # Tests (pytest)
│   ├── conftest.py       # Fixtures
│   ├── test_weather_service.py    # 14 tests
│   ├── test_marine_service.py     # 5 tests
│   ├── test_cyclone_detector.py   # 10 tests
│   └── test_integration.py        # 7 tests (API réelles)
├── docs/                 # Documentation
│   ├── SCHEMA_ARCHITECTURE.md     # 6 diagrammes Mermaid
│   ├── CAPTURES_POSTMAN.md        # Tests API (11 tests)
│   ├── REVUE_CODE_FINALE.md       # Code review (8.6/10)
│   ├── VALIDATION_FINALE.md       # Certification
│   └── prompts/          # Historique des prompts (6 fichiers)
├── .env.example          # Template de configuration
├── .gitignore            # Exclusions Git
├── requirements.txt      # Dépendances Python
├── pytest.ini            # Configuration pytest
└── README.md             # Ce fichier
```

### Architecture en 3 Couches

1. **Config Layer** (`src/config/`)
   - Gestion centralisée de la configuration
   - Validation des paramètres
   - Chargement depuis `.env`

2. **Utils Layer** (`src/utils/`)
   - Client HTTP réutilisable avec retry
   - Gestion des erreurs (7 exceptions)
   - Validation des entrées

3. **Services Layer** (`src/services/`)
   - `WeatherService` : API météo
   - `MarineService` : API marine
   - `CycloneDetector` : Algorithme de détection

## 📦 Installation

### Prérequis

- Python 3.12+
- pip (gestionnaire de packages)
- Git (optionnel)

### Étapes

1. **Cloner le projet** (ou télécharger les fichiers)

```bash
git clone <repo-url>
cd Brief2_Integration_API
```

2. **Créer un environnement virtuel**

```bash
python -m venv venv
```

3. **Activer l'environnement virtuel**

Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

5. **Configurer les variables d'environnement**

Copier `.env.example` vers `.env` :

```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Modifier `.env` si nécessaire (les valeurs par défaut fonctionnent).

## ⚙️ Configuration

Le fichier `.env` contient toutes les configurations :

### APIs
```bash
WEATHER_API_URL=https://api.open-meteo.com/v1/forecast
MARINE_API_URL=https://marine-api.open-meteo.com/v1/marine
```

### Réseau
```bash
TIMEOUT=10                  # Timeout en secondes
RETRY_COUNT=3               # Nombre de tentatives
RETRY_DELAY=2               # Délai initial entre tentatives
MAX_RETRY_DELAY=30          # Délai maximum
```

### Seuils de Détection Cyclonique
```bash
CYCLONE_SST_THRESHOLD=26.5        # Température surface mer (°C)
CYCLONE_PRESSURE_THRESHOLD=980.0  # Pression (hPa)
CYCLONE_WIND_THRESHOLD=117.0      # Vitesse vent (km/h)
```

### Logging
```bash
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## 🚀 Utilisation

### Application Démo

Lancer l'analyse pour 4 localisations de l'océan Indien :

```bash
python -m src.main
```

Sortie attendue :
```
==============================================================
ANALYSE CYCLONIQUE - La Réunion
==============================================================
Coordonnées: -21.1151, 55.5364
Date d'analyse: 2024-01-15

🌀 CATÉGORIE: Aucun
⚠️  Sévérité: 23.45%

📊 CONDITIONS MÉTÉOROLOGIQUES:
  ❌ Température de surface: 25.8°C (seuil: >26.5°C)
  ❌ Pression de surface: 1013.2 hPa (seuil: <980.0 hPa)
  ❌ Vitesse du vent: 45.3 km/h (seuil: >117.0 km/h)

🌡️  TEMPÉRATURES:
  Maximum: 30.5°C
  Minimum: 24.3°C
==============================================================
```

### Utilisation Programmatique

```python
from src.utils.api_client import APIClient
from src.services.weather_service import WeatherService
from src.services.cyclone_detector import CycloneDetector

# Initialiser les services
client = APIClient()
weather_service = WeatherService(client)
detector = CycloneDetector()

# Récupérer les données météo
weather_data = weather_service.get_forecast(
    latitude=-21.1151,
    longitude=55.5364,
    forecast_days=7
)

# Détecter les conditions cycloniques
result = detector.detect(weather_data=weather_data)

print(f"Catégorie: {result['category']}")
print(f"Sévérité: {result['severity_score']:.2%}")

# Fermer la connexion
client.close()
```

## 🧪 Tests

### Exécuter Tous les Tests

```bash
pytest
```

### Tests Unitaires Uniquement

```bash
pytest -m unit
```

### Tests d'Intégration (APIs réelles)

```bash
pytest -m integration
```

### Tests avec Couverture

```bash
pytest --cov=src --cov-report=html
```

Ouvrir `htmlcov/index.html` pour voir le rapport détaillé.

### Tests Spécifiques

```bash
# Tester WeatherService
pytest tests/test_weather_service.py

# Tester un test spécifique
pytest tests/test_cyclone_detector.py::TestCycloneDetectorDetect::test_detect_cyclone_conditions -v
```

### Statistiques des Tests

- **41 tests** au total
- **14 tests** : WeatherService
- **5 tests** : MarineService
- **10 tests** : CycloneDetector
- **7 tests** : Intégration
- **5 tests** : Fiabilité (marqués `slow`)

## 🌪️ Algorithme de Détection Cyclonique

### Critères (tous doivent être remplis pour "Cyclone")

1. **SST (Sea Surface Temperature)** > 26.5°C
2. **Pression** < 980 hPa
3. **Vent** > 117 km/h (65 nœuds)

### Classification

| Conditions Remplies | Sévérité | Catégorie |
|---------------------|----------|-----------|
| 3/3 | > 0.5 | 🔴 **Cyclone** |
| 2/3 | > 0.5 | 🟡 **Tempête Tropicale** |
| 1/3 | > 0.3 | 🟠 **Dépression Tropicale** |
| 0/3 | < 0.3 | 🟢 **Aucun** |

### Score de Sévérité (0-1)

```
severity = (sst_score + pressure_score + wind_score) / 3

où :
- sst_score = (SST - 26.5) / (30 - 26.5)
- pressure_score = (980 - Pressure) / (980 - 900)
- wind_score = (Wind - 117) / (250 - 117)
```

## 🛠️ Technologies

### Core
- **Python 3.12+** : Langage principal
- **requests 2.31.0** : Client HTTP
- **python-dotenv 1.0.0** : Gestion variables d'environnement

### Testing
- **pytest 9.0.1** : Framework de tests
- **pytest-cov 7.0.0** : Couverture de code
- **pytest-timeout 2.4.0** : Timeout des tests
- **pytest-mock 3.14.0** : Mocking

### Quality
- **black 24.4.2** : Formatage de code
- **flake8 7.0.0** : Linting
- **mypy 1.10.0** : Type checking

### Optional
- **redis 5.0.1** : Cache (non implémenté dans v1.0)

## 📊 APIs Utilisées

### 1. Open-Meteo Weather Forecast API

**Endpoint** : `https://api.open-meteo.com/v1/forecast`

**Paramètres** :
- `latitude`, `longitude` : Coordonnées
- `forecast_days` : 1-16 jours
- `daily` : Variables (temperature_2m_max, surface_pressure, wind_speed_10m_max)
- `timezone` : auto

**Exemple** :
```
GET https://api.open-meteo.com/v1/forecast?latitude=-21.1151&longitude=55.5364&daily=temperature_2m_max,temperature_2m_min,surface_pressure,wind_speed_10m_max&forecast_days=7&timezone=auto
```

### 2. Open-Meteo Marine Weather API

**Endpoint** : `https://marine-api.open-meteo.com/v1/marine`

**Paramètres** :
- `latitude`, `longitude` : Coordonnées
- `daily` : Variables (wave_height_max, wave_direction_dominant, ocean_current_velocity)
- `timezone` : auto

**Exemple** :
```
GET https://marine-api.open-meteo.com/v1/marine?latitude=-21.1151&longitude=55.5364&daily=wave_height_max,wave_direction_dominant,ocean_current_velocity,ocean_current_direction&timezone=auto
```

## 🤖 Utilisation de LLM

Ce projet a été développé avec l'assistance de GitHub Copilot et Claude 3.5 Sonnet.

### LLM Utilisés
- **GitHub Copilot** : Autocomplétion de code, suggestions de structure
- **Claude 3.5 Sonnet** : Architecture, documentation, tests

### Contributions du LLM

1. **Architecture** : Proposition de l'architecture 3-couches
2. **Code Generation** : Services, tests, gestion d'erreurs
3. **Documentation** : README, docstrings, diagrammes
4. **Tests** : Fixtures, tests paramétrés, mocking
5. **Best Practices** : Retry logic, validation, logging

### Prompts Clés (extrait)

```
"Créer un module Python pour intégrer l'API Open-Meteo avec détection 
cyclonique basée sur SST>26.5°C, Pression<980hPa, Vent>117km/h. 
Architecture modulaire avec tests pytest."

"Implémenter un HTTPClient avec retry logic, backoff exponentiel, 
gestion d'erreurs (429, timeout, connection), logging."

"Générer 41 tests pytest avec fixtures, mocking, tests d'intégration, 
couverture 60%+."
```

Voir `docs/prompts/` pour l'historique complet des 60+ prompts utilisés.

## 📚 Documentation Complète

- **Architecture** : `docs/SCHEMA_ARCHITECTURE.md` (6 diagrammes Mermaid)
- **Tests Postman** : `docs/CAPTURES_POSTMAN.md` (11 tests API)
- **Code Review** : `docs/REVUE_CODE_FINALE.md` (Score 8.6/10)
- **Validation** : `docs/VALIDATION_FINALE.md` (Certification Brief 2)
- **Prompts** : `docs/prompts/` (Historique détaillé par mission)

## 🔒 Sécurité

- ✅ Pas de credentials en dur (utilisation de `.env`)
- ✅ `.env` dans `.gitignore`
- ✅ Validation de toutes les entrées utilisateur
- ✅ Gestion des erreurs (pas de crash silencieux)
- ✅ Logging des opérations sensibles
- ✅ Timeout sur toutes les requêtes

## 🐛 Dépannage

### Erreur : `ModuleNotFoundError: No module named 'src'`

Solution :
```bash
# Exécuter depuis la racine du projet
python -m src.main

# Ou ajouter le projet au PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac
$env:PYTHONPATH="$env:PYTHONPATH;$(pwd)"  # Windows PowerShell
```

### Erreur : `TimeoutError: Request timeout`

Solution :
- Vérifier la connexion Internet
- Augmenter `TIMEOUT` dans `.env`
- Vérifier que les URLs d'API sont correctes

### Tests d'intégration échouent

Solution :
- Vérifier la disponibilité des APIs Open-Meteo
- Exécuter uniquement les tests unitaires : `pytest -m unit`
- Augmenter `TIMEOUT` et `RETRY_COUNT`

## 📄 Licence

MIT License - Voir le fichier LICENSE pour plus de détails.

## 👤 Auteur

**Projet Brief 2** - Formation Développeur IA
- Développé avec : Python 3.12, Open-Meteo APIs
- Assistance LLM : GitHub Copilot, Claude 3.5 Sonnet
- Date : Janvier 2025

## 🙏 Remerciements

- **Open-Meteo** : APIs météo et marines gratuites
- **GitHub Copilot** : Assistance au développement
- **Claude 3.5 Sonnet** : Architecture et documentation
- **Simplon** : Formation et encadrement

## 📈 Statistiques du Projet

- **Lignes de Code** : ~1800 (src/) + ~700 (tests/)
- **Lignes de Documentation** : ~2500+
- **Tests** : 41 tests (60%+ couverture)
- **Fichiers Python** : 15
- **Durée de Développement** : ~8 heures
- **LLM Prompts** : 60+
- **Score Code Review** : 8.6/10

## 🔮 Roadmap (v2.0)

- [ ] Async/await pour les appels API
- [ ] Cache Redis fonctionnel
- [ ] API GraphQL pour agrégation de données
- [ ] Dashboard web (Flask/FastAPI)
- [ ] Notifications en temps réel
- [ ] Modèle ML pour prédiction avancée
- [ ] Support multi-régions (Pacifique, Atlantique)
- [ ] Export PDF des rapports
- [ ] CI/CD avec GitHub Actions
- [ ] Docker containerization

---

**⚡ Quick Start**

```bash
# Installation
git clone <repo-url>
cd Brief2_Integration_API
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
copy .env.example .env

# Exécution
python -m src.main

# Tests
pytest
```

---

Pour toute question ou problème, ouvrir une issue sur GitHub ou contacter l'équipe pédagogique.
