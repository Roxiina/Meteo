# Mission 5 - Prompts pour la Documentation

## 📋 Contexte

**Date** : 28 novembre 2025  
**Durée** : 45 min  
**Objectif** : Créer une documentation complète permettant à un autre développeur de reprendre le projet

---

## 📝 Prompt Principal - README Complet

```
Génère un README.md professionnel et complet pour le projet Cyclone Tracker.

Structure attendue :

# 🌀 Cyclone Tracker - Brief 2

## 📋 Description
Système de détection automatique de cyclones tropicaux utilisant l'API Open-Meteo.
Analyse les données météorologiques et marines pour identifier les formations cycloniques
dans l'Océan Indien (Réunion, Maurice, Madagascar, Comores).

## 🎯 Fonctionnalités
- ✅ Récupération données météo (vent, pression) via Weather Forecast API
- ✅ Récupération données marines (SST, vagues) via Marine Weather API
- ✅ Algorithme de détection cyclonique multi-critères
- ✅ Classification : CYCLONE / TEMPÊTE / DÉPRESSION / NORMAL
- ✅ Évaluation du risque : ÉLEVÉ / MODÉRÉ / FAIBLE
- ✅ Gestion d'erreurs robuste avec retry automatique
- ✅ Cache Redis optionnel (TTL 6h)
- ✅ Logging professionnel (fichier + console)
- ✅ Configuration via .env
- ✅ Tests unitaires et d'intégration (60% coverage)

## 🏗️ Architecture
```
Brief2_Integration_API/
├── src/
│   ├── config/          # Configuration (settings.py)
│   ├── services/        # Services métier (Weather, Marine, Cyclone)
│   ├── utils/           # Utilitaires (APIClient, ErrorHandler)
│   └── main.py          # Point d'entrée
├── tests/               # Tests pytest
├── docs/                # Documentation technique
├── logs/                # Fichiers de logs
└── .env                 # Configuration (créer depuis .env.example)
```

## 🚀 Installation

### Prérequis
- Python 3.12+
- pip

### Étapes
```bash
# Cloner le projet
git clone [URL]
cd Brief2_Integration_API

# Créer environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Installer dépendances
pip install -r requirements.txt

# Configurer .env
cp .env.example .env
# Éditer .env si nécessaire
```

## ⚙️ Configuration

Créer fichier `.env` avec :
```bash
# API URLs (ne pas modifier)
WEATHER_API_URL=https://api.open-meteo.com/v1/forecast
MARINE_API_URL=https://marine-api.open-meteo.com/v1/marine

# Network
TIMEOUT=10
RETRY_COUNT=3

# Cyclone Thresholds
CYCLONE_SST_THRESHOLD=26.5
CYCLONE_PRESSURE_THRESHOLD=980
CYCLONE_WIND_THRESHOLD=117

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/cyclone_tracker.log
```

## 📖 Utilisation

### Exemple de base
```python
from config.settings import Settings
from utils.api_client import APIClient
from services.weather_service import WeatherService
from services.marine_service import MarineService
from services.cyclone_detector import CycloneDetector

# Initialisation
settings = Settings()
api_client = APIClient()
weather_service = WeatherService(api_client)
marine_service = MarineService(api_client)
detector = CycloneDetector(weather_service, marine_service)

# Détection cyclone à La Réunion
result = detector.detect(
    latitude=-21.1,
    longitude=55.5,
    hours_to_analyze=48
)

