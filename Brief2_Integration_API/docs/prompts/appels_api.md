# Mission 2 - Prompts pour l'Implémentation des Appels API

## 📋 Contexte

**Date** : 28 novembre 2025  
**Durée** : 1h30  
**Objectif** : Développer les fonctions d'intégration API pour récupérer les variables météorologiques critiques

---

## 🎯 Prompt Principal - WeatherService

### Version 1 - Génération Basique

```
Génère une classe WeatherService en Python pour intégrer l'API Open-Meteo Weather Forecast.

Endpoint : https://api.open-meteo.com/v1/forecast

Variables à récupérer :
- wind_speed_10m : Vitesse du vent à 10m (km/h)
- wind_gusts_10m : Rafales de vent à 10m (km/h)
- pressure_msl : Pression atmosphérique au niveau de la mer (hPa)

Fonctionnalités requises :
1. Méthode get_forecast(latitude, longitude, forecast_days=7)
   - URL dynamique avec paramètres
   - Validation coordonnées (lat: -90 à 90, lon: -180 à 180)
   - Validation forecast_days (1 à 16)
   - Gestion erreurs 400 (Bad Request)
   - Gestion erreurs 429 (Rate Limit)
   - Gestion erreurs 500 (Server Error)
   - Timeout 10 secondes
   - Parsing réponse JSON

2. Méthode get_current_weather(latitude, longitude)
   - Récupérer seulement heure actuelle
   - Même validation que get_forecast

3. Gestion d'erreurs :
   - Lever ValidationError si coordonnées invalides
   - Lever RateLimitError si 429
   - Lever TimeoutError si timeout
   - Lever APIError pour autres erreurs

4. Logging :
   - Logger chaque appel API
   - Logger succès avec temps de réponse
   - Logger erreurs avec détails

Utilise la classe APIClient de utils/api_client.py pour les requêtes HTTP.

Génère le code complet avec docstrings et type hints.
```

**Résultat** : `src/services/weather_service.py` (200+ lignes)

---

### Version 2 - Parsing Amélioré

```
Améliore le parsing de la réponse API dans WeatherService.

Problème actuel : La réponse contient des arrays avec 168 valeurs (7 jours × 24h).

Amélioration demandée :
1. Méthode privée _parse_response(response_data)
   - Vérifier présence de 'hourly'
   - Vérifier présence des variables requises
   - Extraire timestamps
   - Créer structure propre :
     {
       "latitude": float,
       "longitude": float,
       "timezone": str,
       "data": [
         {
           "time": "2025-11-28T00:00",
           "wind_speed": 15.2,
           "wind_gusts": 25.4,
           "pressure": 1013.2
         },
         ...
       ]
     }
   - Lever DataNotFoundError si données manquantes

2. Gérer les valeurs null dans les arrays
   - Remplacer null par None en Python
   - Logger warning si trop de valeurs manquantes (>10%)

3. Validation cohérence temporelle
   - Vérifier que len(time) == len(wind_speed) == len(pressure)

Génère le code de _parse_response() avec gestion complète des edge cases.
```

**Résultat** : Méthode `_parse_response()` robuste avec validation

---

## 🌊 Prompt Principal - MarineService

```
Génère une classe MarineService en Python pour intégrer l'API Open-Meteo Marine Weather.

Endpoint : https://marine-api.open-meteo.com/v1/marine

Variables à récupérer :
- sea_surface_temperature (SST) : Température surface mer (°C)
- wave_height : Hauteur des vagues (m)
- wave_direction : Direction des vagues (°)

Spécificités Marine API :
- Maximum 7 jours de prévisions (vs 16 pour Weather)
- Résolution 8km (modèle MFWAM)
- Disponible uniquement pour zones océaniques

Fonctionnalités requises :
1. Méthode get_marine_forecast(latitude, longitude, forecast_days=7)
   - Validation forecast_days max 7 (lever ValidationError si >7)
   - Même validation coordonnées que WeatherService
   - Timeout 10 secondes
   - Parsing réponse JSON

2. Méthode get_sst(latitude, longitude)
   - Récupérer seulement SST actuelle
   - Utilisé pour détection cyclones (seuil 26.5°C)

3. Méthode privée _parse_marine_response()
   - Structure similaire à WeatherService
   - Gérer cas où wave_direction est null (eaux calmes)

4. Validation zone océanique (optionnel) :
   - Logger warning si coordonnées loin des océans
   - Utiliser heuristique simple (distance côtes)

Hérite de la même architecture que WeatherService pour cohérence.

Génère le code complet avec docstrings.
```

**Résultat** : `src/services/marine_service.py` (180+ lignes)

---

## 🔧 Prompt - APIClient Générique

