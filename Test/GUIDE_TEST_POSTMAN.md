# Guide de Test Complet - API Open-Meteo Cyclones

## 🎯 OBJECTIF
Valider toutes les informations des documents d'analyse en testant réellement l'API avec Postman.

---

## ✅ ÉTAPE 1 : Installation et configuration (5 min)

### 1.1 Installer Postman
1. Télécharger : https://www.postman.com/downloads/
2. Installer et créer un compte gratuit
3. Ouvrir Postman Desktop

### 1.2 Créer un environnement
1. Dans Postman, cliquer sur **Environments** (panneau gauche)
2. Cliquer **"+"** pour créer un nouvel environnement
3. Nommer : `Cyclone Océan Indien`
4. Ajouter ces variables :

| Variable | Initial Value | Current Value |
|----------|--------------|---------------|
| `lat` | `-20.0` | `-20.0` |
| `lon` | `55.5` | `55.5` |
| `tz` | `Indian/Reunion` | `Indian/Reunion` |

5. Cliquer **Save**
6. Sélectionner cet environnement dans le menu déroulant en haut à droite

---

## ✅ ÉTAPE 2 : Créer une collection (2 min)

1. Cliquer **Collections** (panneau gauche)
2. Cliquer **"+"** → **Create Collection**
3. Nommer : `Open-Meteo Cyclones`
4. Cliquer **Save**

---

## ✅ ÉTAPE 3 : Tests de base (10 min)

### TEST 1 : Endpoint Weather Forecast existe-t-il ? ✅

**Action :**
1. Dans votre collection, cliquer **Add request**
2. Nommer : `TEST 1 - Weather Forecast Base`
3. Méthode : **GET**
4. URL : 
```
https://api.open-meteo.com/v1/forecast?latitude={{lat}}&longitude={{lon}}&hourly=temperature_2m
```
5. Cliquer **Send**

**Résultat attendu :**
- ✅ Status : `200 OK` (en vert)
- ✅ Response contient JSON avec `latitude`, `longitude`, `hourly`
- ✅ `hourly.temperature_2m` contient un array de nombres

**Si ça marche :**
```json
{
  "latitude": -20.0,
  "longitude": 55.5,
  "hourly": {
    "time": ["2025-11-24T00:00", "2025-11-24T01:00", ...],
    "temperature_2m": [25.3, 25.1, 24.9, ...]
  }
}
```

**Si ça échoue :**
- ❌ Status 400 → Vérifier syntaxe URL
- ❌ Status 404 → API changée (à documenter)
- ❌ Timeout → Problème réseau

---

### TEST 2 : Variables cycloniques disponibles ? 🌀

**Action :**
1. Nouvelle requête : `TEST 2 - Variables Cyclone`
2. Méthode : **GET**
3. URL :
```
https://api.open-meteo.com/v1/forecast?latitude={{lat}}&longitude={{lon}}&hourly=wind_speed_10m,wind_gusts_10m,pressure_msl&forecast_days=3
```
4. Cliquer **Send**

**Vérifications :**
- ✅ `hourly.wind_speed_10m` existe et contient valeurs 0-150 km/h
- ✅ `hourly.wind_gusts_10m` existe et ≥ wind_speed_10m
- ✅ `hourly.pressure_msl` existe et contient valeurs 980-1030 hPa
- ✅ Array longueur ~72 (3 jours × 24h)

**Onglet Tests (facultatif) :**
Copier ce code pour automatiser la validation :
```javascript
pm.test("Status 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Variables cycloniques présentes", function () {
    const json = pm.response.json();
    pm.expect(json.hourly).to.have.property('wind_speed_10m');
    pm.expect(json.hourly).to.have.property('pressure_msl');
});

pm.test("Valeurs plausibles", function () {
    const json = pm.response.json();
    const pressure = json.hourly.pressure_msl[0];
    pm.expect(pressure).to.be.within(950, 1050);
});
```

---

### TEST 3 : Marine API (température surface océan) 🌊

**Action :**
1. Nouvelle requête : `TEST 3 - Marine SST`
2. Méthode : **GET**
3. URL :
```
https://marine-api.open-meteo.com/v1/marine?latitude={{lat}}&longitude={{lon}}&hourly=sea_surface_temperature,wave_height
```
4. Cliquer **Send**

**Vérifications :**
- ✅ Status 200
- ✅ `sea_surface_temperature` existe
- ✅ Valeurs SST entre 20-32°C (Océan Indien)
- ✅ `wave_height` existe (0-15m)

