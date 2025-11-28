# Mission 3 - Prompts pour la Refactorisation et Sécurisation

## 📋 Contexte

**Date** : 28 novembre 2025  
**Durée** : 1h  
**Objectif** : Professionnaliser le module avec sécurité, robustesse et maintenabilité

---

## 🔒 Prompt 1 - Timeout Configurable

```
Ajoute un système de timeout configurable dans l'APIClient.

Problème actuel : Timeout hardcodé à 10 secondes.

Amélioration demandée :
1. Dans settings.py :
   - Ajouter TIMEOUT = int(os.getenv("TIMEOUT", "10"))
   - Ajouter MAX_TIMEOUT = int(os.getenv("MAX_TIMEOUT", "30"))
   - Valider TIMEOUT > 0 et < MAX_TIMEOUT

2. Dans APIClient :
   - Paramètre timeout dans __init__(timeout=None)
   - Si None, utiliser settings.TIMEOUT
   - Permettre override par appel : get(endpoint, params, timeout=15)

3. Dans tests :
   - Test avec timeout court (0.1s) → TimeoutError
   - Test avec timeout long (30s) → Success
   - Marquer test timeout comme @pytest.mark.slow

4. Logging :
   - Logger warning si timeout > 20s (trop long)
   - Logger info du timeout utilisé pour chaque requête

Génère le code complet avec validation.
```

**Résultat** : Timeout configurable + validation

---

## 🔐 Prompt 2 - Sécurisation .env

```
Sécurise les variables sensibles dans .env et améliore la gestion de configuration.

Améliorations requises :

1. .env.example complet :
   # === API Configuration ===
   WEATHER_API_URL=https://api.open-meteo.com/v1/forecast
   MARINE_API_URL=https://marine-api.open-meteo.com/v1/marine
   
   # === Network Settings ===
   TIMEOUT=10
   RETRY_COUNT=3
   RETRY_DELAY=2
   MAX_RETRY_DELAY=60
   
   # === Cache Configuration (Optional) ===
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_PASSWORD=
   CACHE_TTL=21600
   CACHE_ENABLED=false
   
   # === Cyclone Detection Thresholds ===
   CYCLONE_SST_THRESHOLD=26.5
   CYCLONE_PRESSURE_THRESHOLD=980
   CYCLONE_WIND_THRESHOLD=117
   STORM_PRESSURE_THRESHOLD=995
   STORM_WIND_THRESHOLD=88
   DEPRESSION_PRESSURE_THRESHOLD=1000
   DEPRESSION_WIND_THRESHOLD=62
   
   # === Logging ===
   LOG_LEVEL=INFO
   LOG_FILE=logs/cyclone_tracker.log
   LOG_MAX_SIZE=10485760
   LOG_BACKUP_COUNT=5

2. Dans settings.py :
   - Valider que .env existe (optionnel mais recommandé)
   - Ne JAMAIS logger les passwords/tokens
   - Méthode display() qui masque valeurs sensibles
   - Exemple : "REDIS_PASSWORD=****" au lieu de la vraie valeur

3. .gitignore :
   # Environment
   .env
   .env.local
   .env.*.local
   
   # Logs
   logs/
   *.log
   
   # Cache
   __pycache__/
   *.pyc
   .pytest_cache/
   
   # Coverage
   htmlcov/
   .coverage
   
   # IDE
   .vscode/
   .idea/

4. Documentation README :
   - Section "Configuration" détaillée
   - Copier .env.example vers .env
   - Expliquer chaque variable
   - Valeurs par défaut sensibles

Génère .env.example complet et améliore settings.py.
```

**Résultat** : Configuration sécurisée avec 40+ variables

---

## 📝 Prompt 3 - Logging Professionnel

```
Implémente un système de logging professionnel multi-niveaux.

Spécifications :

1. Configuration centralisée dans src/__init__.py :
   import logging
   import sys
   from pathlib import Path
   
   def setup_logging():
       log_file = Path(settings.LOG_FILE)
       log_file.parent.mkdir(parents=True, exist_ok=True)
       
       logging.basicConfig(
           level=getattr(logging, settings.LOG_LEVEL),
           format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
           handlers=[
               logging.FileHandler(log_file),
               logging.StreamHandler(sys.stdout)
           ]
       )

2. Par module :
   # api_client.py
   logger = logging.getLogger(__name__)
   
   # Avant appel API
   logger.info(f"Calling {endpoint} with params: {params}")
   
   # Succès
   logger.info(f"API call successful (status: 200, time: {elapsed:.2f}s)")
   
   # Erreur
   logger.error(f"API call failed: {e}", exc_info=True)

3. Niveaux de log à utiliser :
   - DEBUG : Données brutes, détails techniques
   - INFO : Appels API, détections, métriques
   - WARNING : Valeurs manquantes, timeout proche, cache miss
   - ERROR : Échecs API, validations échouées
   - CRITICAL : Config invalide, services indisponibles

4. Rotation des logs :
   from logging.handlers import RotatingFileHandler
   
   handler = RotatingFileHandler(
       settings.LOG_FILE,
       maxBytes=settings.LOG_MAX_SIZE,  # 10MB
       backupCount=settings.LOG_BACKUP_COUNT  # 5 fichiers
   )

5. Logs structurés (optionnel) :
   logger.info("cyclone_detected", extra={
       "latitude": -21.1,
       "longitude": 55.5,
       "category": "CYCLONE",
       "risk": "ÉLEVÉ"
   })

Génère le code de logging complet et ajoute logs dans tous les modules.
```

