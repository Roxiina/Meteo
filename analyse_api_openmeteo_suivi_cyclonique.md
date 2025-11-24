# Analyse API Open-Meteo : Suivi Cyclonique Océan Indien

**Date d'analyse** : 24 novembre 2025  
**Contexte métier** : Suivi et prévision des cyclones tropicaux dans l'Océan Indien  
**Source documentation** : https://open-meteo.com/en/docs

---

## 1. RÉSUMÉ EXÉCUTIF

### Constat principal
⚠️ **LIMITATION CRITIQUE IDENTIFIÉE** : Open-Meteo ne dispose **PAS** d'un endpoint dédié au suivi cyclonique (l'URL https://open-meteo.com/en/docs/tropical-cyclone-api retourne une erreur 404).

### Approche alternative recommandée
Utiliser une combinaison des endpoints suivants pour surveiller les conditions propices aux cyclones :
1. **Weather Forecast API** - Variables atmosphériques critiques
2. **Marine Weather API** - Conditions océaniques
3. **Ensemble API** - Modèles probabilistes ECMWF pour l'incertitude
4. **ECMWF API** - Modèle haute résolution (9 km)

---

## 2. ENDPOINTS PERTINENTS POUR LE SUIVI CYCLONIQUE

### 2.1 Weather Forecast API
**Endpoint** : `https://api.open-meteo.com/v1/forecast`  
**Documentation** : https://open-meteo.com/en/docs

#### Paramètres obligatoires
| Paramètre | Type | Description |
|-----------|------|-------------|
| `latitude` | Float | Coordonnées WGS84 (ex: -20.5 pour Réunion) |
| `longitude` | Float | Coordonnées WGS84 (ex: 55.5 pour Réunion) |
| `hourly` ou `daily` | String array | Liste des variables météo demandées |

#### Paramètres recommandés
| Paramètre | Valeur suggérée | Justification |
|-----------|-----------------|---------------|
| `models` | `ecmwf_ifs` | Meilleure couverture globale (9 km résolution) |
| `forecast_days` | `10-16` | Horizon suffisant pour trajectoires cycloniques |
| `timezone` | `Indian/Reunion` | Heure locale Océan Indien |
| `cell_selection` | `sea` | Préférence grilles océaniques |

#### Variables critiques pour détection cyclonique

**Variables horaires (`&hourly=`)**

| Variable | Unité | Type | Pertinence cyclone |
|----------|-------|------|-------------------|
| `pressure_msl` | hPa | Instant | 🔴 **CRITIQUE** : Détection dépression (<1000 hPa) |
| `wind_speed_10m` | km/h | Instant | 🔴 **CRITIQUE** : Vitesse vents soutenus (>117 km/h = cyclone) |
| `wind_gusts_10m` | km/h | Max heure précédente | 🔴 **CRITIQUE** : Rafales extrêmes |
| `wind_direction_10m` | ° | Instant | 🟠 **Important** : Structure rotation vents |
| `temperature_2m` | °C | Instant | 🟡 Contexte thermique |
| `precipitation` | mm | Somme heure précédente | 🟠 **Important** : Précipitations intenses |
| `cloud_cover` | % | Instant | 🟡 Couverture nuageuse totale |
| `cape` | J/kg | Instant | 🟠 **Important** : Énergie potentielle convective (instabilité) |
| `weather_code` | Code WMO | Instant | 🟡 Code conditions météo (95=orage, 82=pluies violentes) |

**Variables quotidiennes (`&daily=`)**

| Variable | Unité | Pertinence |
|----------|-------|------------|
| `wind_speed_10m_max` | km/h | 🔴 Vent max journalier |
| `wind_gusts_10m_max` | km/h | 🔴 Rafales max journalières |
| `precipitation_sum` | mm | 🟠 Cumul précipitations |
| `weather_code` | Code WMO | 🟡 Conditions dominantes |