**Point critique :**
Si SST > 26.5°C → Conditions favorables cyclone ⚠️

---

### TEST 4 : L'API Tropical Cyclone existe-t-elle ? ❌

**Action :**
1. Nouvelle requête : `TEST 4 - Tropical Cyclone (404?)`
2. Méthode : **GET**
3. URL :
```
https://api.open-meteo.com/v1/tropical-cyclone?latitude={{lat}}&longitude={{lon}}
```
4. Cliquer **Send**

**Résultat attendu :**
- ❌ Status : `404 Not Found`
- ❌ Confirme que l'endpoint cyclone dédié **n'existe pas**

**Conclusion :**
✅ Valide notre analyse : pas d'API cyclone spécifique, il faut construire la détection nous-mêmes.

---

## ✅ ÉTAPE 4 : Tests avancés (15 min)

### TEST 5 : Modèle ECMWF spécifique

**URL :**
```
https://api.open-meteo.com/v1/forecast?latitude={{lat}}&longitude={{lon}}&hourly=wind_speed_10m,pressure_msl&models=ecmwf_ifs&forecast_days=10
```

**Vérifications :**
- ✅ Status 200
- ✅ Array plus long (~240 valeurs pour 10 jours)
- ✅ Comparer avec `models=auto` : données différentes ?

---

### TEST 6 : Prévision longue (16 jours)

**URL :**
```
https://api.open-meteo.com/v1/forecast?latitude={{lat}}&longitude={{lon}}&hourly=pressure_msl&forecast_days=16
```

**Vérifications :**
- ✅ Status 200
- ✅ Array longueur ~384 (16j × 24h)
- ⚠️ Vérifier intervalles temps : 1h puis 3h puis 6h après 144h ?

**Test intervalle :**
```javascript
pm.test("Résolution temporelle", function() {
    const times = pm.response.json().hourly.time;
    const t1 = new Date(times[0]);
    const t2 = new Date(times[1]);
    const diff = (t2 - t1) / 3600000; // heures
    console.log(`Intervalle début : ${diff}h`);
    pm.expect(diff).to.equal(1); // Doit être 1h au début
});
```

---

### TEST 7 : Ensemble API (incertitudes)

**URL :**
```
https://ensemble-api.open-meteo.com/v1/ensemble?latitude={{lat}}&longitude={{lon}}&hourly=pressure_msl&models=ecmwf_ifs025&forecast_days=3
```

**Vérifications :**
- ✅ Status 200
- ✅ Structure différente : `pressure_msl` est un array 2D
- ✅ Premier timestamp contient 51 valeurs (membres ensemble)

**Test structure :**
```javascript
pm.test("51 membres ECMWF", function() {
    const pressure = pm.response.json().hourly.pressure_msl;
    pm.expect(pressure[0].length).to.equal(51);
    console.log(`Min: ${Math.min(...pressure[0])} | Max: ${Math.max(...pressure[0])}`);
});
```

---

## ✅ ÉTAPE 5 : Simulation détection cyclone (20 min)

### TEST 8 : Algorithmique cyclone

**Créer cette requête :**
```
https://api.open-meteo.com/v1/forecast?latitude={{lat}}&longitude={{lon}}&hourly=wind_speed_10m,pressure_msl,temperature_2m&forecast_days=7&timezone={{tz}}
```

**Onglet Tests - Copier ce script complet :**
```javascript
pm.test("Status 200", function () {
    pm.response.to.have.status(200);
});

// Détection cyclone
pm.test("Analyse conditions cycloniques", function () {
    const json = pm.response.json();
    const times = json.hourly.time;
    const wind = json.hourly.wind_speed_10m;
    const pressure = json.hourly.pressure_msl;
    
    let cycloneDetected = false;
    let alertes = [];
    
    for (let i = 0; i < times.length; i++) {
        // Critères cyclone tropical
        if (pressure[i] < 980 && wind[i] > 117) {
            cycloneDetected = true;
            alertes.push({
                time: times[i],
                pressure: pressure[i],
                wind: wind[i],
                category: "CYCLONE TROPICAL"
            });
        }
        // Critères tempête tropicale
        else if (pressure[i] < 995 && wind[i] > 88 && wind[i] <= 117) {
            alertes.push({
                time: times[i],
                pressure: pressure[i],
                wind: wind[i],
                category: "TEMPÊTE TROPICALE"
            });
        }
        // Critères dépression tropicale
        else if (pressure[i] < 1000 && wind[i] > 62 && wind[i] <= 88) {
            alertes.push({
                time: times[i],
                pressure: pressure[i],
                wind: wind[i],
                category: "DÉPRESSION TROPICALE"
            });
        }
    }
    
    if (alertes.length > 0) {
        console.log(`⚠️ ${alertes.length} alertes détectées :`);
        alertes.slice(0, 5).forEach(a => {
            console.log(`  - ${a.time} : ${a.category} (${a.wind} km/h, ${a.pressure} hPa)`);
        });
    } else {
        console.log("✅ Aucune condition cyclonique détectée sur 7 jours");
    }
    
    pm.environment.set("cyclone_alert", cycloneDetected);
});
```