print(f"Cyclone détecté : {result['cyclone_detected']}")
print(f"Catégorie : {result['category']}")
print(f"Risque : {result['risk_level']}")
```

### Lancer l'application de démo
```bash
python src/main.py
```

## 🧪 Tests

### Tests unitaires (rapides)
```bash
pytest tests/ -v -m "not integration"
```

### Tests d'intégration (requêtes API réelles)
```bash
pytest tests/ -v -m integration
```

### Coverage
```bash
pytest tests/ --cov=src --cov-report=html
# Ouvrir htmlcov/index.html
```

## 📊 Algorithme de Détection

### Critères Cyclone (Risque ÉLEVÉ)
- SST > 26.5°C **ET**
- Pression < 980 hPa **ET**
- Vent > 117 km/h

### Critères Tempête (Risque MODÉRÉ)
- SST > 26.5°C **ET**
- Pression < 995 hPa **ET**
- Vent > 88 km/h

### Critères Dépression (Risque MODÉRÉ)
- SST > 26.5°C **ET**
- Pression < 1000 hPa **ET**
- Vent > 62 km/h

## 🛠️ Technologies
- **Python** : 3.12
- **Requests** : HTTP client
- **python-dotenv** : Configuration
- **Pytest** : Tests
- **Redis** : Cache (optionnel)

## 📚 Documentation
- [API Open-Meteo](https://open-meteo.com/en/docs)
- [Schémas d'architecture](docs/SCHEMA_ARCHITECTURE.md)
- [Captures Postman](docs/CAPTURES_POSTMAN.md)
- [Historique prompts](docs/prompts/)

## 👨‍💻 Développement avec LLM

Ce projet a été développé avec l'assistance d'un LLM (Claude Sonnet 4.5).

### Approche utilisée :
1. **Génération guidée** : Prompts détaillés avec contraintes techniques
2. **Itérations contrôlées** : Validation humaine à chaque étape
3. **Tests systématiques** : Vérification après chaque génération
4. **Documentation prompts** : Historique complet dans docs/prompts/

### Avantages :
- ✅ Architecture propre dès le début
- ✅ Gestion d'erreurs exhaustive
- ✅ Tests générés automatiquement
- ✅ Documentation à jour

### Vigilance requise :
- ⚠️ Validation des imports Python (absolu vs relatif)
- ⚠️ Vérification logique métier (algorithme cyclone)
- ⚠️ Tests avec données réelles (pas seulement mocks)

## 📄 Licence
MIT

## 👤 Auteur
[Votre nom] - Brief 2 Simplon

Génère ce README complet avec tous les badges, liens et exemples de code.
```

**Résultat** : `README.md` (300+ lignes)

---

## 📐 Prompt - Schémas Mermaid

```
Génère des diagrammes Mermaid pour documenter l'architecture du projet.

Fichier : docs/SCHEMA_ARCHITECTURE.md

Diagrammes à créer :

1. Architecture globale (graph TB)
   - Clients (User, CLI)
   - Application Layer (Main, Services, Utils, Config)
   - External APIs (Open-Meteo Weather, Marine)
   - Storage (Redis, Logs)
   - Connexions entre composants

2. Séquence de détection cyclone (sequenceDiagram)
   - User → Main → Detector
   - Detector → WeatherService → APIClient → OpenMeteo
   - Detector → MarineService → APIClient → OpenMeteo
   - Detector → Analyse → Return Result

3. Algorithme de détection (flowchart TD)
   - Début → Récupération données
   - Pour chaque heure → Extraire conditions
   - SST > 26.5 ? → Oui/Non
   - Pression < 980 ? → CYCLONE
   - Pression < 995 ? → TEMPÊTE
   - Pression < 1000 ? → DÉPRESSION
   - Sinon → NORMAL
   - Sélectionner le plus sévère → Retour

4. Modèle de données (erDiagram)
   - DETECTION (cyclone_detected, category, risk, conditions)
   - CONDITIONS (time, wind, pressure, sst)
   - WEATHER_DATA (hourly arrays)
   - MARINE_DATA (hourly arrays)
   - Relations entre entités

5. Architecture des tests (graph TB)
   - conftest.py → Fixtures
   - test_weather_service.py → Tests unitaires
   - test_integration.py → Tests e2e
   - Coverage Report

6. Pipeline de traitement (flowchart LR)
   - Input → Validation → API Calls (parallel)
   - Cache check → API ou Cache
   - Parse → Analyze → Classify
   - Log → Output

Pour chaque diagramme :
- Style nodes avec couleurs appropriées
- Labels descriptifs en français
- Légende si nécessaire

Génère docs/SCHEMA_ARCHITECTURE.md avec tous les diagrammes.
```

**Résultat** : `docs/SCHEMA_ARCHITECTURE.md` avec 6 diagrammes Mermaid

---

## 🔌 Prompt - Documentation Postman