#### Limites identifiées
- ❌ **Pas de variable "cyclone tracker"** officielle
- ❌ **Pas de trajectoire cyclonique prédite**
- ❌ **Pas de catégorie cyclonique** (Saffir-Simpson ou équivalent)
- ⚠️ Résolution temporelle : 1h (premiers 90h), puis 3h, puis 6h (après 144h)
- ⚠️ Mise à jour : toutes les 6 heures (peut manquer évolution rapide)

---

### 2.2 Marine Weather API
**Endpoint** : `https://marine-api.open-meteo.com/v1/marine`  
**Documentation** : https://open-meteo.com/en/docs/marine-weather-api

#### Variables océaniques critiques (`&hourly=`)

| Variable | Unité | Type | Pertinence cyclone |
|----------|-------|------|-------------------|
| `sea_surface_temperature` | °C | Instant | 🔴 **CRITIQUE** : Formation cyclone si >26,5°C |
| `wave_height` | m | Instant | 🔴 **CRITIQUE** : Vagues significatives (>8m = danger extrême) |
| `wave_direction` | ° | Instant | 🟠 Direction houle dominante |
| `wave_period` | s | Instant | 🟡 Période vagues moyennes |
| `swell_wave_height` | m | Instant | 🟠 Houle générée par cyclone distant |
| `ocean_current_velocity` | km/h | Instant | 🟡 Courants marins |
| `sea_level_height_msl` | m | Instant | 🟠 Surcote marine (marée tempête) |

#### Variables quotidiennes (`&daily=`)

| Variable | Unité | Pertinence |
|----------|-------|------------|
| `wave_height_max` | m | 🔴 Vague max journalière |
| `swell_wave_height_max` | m | 🟠 Houle max |

#### Modèles disponibles pour Océan Indien
| Modèle | Résolution | Mise à jour | Pertinence |
|--------|------------|-------------|------------|
| ECMWF WAM | 9 km | 6h | ✅ **Recommandé** (couverture globale) |
| MeteoFrance MFWAM | ~8 km | 12h | ✅ Bon pour Océan Indien Sud-Ouest |
| NCEP GFS Wave | 16-25 km | 6h | ✅ Alternative acceptable |

#### Limites
- ⚠️ **Avertissement documentation** : "Accuracy at coastal areas is limited. This is not suitable for coastal navigation"
- ⚠️ Données marées/courants : résolution 0.08° (~8 km), précision limitée près côtes
- ⏱️ Mise à jour : 6-12h selon modèle

---

### 2.3 Ensemble API (Prévisions probabilistes)
**Endpoint** : `https://ensemble-api.open-meteo.com/v1/ensemble`  
**Documentation** : https://open-meteo.com/en/docs/ensemble-api

#### Intérêt pour cyclones
Fournit des **prévisions probabilistes** via plusieurs membres d'ensemble (51 pour ECMWF IFS), permettant :
- Évaluation de l'**incertitude** sur trajectoire et intensité
- Détection de **scénarios multiples**
- **Fourchette de probabilités** (min/mean/max)

#### Modèle recommandé
| Modèle | Membres | Résolution | Horizon | Mise à jour |
|--------|---------|------------|---------|-------------|
| `ecmwf_ifs025` | 51 | 25 km | 15 jours | 6h |
| `gfs_seamless` | 31 | 25-50 km | 35 jours | 6h |

#### Variables pertinentes (exemples)
- `pressure_msl` (51 valeurs par timestamp)
- `wind_speed_10m` (distribution probabiliste)
- Variables quotidiennes : `_min`, `_mean`, `_max` (agrégations ensemble)

#### Limites
- ⚠️ **Coût API** : Compte pour **~4 appels** (facteur multiplicateur)
- ⚠️ Résolution spatiale réduite (25 km vs 9 km IFS direct)
- ⏱️ Résolution temporelle : 3h (6h pour AIFS)

---

### 2.4 ECMWF API (Haute résolution)
**Endpoint** : `https://api.open-meteo.com/v1/forecast?models=ecmwf_ifs`  
**Documentation** : https://open-meteo.com/en/docs/ecmwf-api