```
Génère une classe APIClient réutilisable pour tous les appels API Open-Meteo.

Fonctionnalités core :
1. Méthode get(endpoint, params, timeout=10)
   - Session requests persistante (performance)
   - Headers User-Agent descriptif
   - Retry automatique 3 fois
   - Exponential backoff : delay = RETRY_DELAY * (2 ^ attempt)
   - Max delay 60 secondes
   - Logging détaillé pour chaque tentative

2. Gestion erreurs HTTP :
   - 400 → ValidationError
   - 429 → RateLimitError (avec retry-after)
   - 500-599 → APIError
   - Timeout → TimeoutError
   - ConnectionError → APIError

3. Validation paramètres :
   - Méthode privée _validate_params(params)
   - Vérifier types (latitude/longitude = float)
   - Vérifier ranges
   - Lever ValidationError si invalide

4. Cache (optionnel avec Redis) :
   - Méthode _get_cache_key(endpoint, params)
   - Méthode _check_cache(key)
   - TTL 6 heures (données météo changent peu)
   - Désactivable via config

5. Méthode privée _calculate_backoff_delay(attempt)
   - Formule : min(RETRY_DELAY * (2 ** attempt), MAX_DELAY)
   - Jitter aléatoire ±20% pour éviter thundering herd

Architecture :
- Utilise Settings pour configuration
- Logger pour observabilité
- Type hints complets
- Docstrings détaillées

Génère le code complet de api_client.py.
```

**Résultat** : `src/utils/api_client.py` (270+ lignes, 104 statements)

---

## 🌀 Prompt Principal - CycloneDetector

```
Génère une classe CycloneDetector en Python pour analyser les données météo/marines et détecter les cyclones.

Algorithme de détection (basé Brief1) :

Conditions CYCLONE (risque ÉLEVÉ) :
- SST > 26.5°C ET
- Pression < 980 hPa ET
- Vent > 117 km/h (64 nœuds)

Conditions TEMPÊTE (risque MODÉRÉ) :
- SST > 26.5°C ET
- Pression < 995 hPa ET
- Vent > 88 km/h (48 nœuds)

Conditions DÉPRESSION (risque MODÉRÉ) :
- SST > 26.5°C ET
- Pression < 1000 hPa ET
- Vent > 62 km/h (34 nœuds)

Sinon : NORMAL (risque FAIBLE)

Méthodes requises :

1. detect(latitude, longitude, hours_to_analyze=48)
   - Appeler WeatherService.get_forecast()
   - Appeler MarineService.get_marine_forecast()
   - Analyser les X prochaines heures
   - Retourner première détection OU détection la plus sévère
   - Format retour :
     {
       "cyclone_detected": bool,
       "category": "CYCLONE"|"TEMPÊTE"|"DÉPRESSION"|"NORMAL",
       "risk_level": "ÉLEVÉ"|"MODÉRÉ"|"FAIBLE",
       "conditions": {
         "time": str,
         "wind_speed": float,
         "wind_gusts": float,
         "pressure": float,
         "sst": float
       },
       "location": {"latitude": float, "longitude": float},
       "timestamp": str,
       "total_detections": int
     }

2. _analyze_conditions(wind, pressure, sst) -> tuple[bool, str, str]
   - Appliquer arbre de décision
   - Retourner (detected, category, risk)

3. _extract_conditions(weather_data, marine_data, hour_index) -> dict
   - Extraire valeurs pour heure spécifique
   - Gérer valeurs manquantes (None)

4. _severity_score(category) -> int
   - CYCLONE → 3
   - TEMPÊTE → 2
   - DÉPRESSION → 1
   - NORMAL → 0
   - Utilisé pour sélectionner détection la plus sévère

Injection dépendances :
- WeatherService et MarineService passés au constructeur
- Facilite les tests (mocking)

Logging :
- Logger chaque analyse
- Logger détections trouvées
- Logger temps d'exécution

Génère le code complet avec docstrings et type hints.
```

**Résultat** : `src/services/cyclone_detector.py` (275+ lignes, 78 statements)

---

## 🔄 Prompts de Raffinement

### Prompt 1 - Gestion Valeurs Null

**Problème** : API peut retourner `null` pour certaines heures

```
L'API Open-Meteo retourne parfois null dans les arrays hourly.

Exemple :
{
  "hourly": {
    "time": ["2025-11-28T00:00", "2025-11-28T01:00"],
    "wind_speed_10m": [15.2, null],
    "pressure_msl": [1013.2, 1013.1]
  }
}

Améliore le parsing pour :
1. Détecter valeurs null
2. Logger warning avec timestamp concerné
3. Skip cette heure dans l'analyse cyclone
4. Ne pas crasher l'application
5. Retourner données partielles si >50% valides

Ajoute compteur nb_valeurs_valides / nb_total dans le log.
```

---

### Prompt 2 - Validation Robuste

```
Ajoute validation complète des paramètres dans les services.

Pour chaque méthode publique :
1. Vérifier types avec isinstance()
2. Vérifier ranges avec comparaisons
3. Lever ValidationError avec message descriptif
4. Logger les validations qui échouent

Exemple de messages d'erreur attendus :
- "Latitude must be between -90 and 90, got: 999"
- "Forecast days must be between 1 and 7 for Marine API, got: 10"
- "Longitude must be a number, got: 'invalid'"

Ajoute tests parametrized dans test_weather_service.py pour :
- Coordonnées invalides : (999, 0), (0, 999), (-91, 0), (91, 0)
- Forecast days invalide : 0, -1, 17, "invalid"

Génère le code de validation et les tests pytest.
```

