# Mission 1 - Prompts pour la Génération du Squelette

## 📋 Contexte

**Date** : 28 novembre 2025  
**Durée** : 1h  
**Objectif** : Créer une architecture modulaire pour l'intégration API Open-Meteo avec détection cyclonique

---

## 🎯 Prompt Principal - Génération du Squelette

### Version Initiale

```
Génère un projet Python professionnel pour intégrer l'API Open-Meteo avec détection de cyclones.

Contraintes techniques :
- Architecture modulaire : services/, utils/, config/
- Python 3.12+
- Gestion d'erreurs personnalisées
- Configuration via fichier .env
- Logging professionnel
- Tests unitaires (pytest)

Structure attendue :
src/
  ├── config/
  │   ├── __init__.py
  │   └── settings.py (lecture .env)
  ├── services/
  │   ├── __init__.py
  │   ├── weather_service.py (Weather Forecast API)
  │   ├── marine_service.py (Marine Weather API)
  │   └── cyclone_detector.py (algorithme détection)
  ├── utils/
  │   ├── __init__.py
  │   ├── api_client.py (requêtes HTTP réutilisables)
  │   └── error_handler.py (exceptions custom)
  └── main.py
tests/
  ├── conftest.py
  ├── test_weather_service.py
  ├── test_marine_service.py
  ├── test_cyclone_detector.py
  └── test_integration.py
docs/
.env.example
.gitignore
requirements.txt
README.md

Spécifications API :
- Weather Forecast : https://api.open-meteo.com/v1/forecast
- Marine Weather : https://marine-api.open-meteo.com/v1/marine
- Variables critiques : wind_speed_10m, wind_gusts_10m, pressure_msl, sea_surface_temperature

Critères de détection cyclonique :
- SST > 26.5°C
- Pression < 980 hPa → CYCLONE
- Pression < 995 hPa → TEMPÊTE
- Pression < 1000 hPa → DÉPRESSION
- Vent > 117 km/h → CYCLONE

Génère UNIQUEMENT la structure et les imports de base. Ne code pas encore la logique métier.
```

### Version Affinée (après première itération)

```
Améliore le squelette Python précédent avec ces ajouts :

1. Config avancée :
   - Classe Settings avec validation
   - Méthode display() pour afficher config
   - Valeurs par défaut si .env manquant
   - Type hints complets

2. Error Handler robuste :
   - APIError (base)
   - RateLimitError (429)
   - TimeoutError (timeout)
   - ValidationError (paramètres invalides)
   - CacheError (Redis)
   - ConfigurationError (.env)
   - DataNotFoundError (réponse vide)

3. API Client avec :
   - Session requests réutilisable
   - Retry automatique (3 tentatives)
   - Exponential backoff
   - Timeout configurable
   - Logging détaillé
   - Cache Redis optionnel

4. Dossiers additionnels :
   - logs/ (gitignored)
   - postman/ (collections tests)
   - docs/prompts/ (historique LLM)

Génère le code Python complet pour settings.py et error_handler.py.
```

---

## 🔄 Prompts de Raffinement

### Prompt 1 - Imports Relatifs

**Problème rencontré** : `ModuleNotFoundError: No module named 'src'`

**Prompt de correction** :
```
Le module Python génère l'erreur "ModuleNotFoundError: No module named 'src'".

Structure actuelle :
Brief2_Integration_API/
  src/
    config/settings.py (from src.config import ...)
    main.py

Corrige les imports pour utiliser :
- Imports relatifs dans src/ (from .config import, from ..utils import)
- Ajout de sys.path dans main.py si nécessaire
- Package __init__.py correctement configurés

Explique la différence entre imports absolus et relatifs pour cette structure.
```

**Résultat** : Changement de tous les imports vers imports relatifs

---

### Prompt 2 - Création Dossiers Automatique

**Problème rencontré** : `FileNotFoundError: logs/cyclone_tracker.log`

**Prompt de correction** :
```
Le code échoue car le dossier logs/ n'existe pas au premier lancement.

Modifie le code pour :
1. Créer automatiquement les dossiers manquants (logs/, postman/, docs/)
2. Utiliser pathlib.Path avec mkdir(parents=True, exist_ok=True)
3. Ajouter la création au démarrage de l'application

Code actuel qui échoue :
logging.basicConfig(
    filename=settings.LOG_FILE,  # logs/cyclone_tracker.log
    ...
)

Corrige avec création préalable du dossier.
```