**Résultat attendu :**
- Si pas de cyclone → Console affiche "✅ Aucune condition..."
- Si cyclone → Console liste les alertes avec catégories

---

### TEST 9 : Combiner Marine + Weather

**Créer 2 requêtes séquentielles :**

**9A - Marine SST :**
```
https://marine-api.open-meteo.com/v1/marine?latitude={{lat}}&longitude={{lon}}&hourly=sea_surface_temperature
```

Tests :
```javascript
const sst = pm.response.json().hourly.sea_surface_temperature;
const avgSST = sst.reduce((a,b) => a+b, 0) / sst.length;
pm.environment.set("avg_sst", avgSST);
console.log(`Température surface : ${avgSST.toFixed(1)}°C`);
if (avgSST > 26.5) {
    console.log("✅ Conditions thermiques favorables cyclone");
}
```

**9B - Weather conditions :**
```
https://api.open-meteo.com/v1/forecast?latitude={{lat}}&longitude={{lon}}&current=wind_speed_10m,pressure_msl
```

Tests :
```javascript
const sst = parseFloat(pm.environment.get("avg_sst"));
const current = pm.response.json().current;

console.log("\n=== ÉVALUATION RISQUE CYCLONIQUE ===");
console.log(`SST : ${sst.toFixed(1)}°C ${sst > 26.5 ? '✅' : '❌'}`);
console.log(`Pression : ${current.pressure_msl} hPa ${current.pressure_msl < 1000 ? '⚠️' : '✅'}`);
console.log(`Vents : ${current.wind_speed_10m} km/h ${current.wind_speed_10m > 62 ? '⚠️' : '✅'}`);

let risk = "FAIBLE";
if (sst > 26.5 && current.pressure_msl < 995 && current.wind_speed_10m > 88) {
    risk = "ÉLEVÉ";
} else if (sst > 26.5 && current.pressure_msl < 1005) {
    risk = "MODÉRÉ";
}
console.log(`\nRISQUE CYCLONIQUE : ${risk}`);
```

---

## ✅ ÉTAPE 6 : Tester plusieurs zones (15 min)

### Créer des environnements multiples

| Environnement | Latitude | Longitude | Zone |
|--------------|----------|-----------|------|
| `Réunion` | -21.1 | 55.5 | La Réunion |
| `Maurice` | -20.2 | 57.5 | Île Maurice |
| `Madagascar` | -18.9 | 47.5 | Madagascar Est |
| `Haute mer` | -15.0 | 70.0 | Océan Indien centre |

**Test comparatif :**
1. Lancer la même requête sur chaque environnement
2. Comparer SST, vents, pression
3. Noter différences côte vs haute mer

---

## ✅ ÉTAPE 7 : Tests de limites (10 min)

### TEST 10 : Rate limiting

**Utiliser Postman Runner :**
1. Sélectionner votre collection
2. Cliquer **Run collection**
3. Paramètres :
   - Iterations : `100`
   - Delay : `100 ms`
4. Run

**Observer :**
- ✅ Toutes requêtes → 200 OK : Pas de rate limit atteint
- ❌ Apparition 429 → Rate limit détecté (noter à quelle itération)

---

### TEST 11 : Paramètres invalides

**Tester erreurs API :**

**URL invalide 1 (variable inexistante) :**
```
https://api.open-meteo.com/v1/forecast?latitude={{lat}}&longitude={{lon}}&hourly=cyclone_intensity
```
**Attendu :** 400 Bad Request avec message erreur

**URL invalide 2 (modèle inexistant) :**
```
https://api.open-meteo.com/v1/forecast?latitude={{lat}}&longitude={{lon}}&hourly=temperature_2m&models=tropical_model
```
**Attendu :** 400 Bad Request

**URL invalide 3 (coordonnées hors limites) :**
```
https://api.open-meteo.com/v1/forecast?latitude=100&longitude=55.5&hourly=temperature_2m
```
**Attendu :** 400 Bad Request