**Résultat** : Logging multi-niveaux dans tous les modules

---

## ♻️ Prompt 4 - Refactorisation DRY

```
Refactorise le code pour éliminer les duplications (DRY principle).

Duplications identifiées :

1. Validation coordonnées (dupliquée dans Weather et Marine) :
   # Créer dans utils/validators.py
   def validate_coordinates(latitude: float, longitude: float) -> None:
       if not isinstance(latitude, (int, float)):
           raise ValidationError(f"Latitude must be a number, got {type(latitude)}")
       if not isinstance(longitude, (int, float)):
           raise ValidationError(f"Longitude must be a number, got {type(longitude)}")
       if not -90 <= latitude <= 90:
           raise ValidationError(f"Latitude must be between -90 and 90, got {latitude}")
       if not -180 <= longitude <= 180:
           raise ValidationError(f"Longitude must be between -180 and 180, got {longitude}")
   
   # Utiliser dans services
   from ..utils.validators import validate_coordinates
   validate_coordinates(latitude, longitude)

2. Parsing réponse (similaire Weather et Marine) :
   # Classe abstraite BaseService
   class BaseService:
       def __init__(self, api_client, base_url):
           self.api_client = api_client
           self.base_url = base_url
       
       def _parse_hourly_data(self, response, variables):
           # Logique commune de parsing
           pass
   
   # Weather et Marine héritent
   class WeatherService(BaseService):
       def __init__(self, api_client):
           super().__init__(api_client, settings.WEATHER_API_URL)

3. Gestion erreurs HTTP (dupliquée) :
   # Déplacer dans api_client.py
   def _handle_http_error(self, response):
       if response.status_code == 400:
           raise ValidationError(response.json().get("reason"))
       elif response.status_code == 429:
           raise RateLimitError("Rate limit exceeded")
       # ...

4. Construction URL (similaire) :
   # Méthode utilitaire dans api_client.py
   def _build_url(self, endpoint, params):
       query_string = "&".join(f"{k}={v}" for k, v in params.items())
       return f"{endpoint}?{query_string}"

Règles de refactorisation :
- Si code copié >2 fois → extraire fonction
- Si logique commune entre classes → classe de base ou mixin
- Si validation similaire → validators.py
- Ne PAS sur-abstraire (garder lisibilité)

Génère le code refactorisé avec validators.py et BaseService.
```

**Résultat** : Code DRY avec validators.py

---

## 🛡️ Prompt 5 - Gestion Erreurs Robuste

```
Améliore la gestion des erreurs pour couvrir tous les cas edge.

Cas à gérer :

1. Network errors :
   try:
       response = self.session.get(url, timeout=timeout)
   except requests.ConnectionError as e:
       logger.error(f"Connection failed: {e}")
       raise APIError(f"Cannot connect to {url}")
   except requests.Timeout as e:
       logger.error(f"Request timeout after {timeout}s")
       raise TimeoutError(f"Request timeout after {timeout}s")

2. JSON parsing errors :
   try:
       data = response.json()
   except json.JSONDecodeError as e:
       logger.error(f"Invalid JSON response: {response.text[:200]}")
       raise APIError("Invalid API response format")

3. Missing data :
   if "hourly" not in data:
       raise DataNotFoundError("No hourly data in response")
   
   if not data["hourly"].get("wind_speed_10m"):
       raise DataNotFoundError("Missing wind_speed_10m data")

4. Retry exhausted :
   for attempt in range(self.retry_count):
       try:
           return self._make_request(url, params, timeout)
       except (APIError, TimeoutError) as e:
           if attempt == self.retry_count - 1:
               logger.error(f"All {self.retry_count} attempts failed")
               raise
           logger.warning(f"Attempt {attempt + 1} failed, retrying...")

5. Graceful degradation :
   # Si Marine API échoue, continuer avec Weather seulement
   try:
       marine_data = self.marine_service.get_marine_forecast(lat, lon)
   except APIError as e:
       logger.warning(f"Marine API failed, using default SST: {e}")
       marine_data = {"sst": 27.0}  # Valeur par défaut Océan Indien

6. Context dans exceptions :
   raise ValidationError(
       f"Invalid coordinates for location '{location_name}': "
       f"lat={latitude}, lon={longitude}"
   )

Génère le code de gestion d'erreurs complète.
```