#### Avantages spécifiques
- ✅ **Résolution native 9 km** (grille O1280)
- ✅ Données horaires (90 premières heures)
- ✅ Horizon 15 jours
- ✅ Modèle de référence mondiale

#### Variables additionnelles vs API standard
| Variable | Unité | Pertinence cyclone |
|----------|-------|-------------------|
| `total_column_integrated_water_vapour` | kg/m² | 🟠 Humidité atmosphérique totale |
| `cape` | J/kg | 🟠 Instabilité convective |
| `soil_moisture_0_to_7cm` (etc.) | m³/m³ | 🟡 Saturation sols (précipitations) |
| Variables niveaux de pression | Divers | 🟡 Structure atmosphère 3D |

#### Limites
- ❌ **Pas d'humidité relative à 2m** (uniquement niveaux pression)
- ⏱️ Résolution temporelle dégradée après 90h (3h puis 6h)
- 💰 Licence : gratuit non-commercial (<10 000 appels/jour)

---

## 3. STRATÉGIE D'UTILISATION : ARCHITECTURE MVC

### 3.1 Modèle (Model) - Logique métier cyclonique

#### Critères de détection cyclone (à implémenter)
```
DÉPRESSION TROPICALE :
- Pression centrale < 1000 hPa
- Vents soutenus 62-87 km/h

TEMPÊTE TROPICALE :
- Pression < 995 hPa
- Vents soutenus 88-117 km/h

CYCLONE TROPICAL :
- Pression < 980 hPa
- Vents soutenus > 117 km/h
- SST > 26,5°C (formation)
- CAPE élevé (instabilité)
```

#### Zone géographique Océan Indien
```
Latitude : -30° à -5° (sud)
Longitude : 40° à 100° (est)
Zones prioritaires :
- Maurice : -20.2, 57.5
- Réunion : -21.1, 55.5
- Madagascar : -18.9, 47.5
- Seychelles : -4.6, 55.5
```

### 3.2 Vue (View) - Affichage données

#### Tableaux de bord requis
1. **Carte synoptique** (pression, vents, températures SST)
2. **Graphiques temporels** (évolution 15 jours)
3. **Alertes** (seuils dépassés)
4. **Incertitude** (fourchettes ensemble)

### 3.3 Contrôleur (Controller) - Orchestration appels API

#### Séquence recommandée
1. **Appel Marine API** → Vérifier SST >26,5°C (condition préalable)
2. **Appel Weather Forecast (ECMWF)** → Pression + vents + CAPE
3. **Appel Ensemble API** (si cyclone détecté) → Évaluer incertitude trajectoire
4. **Agrégation données** → Calcul indices cycloniques
5. **Stockage base de données** → Historique + comparaisons

---

## 4. MODÈLES MÉTÉOROLOGIQUES DISPONIBLES

### 4.1 Modèles recommandés pour Océan Indien

| Modèle | Provider | Résolution | Horizon | Mise à jour | Pertinence Océan Indien |
|--------|----------|------------|---------|-------------|------------------------|
| **ECMWF IFS** | ECMWF (UE) | 9 km | 15 jours | 6h | ⭐⭐⭐⭐⭐ **Meilleur** |
| **ECMWF AIFS** | ECMWF (IA) | 25 km | 15 jours | 6h | ⭐⭐⭐⭐ Bon (IA expérimental) |
| GFS | NOAA (US) | 25 km | 16 jours | 6h | ⭐⭐⭐ Acceptable |
| ACCESS-G | BOM (Australie) | 15 km | 10 jours | 6h | ⭐⭐⭐⭐ Bon (focus Pacifique Sud) |
| MeteoFrance | Météo-France | 25 km | 4 jours | 12h | ⭐⭐ Court terme uniquement |

### 4.2 Modèles marins