---

## ✅ ÉTAPE 8 : Validation données historiques (Bonus)

### Tester cyclone réel passé

**Exemple : Cyclone Belal (janvier 2024 - Réunion)**

**URL Historical Weather :**
```
https://archive-api.open-meteo.com/v1/archive?latitude=-21.1&longitude=55.5&start_date=2024-01-14&end_date=2024-01-16&hourly=wind_speed_10m,wind_gusts_10m,pressure_msl
```

**Vérifications :**
- ✅ Status 200
- ✅ Période 14-16 janvier 2024
- ✅ Pics vents >100 km/h
- ✅ Chute pression <1000 hPa

**Comparer avec observations réelles Météo France La Réunion**

---

## 📊 TABLEAU RÉCAPITULATIF DES TESTS

| Test | Endpoint | Status attendu | Validation | Priorité |
|------|----------|----------------|------------|----------|
| 1 | Weather Forecast Base | ✅ 200 | Structure JSON | 🔴 Critique |
| 2 | Variables cycloniques | ✅ 200 | Valeurs plausibles | 🔴 Critique |
| 3 | Marine SST | ✅ 200 | SST 20-32°C | 🔴 Critique |
| 4 | Tropical Cyclone API | ❌ 404 | Confirme absence | 🔴 Critique |
| 5 | Modèle ECMWF | ✅ 200 | Données spécifiques | 🟠 Important |
| 6 | Forecast 16 jours | ✅ 200 | 384 timestamps | 🟠 Important |
| 7 | Ensemble API | ✅ 200 | 51 membres | 🟡 Optionnel |
| 8 | Détection algorithme | ✅ 200 | Script cyclone | 🔴 Critique |
| 9 | Marine + Weather | ✅ 200 × 2 | Risque combiné | 🟠 Important |
| 10 | Rate limiting | Variables | 100 iterations | 🟡 Optionnel |
| 11 | Erreurs API | ❌ 400 | Messages erreur | 🟡 Optionnel |

---

## ✅ CHECKLIST FINALE

Avant de valider votre fiche API, assurez-vous :

### Endpoints
- [ ] ✅ Weather Forecast fonctionne (200 OK)
- [ ] ✅ Marine Weather fonctionne (200 OK)
- [ ] ❌ Tropical Cyclone n'existe pas (404 confirmé)
- [ ] ✅ Ensemble API fonctionne (200 OK)

### Variables
- [ ] ✅ `wind_speed_10m` disponible et valide
- [ ] ✅ `wind_gusts_10m` disponible et valide
- [ ] ✅ `pressure_msl` disponible et valide
- [ ] ✅ `sea_surface_temperature` disponible et valide
- [ ] ✅ `wave_height` disponible et valide

### Modèles
- [ ] ✅ `ecmwf_ifs` fonctionne
- [ ] ✅ `models=auto` fonctionne
- [ ] ❌ `tropical_model` n'existe pas (erreur 400)

### Algorithme
- [ ] ✅ Script détection cyclone fonctionne
- [ ] ✅ Seuils validés (980 hPa, 117 km/h)
- [ ] ✅ Combinaison SST + pression + vents OK

### Limites
- [ ] ⚠️ Rate limiting mesuré (ou accepté 10k/jour)
- [ ] ⚠️ Latence 6h documentée
- [ ] ⚠️ Résolution temporelle observée

---

## 🎯 RÉSULTAT FINAL

Une fois tous les tests passés, vous pourrez affirmer dans votre fiche API :

✅ **Validé Postman** : Toutes les informations testées réellement  
✅ **Divergences LLM résolues** : Endpoint cyclone confirmé inexistant  
✅ **Algorithme fonctionnel** : Détection cyclone opérationnelle  
✅ **Limites identifiées** : Rate limit, latence, précision documentées  

---

## 📝 EXPORTER VOS RÉSULTATS

1. **Exporter collection Postman :**
   - Collection → ⋯ → Export
   - Format : Collection v2.1
   - Sauvegarder : `open-meteo-cyclones.postman_collection.json`

2. **Exporter environnement :**
   - Environment → ⋯ → Export
   - Sauvegarder : `cyclone-ocean-indien.postman_environment.json`

3. **Capturer résultats :**
   - Screenshots tests réussis (200 OK)
   - Console logs (détection cyclone)
   - Screenshots erreurs (404 tropical-cyclone)

---

**Temps total estimé : 1h30**  
**Prérequis : Postman Desktop + connexion internet**

Bon test ! 🚀
