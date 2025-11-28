# Mission 6 - Prompts pour le Débogage et Revue de Code

## 📋 Contexte

**Date** : 28 novembre 2025  
**Durée** : 45 min  
**Objectif** : Finaliser un code propre, débogué et validé par revue de code

---

## 🐛 Prompt 1 - Debug ModuleNotFoundError

### Problème Rencontré

```bash
PS> python src/main.py
Traceback (most recent call last):
  File "C:\...\Brief2_Integration_API\src\main.py", line 3, in <module>
    from src.config.settings import Settings
ModuleNotFoundError: No module named 'src'
```

### Prompt de Debug

```
Erreur lors de l'exécution de main.py :

ModuleNotFoundError: No module named 'src'

Structure du projet :
Brief2_Integration_API/
  src/
    config/
      __init__.py
      settings.py
    main.py

Imports actuels dans main.py :
from src.config.settings import Settings
from src.utils.api_client import APIClient
from src.services.weather_service import WeatherService

Analyse le problème et propose 2 solutions :
1. Solution avec imports relatifs (préférée pour modules)
2. Solution avec sys.path.insert (alternative)

Pour chaque solution :
- Explique pourquoi ça fonctionne
- Donne le code exact à utiliser
- Liste les fichiers à modifier

Contexte : Python 3.12, Windows, exécution depuis racine du projet.
```

### Solution Appliquée

**Changement vers imports relatifs** :

```python
# main.py - AVANT
from src.config.settings import Settings
from src.utils.api_client import APIClient

# main.py - APRÈS
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import Settings
from utils.api_client import APIClient
```

**Résultat** : ✅ Application démarre correctement

---

## 🐛 Prompt 2 - Debug FileNotFoundError

### Problème Rencontré

```bash
FileNotFoundError: [Errno 2] No such file or directory: 'logs/cyclone_tracker.log'
```

### Prompt de Debug