| Modèle | Résolution | Horizon | Pertinence |
|--------|------------|---------|------------|
| **ECMWF WAM** | 9 km | 15 jours | ⭐⭐⭐⭐⭐ **Recommandé** |
| MeteoFrance MFWAM | ~8 km | 10 jours | ⭐⭐⭐⭐ |
| NCEP GFS Wave | 16 km | 16 jours | ⭐⭐⭐ |

---

## 5. LIMITES ET RISQUES IDENTIFIÉS

### 5.1 Limitations techniques confirmées

| Limitation | Impact | Mitigation recommandée |
|------------|--------|------------------------|
| ❌ **Pas d'endpoint cyclone dédié** | 🔴 Critique | Développer algorithme détection custom |
| ❌ Pas de trajectoire cyclone prédite | 🔴 Critique | Modélisation trajectoire via données pression/vent |
| ❌ Pas de catégorie cyclone (Saffir-Simpson) | 🟠 Élevé | Calculer catégorie à partir vents soutenus |
| ⚠️ Résolution temporelle variable (1h→6h) | 🟡 Moyen | Interpolation temporelle si nécessaire |
| ⚠️ Mise à jour 6h | 🟡 Moyen | Accepter latence, compléter avec données temps réel (autre source) |
| ⚠️ Précision côtière limitée (Marine API) | 🟡 Moyen | Utiliser pour détection large, affiner avec modèles régionaux |

### 5.2 Risques opérationnels

| Risque | Probabilité | Gravité | Action requise |
|--------|-------------|---------|----------------|
| Faux négatifs (cyclone non détecté) | Moyenne | 🔴 Critique | Multi-seuils + validation manuelle |
| Faux positifs (alerte abusive) | Élevée | 🟠 Moyenne | Filtrage temporel (persistance conditions) |
| Latence données (6h) | Certaine | 🟡 Faible | Disclaimers utilisateurs + sources complémentaires |
| Données manquantes (API indisponible) | Faible | 🔴 Critique | Système de cache + fallback API alternatives |

### 5.3 Points à ABSOLUMENT vérifier dans la documentation

| Point | Raison | URL à consulter |
|-------|--------|-----------------|
| 📋 **Existence API Tropical Cyclone** | URL 404 détectée | https://open-meteo.com/en/docs/tropical-cyclone-api |
| 📋 Licence commerciale si >10k appels/jour | Conditions utilisation | https://open-meteo.com/en/terms |
| 📋 Disponibilité historique cyclones passés | Validation modèle | https://open-meteo.com/en/docs/historical-weather-api |
| 📋 Format erreur API (codes HTTP) | Gestion erreurs robuste | Documenter tests |
| 📋 Limites rate limiting (appels/min) | Architecture scalable | https://open-meteo.com/en/pricing |

---

## 6. VARIABLES MÉTÉOROLOGIQUES : RÉFÉRENCE COMPLÈTE

### 6.1 Codes WMO (Weather Code)

| Code | Signification | Pertinence cyclone |
|------|---------------|-------------------|
| 0 | Ciel dégagé | ⚪ |
| 1-3 | Partiellement nuageux | ⚪ |
| 51-67 | Bruine/pluie/pluie verglaçante | 🟡 |
| 80-82 | Averses pluie (82=violentes) | 🟠 **Indicateur précurseur** |
| 95 | Orage modéré/léger | 🟠 **Convection** |
| 96-99 | Orage avec grêle | 🔴 **Conditions extrêmes** |

### 6.2 Unités de mesure

| Variable | Unité par défaut | Alternatives disponibles |
|----------|------------------|-------------------------|
| Température | °C | °F (`temperature_unit=fahrenheit`) |
| Vitesse vent | km/h | m/s, mph, kn (`wind_speed_unit=`) |
| Précipitations | mm | inch (`precipitation_unit=inch`) |
| Pression | hPa | - |
| CAPE | J/kg | - |

---

## 7. FICHE API RÉUTILISABLE (TEMPLATE)