**Résultat** : Ajout de `Path(settings.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)`

---

### Prompt 3 - Validation Settings

**Prompt** :
```
Ajoute une méthode validate() dans la classe Settings pour :
- Vérifier que les URLs API sont valides (https://)
- Valider RETRY_COUNT > 0
- Valider TIMEOUT > 0
- Valider les seuils cycloniques (SST > 0, PRESSURE < 1100)
- Lever ConfigurationError si invalide

Appelle validate() automatiquement dans __init__().
```

---

## 📊 Résultats de la Génération

### Fichiers Créés (11 fichiers Python)

```
✅ src/__init__.py (2 lignes)
✅ src/config/__init__.py (3 lignes)
✅ src/config/settings.py (76 statements, 200+ lignes)
✅ src/utils/__init__.py (3 lignes)
✅ src/utils/error_handler.py (50 lignes, 7 exceptions)
✅ src/utils/api_client.py (104 statements, 270+ lignes)
✅ src/services/__init__.py (4 lignes)
✅ src/services/weather_service.py (46 statements, 200+ lignes)
✅ src/services/marine_service.py (48 statements, 180+ lignes)
✅ src/services/cyclone_detector.py (78 statements, 275+ lignes)
✅ src/main.py (65 statements, 150+ lignes)
```

### Fichiers Configuration (5 fichiers)

```
✅ .env.example (40+ variables)
✅ .gitignore (Python standard)
✅ requirements.txt (12 dépendances)
✅ pytest.ini (configuration tests)
✅ README.md (300+ lignes)
```

---

## 🎓 Leçons Apprises

### ✅ Ce Qui a Fonctionné

1. **Contraintes claires dans le prompt** :
   - Architecture imposée → respect strict
   - Exemples d'APIs → intégration directe
   - Critères cycloniques → algorithme précis

2. **Génération itérative** :
   - Squelette d'abord → validation structure
   - Code ensuite → validation fonctionnelle
   - Corrections incrémentales → stabilité

3. **Séparation des responsabilités** :
   - Config isolée → changements faciles
   - Utils réutilisables → DRY principle
   - Services métier → logique claire

### ⚠️ Pièges Évités

1. **Import absolus vs relatifs** :
   - Problème : Python ne trouve pas 'src' en absolu
   - Solution : Imports relatifs dans package
   - Prompt : Expliciter la structure attendue

2. **Dossiers manquants** :
   - Problème : logs/ non créé au démarrage
   - Solution : mkdir(parents=True, exist_ok=True)
   - Prompt : Demander gestion automatique

3. **Validation config** :
   - Problème : .env mal formaté = crash silencieux
   - Solution : validate() avec exceptions claires
   - Prompt : Demander validation explicite

### 🔧 Améliorations Futures

1. **Cache Redis** : Implémenté dans api_client mais non testé
2. **Async/await** : Appels API séquentiels actuellement
3. **Rate limiting** : Détecté (429) mais pas de backoff intelligent
4. **Monitoring** : Logs créés mais pas de métriques

---

## 📝 Template de Prompt Réutilisable

```
Génère un projet [LANGAGE] professionnel pour [OBJECTIF].

Contraintes techniques :
- Architecture : [DOSSIERS]
- Version : [LANGAGE] [VERSION]+
- Gestion d'erreurs : [TYPE]
- Configuration : [METHODE]
- Tests : [FRAMEWORK]

Structure attendue :
[ARBORESCENCE EXACTE]

Spécifications techniques :
- APIs : [LISTE]
- Variables critiques : [LISTE]
- Algorithmes : [DESCRIPTION]

Critères de qualité :
- [CRITERE_1]
- [CRITERE_2]

Génère [PHASE] (squelette / code complet / tests).
```

---

## ⏱️ Temps Passé

- **Génération initiale** : 5 min (LLM)
- **Correction imports** : 10 min (debug + prompt)
- **Création dossiers** : 5 min (prompt)
- **Validation** : 10 min (tests manuels)
- **Documentation** : 30 min (ce fichier)

**Total Mission 1** : 1h ✅

---

## 🔗 Fichiers Liés

- `src/config/settings.py` - Configuration générée
- `src/utils/error_handler.py` - Exceptions custom
- `.env.example` - Template configuration
- `README.md` - Documentation principale