```
Erreur au démarrage de l'application :

FileNotFoundError: logs/cyclone_tracker.log

Le dossier logs/ n'existe pas au premier lancement.

Améliore le code pour :
1. Créer automatiquement les dossiers manquants au démarrage
2. Utiliser pathlib.Path pour portabilité (Windows/Linux)
3. Créer aussi docs/, postman/ si manquants

Code actuel qui échoue :
```python
logging.basicConfig(
    filename=settings.LOG_FILE,  # logs/cyclone_tracker.log
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Génère le code de création automatique à ajouter AVANT logging.basicConfig().

Contrainte : Ne pas crasher si dossiers existent déjà (exist_ok=True).
```

### Solution Appliquée

```python
# Ajout dans main.py avant logging.basicConfig()
from pathlib import Path

log_file = Path(settings.LOG_FILE)
log_file.parent.mkdir(parents=True, exist_ok=True)

# Créer autres dossiers
Path("docs/prompts").mkdir(parents=True, exist_ok=True)
Path("postman").mkdir(parents=True, exist_ok=True)
```

**Résultat** : ✅ Dossiers créés automatiquement

---

## 🐛 Prompt 3 - Debug AttributeError (Config Display)

### Problème Rencontré

```python
AttributeError: 'bool' object has no attribute 'items'
```

### Prompt de Debug

```
Erreur dans settings.display() :

AttributeError: 'bool' object has no attribute 'items'

Code actuel :
```python
def display(self):
    for key, value in vars(self).items():
        print(f"{key}={value}")
```

Problème : Certaines variables sont bool, float, int (pas dict).

Améliore display() pour :
1. Gérer tous types de variables (bool, int, float, str, dict)
2. Masquer valeurs sensibles (passwords) : afficher "****"
3. Formater joliment (aligned, grouped)

Exemple attendu :
```
=== API Configuration ===
WEATHER_API_URL=https://api.open-meteo.com/v1/forecast
MARINE_API_URL=https://marine-api.open-meteo.com/v1/marine

=== Network Settings ===
TIMEOUT=10
RETRY_COUNT=3

=== Cache ===
REDIS_PASSWORD=****
CACHE_ENABLED=False
```

Génère code de display() amélioré avec groupement par catégorie.
```

### Solution Appliquée

```python
def display(self):
    config_groups = {
        "API Configuration": ["WEATHER_API_URL", "MARINE_API_URL"],
        "Network Settings": ["TIMEOUT", "RETRY_COUNT", "RETRY_DELAY"],
        "Cache": ["REDIS_HOST", "REDIS_PASSWORD", "CACHE_ENABLED"],
        "Cyclone Thresholds": ["CYCLONE_SST_THRESHOLD", "CYCLONE_PRESSURE_THRESHOLD"],
        "Logging": ["LOG_LEVEL", "LOG_FILE"]
    }
    
    for group_name, keys in config_groups.items():
        print(f"\n=== {group_name} ===")
        for key in keys:
            value = getattr(self, key, None)
            if "PASSWORD" in key or "TOKEN" in key:
                value = "****"
            print(f"{key}={value}")
```

**Résultat** : ✅ Configuration affichée proprement

---

## 🐛 Prompt 4 - Debug Valeurs Null dans API

### Problème Rencontré

```python
TypeError: unsupported operand type(s) for >: 'NoneType' and 'float'
```

### Prompt de Debug

```
Erreur lors de l'analyse cyclone :

TypeError: unsupported operand type(s) for >: 'NoneType' and 'float'

Contexte : L'API Open-Meteo retourne parfois null dans les arrays hourly.

Exemple de réponse problématique :
```json
{
  "hourly": {
    "time": ["2025-11-28T00:00", "2025-11-28T01:00"],
    "wind_speed_10m": [15.2, null],
    "pressure_msl": [1013.2, 1013.1],
    "sea_surface_temperature": [27.5, 27.6]
  }
}
```

Code qui crash :
```python
for i in range(len(weather_data["hourly"]["time"])):
    wind = weather_data["hourly"]["wind_speed_10m"][i]
    if wind > 117:  # TypeError si wind est None
        return True
```

Améliore le code pour :
1. Détecter valeurs None avec `is None`
2. Logger warning avec timestamp de la valeur manquante
3. Skip cette heure dans l'analyse (continuer avec heure suivante)
4. Ne retourner résultat que si >50% des données valides
5. Ajouter compteur : nb_valeurs_valides / nb_total

Génère code robuste pour _extract_conditions() et detect().
```

### Solution Appliquée

```python
def _extract_conditions(self, weather_data, marine_data, hour_index):
    # Extraire valeurs
    wind = weather_data["hourly"]["wind_speed_10m"][hour_index]
    pressure = weather_data["hourly"]["pressure_msl"][hour_index]
    sst = marine_data["hourly"]["sea_surface_temperature"][hour_index]
    
    # Vérifier valeurs None
    if wind is None or pressure is None or sst is None:
        logger.warning(
            f"Missing data at hour {hour_index}: "
            f"wind={wind}, pressure={pressure}, sst={sst}"
        )
        return None  # Skip cette heure
    
    return {
        "wind_speed": wind,
        "pressure": pressure,
        "sst": sst,
        "time": weather_data["hourly"]["time"][hour_index]
    }

def detect(self, latitude, longitude, hours=48):
    valid_detections = 0
    total_hours = min(hours, len(weather_data["hourly"]["time"]))
    
    for i in range(total_hours):
        conditions = self._extract_conditions(weather_data, marine_data, i)
        if conditions is None:
            continue  # Skip heure avec données manquantes
        
        valid_detections += 1
        # ... analyse ...
    
    logger.info(f"Valid data: {valid_detections}/{total_hours} hours ({valid_detections/total_hours*100:.1f}%)")
```

**Résultat** : ✅ Gestion robuste des valeurs null

---

## 🔍 Prompt 5 - Revue de Code Assistée

```
Effectue une revue de code complète du projet Cyclone Tracker.

Fichiers à analyser :
- src/config/settings.py
- src/utils/api_client.py
- src/utils/error_handler.py
- src/services/weather_service.py
- src/services/marine_service.py
- src/services/cyclone_detector.py

Critères de revue :

1. **Architecture & Design**
   - [ ] Séparation des responsabilités (SRP)
   - [ ] Injection de dépendances
   - [ ] Couplage faible
   - [ ] Cohésion forte

2. **Code Quality**
   - [ ] Type hints complets
   - [ ] Docstrings claires
   - [ ] Nommage explicite (pas de x, tmp, etc.)
   - [ ] Fonctions < 50 lignes
   - [ ] Complexité cyclomatique < 10

3. **Error Handling**
   - [ ] Toutes les exceptions gérées
   - [ ] Messages d'erreur descriptifs
   - [ ] Pas de except générique
   - [ ] Ressources nettoyées (context managers)

4. **Performance**
   - [ ] Pas de calculs redondants
   - [ ] Pas de requêtes API inutiles
   - [ ] Cache utilisé efficacement
   - [ ] Pas de memory leaks

5. **Security**
   - [ ] Pas de secrets hardcodés
   - [ ] Input validation systématique
   - [ ] SQL injection impossible (pas de SQL ici)
   - [ ] XSS impossible

6. **Testing**
   - [ ] Coverage > 80%
   - [ ] Tests unitaires + intégration
   - [ ] Edge cases testés
   - [ ] Mocks appropriés

7. **Documentation**
   - [ ] README complet
   - [ ] Exemples de code
   - [ ] Architecture documentée
   - [ ] Installation claire

Pour chaque problème trouvé :
- Sévérité : 🔴 Critique / 🟡 Majeur / 🟢 Mineur
- Fichier et ligne
- Description du problème
- Solution recommandée
- Exemple de code corrigé

Génère rapport de revue complet au format Markdown.
```

### Rapport de Revue Généré

Voir : `docs/REVUE_CODE_FINALE.md`

---

## 🔄 Prompt 6 - Optimisations Performance

```
Analyse les performances du module et propose optimisations.

Métriques actuelles :
- Temps détection 1 location : ~1.8s
  - Weather API : 0.9s
  - Marine API : 0.8s
  - Analyse : 0.1s
- Détection 4 locations : ~7.2s (séquentiel)

Objectifs :
- Détection 1 location : <1s
- Détection 4 locations : <3s

Optimisations à implémenter :

1. **Appels API parallèles**
   ```python
   # Actuel (séquentiel)
   weather = weather_service.get_forecast(lat, lon)  # 0.9s
   marine = marine_service.get_forecast(lat, lon)    # 0.8s
   # Total : 1.7s
   
   # Optimisé (parallèle avec asyncio)
   weather, marine = await asyncio.gather(
       weather_service.get_forecast(lat, lon),
       marine_service.get_forecast(lat, lon)
   )
   # Total : 0.9s (temps du plus lent)
   ```

2. **Cache agressif**
   - TTL 15 min pour données actuelles
   - TTL 6h pour prévisions
   - Clé cache : f"{endpoint}:{lat}:{lon}:{forecast_days}"

3. **Connexion keep-alive**
   - Session requests réutilisée (déjà fait ✅)
   - Connection pooling

4. **Analyse optimisée**
   - Early exit si CYCLONE détecté (pas besoin d'analyser 48h)
   - Vectorisation avec numpy (optionnel)

Génère code optimisé pour api_client.py avec asyncio.
Garde compatibilité synchrone pour démo simple.
```

### Solution Appliquée (Partielle)

```python
# api_client.py - Version async (optionnelle)
import aiohttp
import asyncio

class AsyncAPIClient:
    async def get(self, endpoint, params, timeout=10):
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, params=params, timeout=timeout) as response:
                return await response.json()

# cyclone_detector.py - Version async
async def detect_async(self, latitude, longitude, hours=48):
    # Appels parallèles
    weather_data, marine_data = await asyncio.gather(
        self.weather_service.get_forecast_async(latitude, longitude),
        self.marine_service.get_marine_forecast_async(latitude, longitude)
    )
    # ... analyse ...
```

**Résultat** : 🟡 Async implémenté mais non utilisé en production (complexité)

---

## ✅ Prompt 7 - Validation Finale

```
Effectue validation complète avant livraison du Brief 2.

Checklist de validation :

### Fonctionnalités ✅
- [ ] Application démarre sans erreur
- [ ] Détection cyclone fonctionne (4 locations testées)
- [ ] Gestion erreurs complète (400, 429, 500, timeout)
- [ ] Logging opérationnel (fichier + console)
- [ ] Configuration via .env
- [ ] Cache Redis optionnel (pas obligatoire)

### Tests ✅
- [ ] 29 tests unitaires PASSED
- [ ] 7 tests d'intégration créés
- [ ] Coverage > 60%
- [ ] Pas de tests flaky
- [ ] pytest.ini configuré

### Documentation ✅
- [ ] README.md complet (installation, usage, exemples)
- [ ] SCHEMA_ARCHITECTURE.md avec 6 diagrammes Mermaid
- [ ] CAPTURES_POSTMAN.md avec 11 tests API
- [ ] docs/prompts/ avec 6 fichiers historique
- [ ] .env.example avec 40+ variables

### Code Quality ✅
- [ ] Type hints complets
- [ ] Docstrings présentes
- [ ] Pas de code commenté inutile
- [ ] Pas de print() debug oubliés
- [ ] .gitignore complet

### Sécurité ✅
- [ ] Pas de secrets dans le code
- [ ] .env dans .gitignore
- [ ] Validation inputs
- [ ] Pas de SQL/XSS

### Livrables Brief 2 ✅
- [ ] Module d'intégration API (src/)
- [ ] Tests d'intégration + capture (tests/, tests_execution_unit.txt)
- [ ] README technique complet
- [ ] Schéma architecture (Mermaid)
- [ ] Captures Postman/Thunder Client
- [ ] Dossier complet prompts utilisés (docs/prompts/)

Génère rapport final avec statut de chaque item.
```

### Rapport de Validation

Voir : `docs/VALIDATION_FINALE.md`

---

## 🎓 Leçons Apprises - Débogage

### ✅ Stratégies Efficaces

1. **Debug incrémental** :
   - Tester après chaque modification
   - Isoler le problème (print, debugger)
   - Corriger 1 bug à la fois

2. **Logs détaillés** :
   - Logger AVANT l'opération qui peut crasher
   - Logger les valeurs des variables
   - Logger stacktrace complète (exc_info=True)

3. **Tests de régression** :
   - Ajouter test pour chaque bug trouvé
   - Éviter réintroduction du bug

4. **Validation humaine** :
   - Ne pas faire confiance aveuglément au LLM
   - Tester avec données réelles
   - Revue de code par pair

### ⚠️ Pièges du Debug Assisté par LLM

1. **Solutions trop génériques** :
   - LLM propose souvent try/except large
   - Préférer gestion spécifique

2. **Optimisations prématurées** :
   - LLM suggère asyncio, caching complexe
   - Valider besoin réel d'optimisation

3. **Sur-engineering** :
   - LLM ajoute parfois trop d'abstraction
   - Garder KISS (Keep It Simple, Stupid)

### 🔧 Debug Checklist

```
Avant de demander aide LLM :
1. [ ] Lire stacktrace complète
2. [ ] Identifier ligne exacte qui crash
3. [ ] Vérifier valeurs des variables (print/log)
4. [ ] Reproduire bug de façon déterministe
5. [ ] Simplifier pour isoler le problème

Lors de demande aide LLM :
1. [ ] Fournir stacktrace complète
2. [ ] Donner contexte (structure projet, versions)
3. [ ] Montrer code qui crash (10 lignes contexte)
4. [ ] Expliquer ce qui était attendu
5. [ ] Mentionner tentatives de correction

Après correction LLM :
1. [ ] Comprendre la correction (ne pas copier-coller)
2. [ ] Tester avec plusieurs cas
3. [ ] Ajouter test de régression
4. [ ] Documenter dans prompts/debug.md
```

---

## ⏱️ Temps Passé

- **Debug ModuleNotFoundError** : 10 min
- **Debug FileNotFoundError** : 5 min
- **Debug AttributeError** : 5 min
- **Debug valeurs null** : 10 min
- **Revue de code assistée** : 15 min
- **Optimisations performance** : 10 min (partielles)
- **Validation finale** : 10 min

**Total Mission 6** : 1h05 ✅ (20min overtime pour revue complète)

---

## 🔗 Fichiers Modifiés

- `src/main.py` (imports, création dossiers)
- `src/config/settings.py` (display())
- `src/services/cyclone_detector.py` (gestion null)
- `docs/REVUE_CODE_FINALE.md` (NOUVEAU)
- `docs/VALIDATION_FINALE.md` (NOUVEAU)