```markdown
# FICHE API : [Nom API]

## Informations générales
- **URL base** : 
- **Version** : 
- **Documentation** : 
- **Fournisseur** : 
- **Licence** : 

## Endpoints
| Endpoint | Méthode | Description | Latence |
|----------|---------|-------------|---------|
| | | | |

## Paramètres
### Obligatoires
| Paramètre | Type | Valeurs | Description |
|-----------|------|---------|-------------|

### Optionnels recommandés
| Paramètre | Type | Valeur défaut | Usage |

## Variables disponibles
### Horaires (`hourly`)
| Variable | Unité | Type | Pertinence métier | Limites |

### Quotidiennes (`daily`)
| Variable | Unité | Agrégation | Pertinence métier |

## Modèles sous-jacents
| Modèle | Résolution | Horizon | Mise à jour | Zone géo |

## Format réponse
```json
{
  "latitude": float,
  "longitude": float,
  "hourly": {
    "time": ["ISO8601"],
    "variable": [floats]
  }
}
```

## Gestion erreurs
| Code HTTP | Signification | Action |
|-----------|---------------|--------|
| 400 | Bad Request | Vérifier paramètres |
| 429 | Rate limit | Backoff exponentiel |
| 500 | Erreur serveur | Retry + alerting |

## Limites identifiées
- [ ] Limite 1
- [ ] Limite 2

## Points à vérifier
- [ ] Point incertain 1
- [ ] Point incertain 2

## Références
- Documentation officielle : 
- Changelog : 
- Support : 
```

---

## 8. RECOMMANDATIONS FINALES

### 8.1 Actions prioritaires

1. ✅ **VALIDÉ** : Confirmer absence endpoint cyclone dédié
2. 🔴 **URGENT** : Développer algorithme détection cyclonique custom basé sur :
   - Pression centrale < 980 hPa
   - Vents soutenus > 117 km/h
   - SST > 26,5°C
   - CAPE élevé
3. 🟠 **Important** : Tester fiabilité modèles ECMWF vs observations réelles (cyclones 2023-2024)
4. 🟡 **Souhaitable** : Intégrer source complémentaire temps réel (RSMC La Réunion, NHC)

### 8.2 Architecture système recommandée

```
[Open-Meteo APIs]
    ↓
[Controller : Orchestration appels]
    ↓
[Model : Détection cyclonique + Calculs]
    ↓
[Base de données : Historique]
    ↓
[View : Dashboard + Alertes]
```

### 8.3 Points de vigilance

- ⚠️ **NE PAS** se fier uniquement à `weather_code` (manque granularité cyclone)
- ⚠️ **TOUJOURS** croiser Marine API (SST) + Weather API (pression/vent)
- ⚠️ **PRÉVOIR** cache données en cas indisponibilité API
- ⚠️ **RESPECTER** limites 10 000 appels/jour (non-commercial)

---

## 9. SOURCES ET VALIDATION

### Documentation consultée (novembre 2025)
- ✅ Weather Forecast API : https://open-meteo.com/en/docs
- ✅ Marine Weather API : https://open-meteo.com/en/docs/marine-weather-api
- ✅ ECMWF API : https://open-meteo.com/en/docs/ecmwf-api
- ✅ Ensemble API : https://open-meteo.com/en/docs/ensemble-api
- ❌ Tropical Cyclone API : **404 Not Found** (endpoint n'existe pas)

### Informations incertaines / À vérifier

| Information | Statut | Action requise |
|-------------|--------|----------------|
| Précision modèles ECMWF Océan Indien | ⚠️ À valider | Comparer prévisions vs observations réelles |
| Rate limiting exact (requêtes/min) | ⚠️ Non documenté | Tests charge + contact support |
| Disponibilité historique cyclones | ⚠️ Supposé disponible | Tester Historical Weather API |
| Délai mise à disposition données | ⚠️ "6h" mentionné | Mesurer latence réelle |

---

**Document établi selon documentation officielle Open-Meteo - Toute information incertaine est explicitement marquée ⚠️**