```
Génère documentation pour les tests API Postman/Thunder Client.

Fichier : docs/CAPTURES_POSTMAN.md

Contenu attendu :

## Collection Postman - Brief 2

### Tests inclus (11 requêtes)

1. **Weather Forecast - Basique**
   - Endpoint : GET https://api.open-meteo.com/v1/forecast
   - Paramètres : latitude, longitude, hourly, timezone
   - Résultat attendu : 200 OK, JSON avec hourly data
   - Capture : [Screenshot placeholder]

2. **Weather - Variables Cycloniques**
   - Variables : wind_speed_10m, wind_gusts_10m, pressure_msl
   - forecast_days=7
   - Vérifier 168 timestamps (7j × 24h)

3. **Marine - SST**
   - Endpoint : GET https://marine-api.open-meteo.com/v1/marine
   - Variable : sea_surface_temperature
   - Vérifier SST > 26.5°C pour Réunion

4. **Test Endpoint Cyclone (404 attendu)**
   - Vérifier qu'il n'existe pas d'endpoint dédié cyclones
   - Justifie l'algorithme custom

5. **Ensemble API - Prévisions Probabilistes**
   - Endpoint : ensemble-api.open-meteo.com
   - Modèle : icon_seamless

6. **Test Paramètres Invalides (400)**
   - latitude=999, longitude=999
   - Vérifier message d'erreur API

7. **Test Performance**
   - 10 appels successifs
   - Mesurer temps moyen
   - Objectif : <1s par appel

8. **Test Cache Headers**
   - Vérifier Cache-Control
   - TTL API vs notre cache

9. **Test Forecast 10 jours**
   - forecast_days=10
   - Vérifier 240 timestamps

10. **Test Timezone**
    - timezone=auto vs UTC
    - Vérifier offset correct

11. **Test Rate Limit**
    - Vérifier headers X-RateLimit-*
    - Limite 10k/jour

### Collection JSON (import Postman)
```json
{
  "info": {"name": "Brief2 - Cyclone Tracker API"},
  "item": [
    {
      "name": "1. Weather Forecast",
      "request": {
        "method": "GET",
        "url": {
          "raw": "https://api.open-meteo.com/v1/forecast?latitude=-21.1&longitude=55.5&hourly=temperature_2m&timezone=auto"
        }
      }
    }
  ]
}
```

### Résumé des tests
| Test | Statut | Temps | Notes |
|------|--------|-------|-------|
| 1. Basique | ✅ | 1.12s | OK |
| 2. Cycloniques | ✅ | 0.89s | 7 jours |
...

Génère documentation Postman complète avec exemples cURL et réponses JSON.
```

**Résultat** : `docs/CAPTURES_POSTMAN.md` avec 11 tests documentés

---

## 📚 Prompt - Historique Prompts

```
Documente l'historique complet des prompts utilisés avec le LLM.

Fichier : docs/HISTORIQUE_PROMPTS.md

Structure :

# Historique des Prompts LLM - Brief 2

## 📊 Vue d'ensemble

**Total prompts** : ~50
**Phases** : 6 missions
**LLM utilisé** : Claude Sonnet 4.5
**Durée totale** : 6h

## 🎯 Stratégie Globale

### Approche itérative
1. Prompt initial → Génération code
2. Validation humaine → Identification problèmes
3. Prompt de correction → Amélioration
4. Tests → Validation

### Principes appliqués
- **Contraintes explicites** : Architecture imposée
- **Exemples concrets** : Réponses API réelles
- **Validation progressive** : Couche par couche
- **Documentation synchrone** : Prompts conservés

## 📁 Prompts par Mission

### Mission 1 - Squelette (10 prompts)
Voir docs/prompts/squelette.md

Prompts clés :
- Génération architecture modulaire
- Correction imports relatifs
- Création dossiers automatique
- Validation configuration

### Mission 2 - Appels API (15 prompts)
Voir docs/prompts/appels_api.md

Prompts clés :
- WeatherService avec validation
- MarineService avec limite 7 jours
- APIClient avec retry exponential
- CycloneDetector avec algorithme décisionnel

### Mission 3 - Refactorisation (10 prompts)
Voir docs/prompts/refacto.md

Prompts clés :
- Timeout configurable
- Sécurisation .env
- Logging multi-niveaux
- Refactorisation DRY

### Mission 4 - Tests (12 prompts)
Voir docs/prompts/tests.md

Prompts clés :
- Structure tests pytest
- Tests unitaires avec mocks
- Tests d'intégration avec vraies APIs
- Coverage >80%

### Mission 5 - Documentation (5 prompts)
Voir docs/prompts/documentation.md

Prompts clés :
- README complet
- Schémas Mermaid
- Documentation Postman
- Historique prompts (meta)

### Mission 6 - Debug (8 prompts)
Voir docs/prompts/debug.md

Prompts clés :
- Correction ModuleNotFoundError
- Gestion valeurs null
- Optimisation performance
- Validation finale

## 🎓 Leçons Apprises

### ✅ Prompts Efficaces

1. **Prompt avec structure** :
   ❌ "Crée un service météo"
   ✅ "Génère une classe WeatherService avec :
       - Méthode get_forecast(lat, lon, days)
       - Validation coordonnées (-90 à 90, -180 à 180)
       - Gestion erreurs 400/429/500
       - Parsing JSON avec gestion null
       - Docstrings et type hints"

2. **Prompt avec exemples** :
   ```
   Réponse API attendue :
   {
     "hourly": {
       "time": ["2025-11-28T00:00"],
       "wind_speed_10m": [15.2]
     }
   }
   Génère parsing qui extrait ces données.
   ```

3. **Prompt avec contraintes** :
   ```
   Contraintes obligatoires :
   - DOIT utiliser imports relatifs (from .config import)
   - DOIT créer dossiers manquants
   - DOIT logger tous les appels API
   - NE DOIT PAS hardcoder timeouts
   ```

### ⚠️ Prompts à Éviter

1. **Prompts vagues** :
   ❌ "Améliore le code"
   ✅ "Extrait validation coordonnées dans validators.py pour éviter duplication"

2. **Prompts sans contexte** :
   ❌ "Corrige l'erreur"
   ✅ "L'erreur ModuleNotFoundError sur 'src' vient des imports absolus. Change vers imports relatifs."

3. **Prompts trop larges** :
   ❌ "Génère tout le projet"
   ✅ "Génère d'abord l'architecture (dossiers + __init__.py), je validerai avant de générer le code"

## 🔄 Exemples de Corrections

### Correction 1 - Imports
**Problème** : ModuleNotFoundError: No module named 'src'

**Prompt initial** (raté) :
"Crée un projet Python avec imports standards"

**Prompt de correction** (réussi) :
```
Le module échoue avec ModuleNotFoundError sur 'src'.