**Résultat** : 6 tests parametrized ajoutés

---

### Prompt 3 - Performance Logging

```
Ajoute mesure de performance dans les appels API.

Pour chaque requête HTTP :
1. time.time() avant appel
2. time.time() après réception
3. Calculer elapsed = end - start
4. Logger : "API call to {endpoint} completed in {elapsed:.2f}s"

Pour le CycloneDetector.detect() :
1. Mesurer temps total d'analyse
2. Mesurer temps par appel (Weather, Marine, algorithme)
3. Logger : "Cyclone detection completed in {total:.2f}s (Weather: {w:.2f}s, Marine: {m:.2f}s, Analysis: {a:.2f}s)"

Ajoute décorateur @timed optionnel pour automatiser.
```

---

## 📊 Validation des Appels API

### Test Manuel 1 - Weather Forecast

**URL construite** :
```
https://api.open-meteo.com/v1/forecast?latitude=-21.1&longitude=55.5&hourly=wind_speed_10m,wind_gusts_10m,pressure_msl&timezone=auto&forecast_days=7
```

**Résultat** : ✅ 200 OK (1.12s)

**Données reçues** :
- 168 timestamps (7j × 24h)
- wind_speed_10m: [15.2, 16.8, 18.3, ...]
- pressure_msl: [1013.2, 1013.1, ...]

---

### Test Manuel 2 - Marine Weather

**URL construite** :
```
https://marine-api.open-meteo.com/v1/marine?latitude=-21.1&longitude=55.5&hourly=sea_surface_temperature,wave_height&timezone=auto&forecast_days=7
```

**Résultat** : ✅ 200 OK (0.88s)

**Données reçues** :
- SST actuelle : 27.5°C (> 26.5°C seuil cyclonique ✅)
- wave_height: [1.8, 1.9, 2.1, ...]

---

### Test Manuel 3 - Détection Cyclone

**Input** : La Réunion (-21.1, 55.5)

**Résultat** :
```json
{
  "cyclone_detected": false,
  "category": "NORMAL",
  "risk_level": "FAIBLE",
  "conditions": {
    "time": "2025-11-28T00:00",
    "wind_speed": 15.2,
    "wind_gusts": 25.4,
    "pressure": 1013.2,
    "sst": 27.5
  }
}
```

**Analyse** :
- SST OK (27.5 > 26.5) ✅
- Pression trop haute (1013 > 1000) ❌
- Vent trop faible (15.2 < 62) ❌
- **Conclusion : NORMAL** ✅

---

## 🎓 Leçons Apprises

### ✅ Stratégies Efficaces

1. **Génération par couches** :
   - D'abord APIClient (base réutilisable)
   - Ensuite WeatherService et MarineService (spécialisés)
   - Enfin CycloneDetector (logique métier)
   - **Avantage** : Chaque couche testable indépendamment

2. **Prompt avec exemples JSON** :
   - Fournir exemple de réponse API réelle
   - LLM génère parsing exact
   - Moins d'itérations de correction

3. **Validation explicite** :
   - Demander validation dans prompt initial
   - Évite bugs silencieux
   - Messages d'erreur clairs pour debug

4. **Injection de dépendances** :
   - CycloneDetector reçoit services en paramètres
   - Facilite mocking dans tests
   - Architecture testable

### ⚠️ Pièges Évités

1. **Null vs None** :
   - JSON null → Python None
   - Vérifier avec `is None` pas `== None`

2. **Forecast days limité** :
   - Weather API : 16 jours max
   - Marine API : 7 jours max
   - Validation différente par service

3. **Rate limiting** :
   - Open-Meteo : 10k requêtes/jour gratuit
   - Implémenter cache pour économiser
   - Retry-after header dans 429

### 🔧 Optimisations Futures

1. **Appels parallèles** :
   - Weather et Marine en asyncio.gather()
   - Réduire temps de 1.5s à 0.9s

2. **Cache intelligent** :
   - Redis avec TTL par type de données
   - Forecast : 6h
   - Current : 15min

3. **Batch analysis** :
   - Analyser plusieurs locations en une requête
   - API supporte multi-locations

---

## ⏱️ Temps Passé

- **WeatherService** : 20 min (génération + tests)
- **MarineService** : 15 min (similaire à Weather)
- **APIClient** : 25 min (retry logic complexe)
- **CycloneDetector** : 30 min (algorithme + tests)
- **Documentation** : 30 min (ce fichier)

**Total Mission 2** : 2h ✅ (30min overtime pour robustesse)

---

## 🔗 Fichiers Générés

- `src/utils/api_client.py` (104 statements)
- `src/services/weather_service.py` (46 statements)
- `src/services/marine_service.py` (48 statements)
- `src/services/cyclone_detector.py` (78 statements)