**Résultat** : Gestion erreurs exhaustive avec retry

---

## 🎨 Prompt 6 - Code Quality (Black, Flake8, Mypy)

```
Ajoute les outils de qualité de code au projet.

1. Ajout requirements :
   # Code quality
   black==24.4.2
   flake8==7.0.0
   mypy==1.10.0

2. Configuration Black (.black.toml ou pyproject.toml) :
   [tool.black]
   line-length = 100
   target-version = ['py312']
   include = '\.pyi?$'
   exclude = '''
   /(
       \.git
     | \.venv
     | build
     | dist
   )/
   '''

3. Configuration Flake8 (.flake8) :
   [flake8]
   max-line-length = 100
   extend-ignore = E203, W503
   exclude = .git,__pycache__,.venv

4. Configuration Mypy (pyproject.toml) :
   [tool.mypy]
   python_version = "3.12"
   warn_return_any = true
   warn_unused_configs = true
   disallow_untyped_defs = true

5. Scripts dans README :
   # Format code
   black src/ tests/
   
   # Check style
   flake8 src/ tests/
   
   # Type checking
   mypy src/

6. Pre-commit hooks (optionnel) :
   # .pre-commit-config.yaml
   repos:
     - repo: https://github.com/psf/black
       rev: 24.4.2
       hooks:
         - id: black
     - repo: https://github.com/pycqa/flake8
       rev: 7.0.0
       hooks:
         - id: flake8

Exécute black et corrige les type hints manquants.
```

**Résultat** : Code formaté + type hints complets

---

## 📊 Validation Avant/Après

### Avant Refactorisation

```python
# Duplication validation (weather_service.py)
if not -90 <= latitude <= 90:
    raise ValidationError(...)

# Duplication validation (marine_service.py)
if not -90 <= latitude <= 90:
    raise ValidationError(...)

# Timeout hardcodé
response = requests.get(url, timeout=10)

# Pas de logs
# Pas de gestion ConnectionError
# Type hints manquants
```

**Problèmes** :
- 🔴 Code dupliqué (DRY violé)
- 🔴 Configuration rigide
- 🔴 Peu d'observabilité
- 🔴 Gestion erreurs incomplète

---

### Après Refactorisation

```python
# Validation centralisée
from ..utils.validators import validate_coordinates
validate_coordinates(latitude, longitude)

# Timeout configurable
timeout = timeout or self.settings.TIMEOUT
response = self.session.get(url, timeout=timeout)

# Logging complet
logger.info(f"API call to {endpoint}")
logger.info(f"Success in {elapsed:.2f}s")

# Gestion erreurs complète
except requests.ConnectionError:
    raise APIError("Connection failed")
except requests.Timeout:
    raise TimeoutError(f"Timeout after {timeout}s")

# Type hints
def get_forecast(
    self,
    latitude: float,
    longitude: float,
    forecast_days: int = 7
) -> Dict[str, Any]:
```

**Améliorations** :
- ✅ DRY respecté (validators.py)
- ✅ Configuration flexible (.env)
- ✅ Logging professionnel (INFO/ERROR)
- ✅ Gestion erreurs exhaustive
- ✅ Type hints complets
- ✅ Code formaté (Black)

---

## 🎓 Leçons Apprises

### ✅ Bonnes Pratiques

1. **Configuration externalisée** :
   - Tout dans .env (jamais hardcodé)
   - Valeurs par défaut sensées
   - Validation au démarrage

2. **Logging stratégique** :
   - INFO pour flux normal
   - WARNING pour anomalies récupérables
   - ERROR pour échecs
   - Rotation pour éviter saturation disque

3. **Validation centralisée** :
   - validators.py réutilisable
   - Messages d'erreur clairs
   - Validation au plus tôt

4. **Refactorisation prudente** :
   - Extraire duplication >2 occurrences
   - Garder lisibilité
   - Tests avant/après

### ⚠️ Pièges Évités

1. **Sur-abstraction** :
   - Pas de classe abstraite si seulement 2 enfants
   - Privilégier composition sur héritage

2. **Configuration complexe** :
   - .env simple (key=value)
   - Pas de nested config au début

3. **Logging excessif** :
   - Pas de DEBUG en production
   - Rotation obligatoire
   - Ne jamais logger passwords

---

## ⏱️ Temps Passé

- **Timeout configurable** : 10 min
- **Sécurisation .env** : 15 min
- **Logging professionnel** : 15 min
- **Refactorisation DRY** : 20 min
- **Gestion erreurs** : 15 min
- **Code quality tools** : 10 min

**Total Mission 3** : 1h25 ✅

---

## 🔗 Fichiers Modifiés

- `src/config/settings.py` (validation + display)
- `src/utils/api_client.py` (timeout + retry)
- `src/utils/validators.py` (NOUVEAU)
- `.env.example` (40+ variables)
- `.gitignore` (sécurité)
- `requirements.txt` (black, flake8, mypy)