Structure actuelle :
Brief2_Integration_API/
  src/
    config/settings.py (from src.config import ...)

Problème : Python ne trouve pas 'src' en import absolu.

Solution demandée :
- Changer vers imports relatifs (from .config import, from ..utils import)
- Ajouter sys.path.insert dans main.py si nécessaire
- Vérifier __init__.py dans chaque package

Génère les corrections pour settings.py, weather_service.py, marine_service.py.
```

### Correction 2 - Valeurs Null
**Problème** : Crash sur null dans arrays JSON

**Prompt de correction** :
```
L'API retourne parfois null dans les arrays hourly :
{
  "hourly": {
    "wind_speed_10m": [15.2, null, 18.3]
  }
}

Améliore le parsing pour :
1. Détecter null avec `value is None`
2. Logger warning avec timestamp concerné
3. Skip cette heure dans l'analyse
4. Ne pas crasher

Génère code robuste dans _parse_response().
```

## 📈 Métriques d'Efficacité

### Prompts par catégorie
- Architecture : 20%
- Implémentation : 35%
- Corrections : 25%
- Tests : 15%
- Documentation : 5%

### Taux de succès
- Première génération OK : 40%
- Correction 1 nécessaire : 45%
- Corrections 2+ : 15%

### Temps gagné vs manuel
- Génération code : 70% gain
- Tests : 60% gain
- Documentation : 50% gain
- Debug : 20% gain (validation nécessaire)

## 🎯 Best Practices

1. **Toujours** :
   - Contraintes techniques explicites
   - Exemples de données réelles
   - Validation humaine systématique

2. **Jamais** :
   - Accepter code sans le lire
   - Générer toutes les missions d'un coup
   - Oublier de documenter les prompts

3. **Recommandations** :
   - 1 prompt = 1 tâche spécifique
   - Valider avant de continuer
   - Conserver historique des échecs

Génère documentation complète de l'utilisation du LLM dans le projet.
```

**Résultat** : `docs/HISTORIQUE_PROMPTS.md` (méta-documentation)

---

## ⏱️ Temps Passé

- **README.md** : 15 min
- **SCHEMA_ARCHITECTURE.md** : 15 min (6 diagrammes)
- **CAPTURES_POSTMAN.md** : 10 min
- **HISTORIQUE_PROMPTS.md** : 15 min
- **Relecture et corrections** : 10 min

**Total Mission 5** : 1h05 ✅ (20min overtime pour qualité)

---

## 🔗 Fichiers Générés

- `README.md` (300+ lignes)
- `docs/SCHEMA_ARCHITECTURE.md` (6 diagrammes Mermaid)
- `docs/CAPTURES_POSTMAN.md` (11 tests API)
- `docs/HISTORIQUE_PROMPTS.md` (méta)
- `docs/prompts/squelette.md`
- `docs/prompts/appels_api.md`
- `docs/prompts/refacto.md`
- `docs/prompts/tests.md`
- `docs/prompts/documentation.md` (ce fichier)
