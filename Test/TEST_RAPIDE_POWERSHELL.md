# Test Rapide - URL Correcte Open-Meteo

## ⚠️ Erreur 403 Forbidden détectée

Si vous avez eu une erreur **403 Forbidden**, c'est probablement parce que :
1. Vous avez testé l'URL dans un navigateur web (bloquée par nginx)
2. Vous devez utiliser **Postman** ou un client HTTP approprié

---

## ✅ SOLUTION : Test avec Postman

### Option A : Postman Desktop (recommandé)

1. **Télécharger Postman** : https://www.postman.com/downloads/
2. **Ouvrir Postman**
3. **Nouvelle requête** :
   - Cliquer sur "New" → "HTTP Request"
   - Dans la barre d'URL, coller :
   ```
   https://api.open-meteo.com/v1/forecast?latitude=-20.0&longitude=55.5&hourly=temperature_2m
   ```
   - Cliquer **Send**

**Résultat attendu : 200 OK avec données JSON**

---

### Option B : PowerShell (test immédiat)

Depuis votre terminal PowerShell actuel, exécutez :

```powershell
# Test basique Weather API
$response = Invoke-RestMethod -Uri "https://api.open-meteo.com/v1/forecast?latitude=-20.0&longitude=55.5&hourly=temperature_2m"
$response | ConvertTo-Json -Depth 3

# Afficher quelques valeurs
Write-Host "Latitude: $($response.latitude)"
Write-Host "Longitude: $($response.longitude)"
Write-Host "Première température: $($response.hourly.temperature_2m[0])°C"
```

**Si ça fonctionne, vous verrez :**
```
Latitude: -20.0
Longitude: 55.5
Première température: 25.3°C
```

---

### Option C : Curl (ligne de commande)

```powershell
curl "https://api.open-meteo.com/v1/forecast?latitude=-20.0&longitude=55.5&hourly=temperature_2m"
```

---

## 🧪 Tests rapides PowerShell à copier-coller

### Test 1 : Variables cycloniques
```powershell
$cyclone = Invoke-RestMethod -Uri "https://api.open-meteo.com/v1/forecast?latitude=-20.0&longitude=55.5&hourly=wind_speed_10m,pressure_msl&forecast_days=3"

Write-Host "`n=== DONNÉES CYCLONIQUES ==="
Write-Host "Vent max: $([math]::Round(($cyclone.hourly.wind_speed_10m | Measure-Object -Maximum).Maximum, 1)) km/h"
Write-Host "Pression min: $([math]::Round(($cyclone.hourly.pressure_msl | Measure-Object -Minimum).Minimum, 1)) hPa"
```

### Test 2 : Marine API (SST)
```powershell
$marine = Invoke-RestMethod -Uri "https://marine-api.open-meteo.com/v1/marine?latitude=-20.0&longitude=55.5&hourly=sea_surface_temperature"

$avgSST = ($marine.hourly.sea_surface_temperature | Measure-Object -Average).Average
Write-Host "`n=== TEMPÉRATURE OCÉAN ==="
Write-Host "SST moyenne: $([math]::Round($avgSST, 1))°C"
if ($avgSST -gt 26.5) {
    Write-Host "⚠️ Conditions thermiques favorables cyclone" -ForegroundColor Yellow
} else {
    Write-Host "✅ Températures normales" -ForegroundColor Green
}
```

### Test 3 : Vérifier endpoint cyclone (doit être 404)
```powershell
try {
    $tropical = Invoke-RestMethod -Uri "https://api.open-meteo.com/v1/tropical-cyclone?latitude=-20.0&longitude=55.5"
    Write-Host "⚠️ API cyclone existe !" -ForegroundColor Yellow
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "`n✅ Confirmé : Pas d'API cyclone dédiée (404)" -ForegroundColor Green
    } else {
        Write-Host "Erreur: $($_.Exception.Message)"
    }
}
```

### Test 4 : Détection conditions cycloniques
```powershell
$data = Invoke-RestMethod -Uri "https://api.open-meteo.com/v1/forecast?latitude=-20.0&longitude=55.5&hourly=wind_speed_10m,pressure_msl&forecast_days=7"

$alertes = @()
for ($i = 0; $i -lt $data.hourly.time.Count; $i++) {
    $pressure = $data.hourly.pressure_msl[$i]
    $wind = $data.hourly.wind_speed_10m[$i]
    
    if ($pressure -lt 980 -and $wind -gt 117) {
        $alertes += [PSCustomObject]@{
            Time = $data.hourly.time[$i]
            Category = "CYCLONE TROPICAL"
            Wind = $wind
            Pressure = $pressure
        }
    }
    elseif ($pressure -lt 995 -and $wind -gt 88) {
        $alertes += [PSCustomObject]@{
            Time = $data.hourly.time[$i]
            Category = "TEMPÊTE TROPICALE"
            Wind = $wind
            Pressure = $pressure
        }
    }
}

Write-Host "`n=== DÉTECTION CYCLONIQUE ==="
if ($alertes.Count -gt 0) {
    Write-Host "⚠️ $($alertes.Count) alertes détectées sur 7 jours" -ForegroundColor Yellow
    $alertes | Select-Object -First 3 | Format-Table
} else {
    Write-Host "✅ Aucune condition cyclonique détectée sur 7 jours" -ForegroundColor Green
}
```

---

## 🎯 Exécution complète (copier-coller tout)

```powershell
Write-Host "==================================="
Write-Host "TEST COMPLET API OPEN-METEO"
Write-Host "==================================="

# Test 1 : Endpoint de base
Write-Host "`n[1/5] Test endpoint Weather Forecast..."
try {
    $test1 = Invoke-RestMethod -Uri "https://api.open-meteo.com/v1/forecast?latitude=-20.0&longitude=55.5&hourly=temperature_2m"
    Write-Host "✅ Weather Forecast : OK (200)" -ForegroundColor Green
} catch {
    Write-Host "❌ Weather Forecast : ERREUR" -ForegroundColor Red
}

# Test 2 : Variables cycloniques
Write-Host "`n[2/5] Test variables cycloniques..."
try {
    $test2 = Invoke-RestMethod -Uri "https://api.open-meteo.com/v1/forecast?latitude=-20.0&longitude=55.5&hourly=wind_speed_10m,wind_gusts_10m,pressure_msl"
    Write-Host "✅ Variables cycloniques : OK" -ForegroundColor Green
    Write-Host "   - Vent max: $([math]::Round(($test2.hourly.wind_speed_10m | Measure-Object -Maximum).Maximum, 1)) km/h"
    Write-Host "   - Pression min: $([math]::Round(($test2.hourly.pressure_msl | Measure-Object -Minimum).Minimum, 1)) hPa"
} catch {
    Write-Host "❌ Variables cycloniques : ERREUR" -ForegroundColor Red
}

# Test 3 : Marine API
Write-Host "`n[3/5] Test Marine API (SST)..."
try {
    $test3 = Invoke-RestMethod -Uri "https://marine-api.open-meteo.com/v1/marine?latitude=-20.0&longitude=55.5&hourly=sea_surface_temperature"
    $avgSST = ($test3.hourly.sea_surface_temperature | Measure-Object -Average).Average
    Write-Host "✅ Marine API : OK" -ForegroundColor Green
    Write-Host "   - SST moyenne: $([math]::Round($avgSST, 1))°C $(if ($avgSST -gt 26.5) {'⚠️ Favorable cyclone'} else {'✅'})"
} catch {
    Write-Host "❌ Marine API : ERREUR" -ForegroundColor Red
}

# Test 4 : API Tropical Cyclone (doit être 404)
Write-Host "`n[4/5] Test API Tropical Cyclone (doit être 404)..."
try {
    $test4 = Invoke-RestMethod -Uri "https://api.open-meteo.com/v1/tropical-cyclone?latitude=-20.0&longitude=55.5"
    Write-Host "⚠️ API cyclone existe (inattendu)" -ForegroundColor Yellow
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "✅ Confirmé : Pas d'API cyclone dédiée (404)" -ForegroundColor Green
    } else {
        Write-Host "❌ Erreur inattendue: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 5 : Modèle ECMWF
Write-Host "`n[5/5] Test modèle ECMWF..."
try {
    $test5 = Invoke-RestMethod -Uri "https://api.open-meteo.com/v1/forecast?latitude=-20.0&longitude=55.5&hourly=temperature_2m&models=ecmwf_ifs&forecast_days=10"
    $nbValues = $test5.hourly.time.Count
    Write-Host "✅ ECMWF IFS : OK ($nbValues timestamps)" -ForegroundColor Green
} catch {
    Write-Host "❌ ECMWF IFS : ERREUR" -ForegroundColor Red
}

Write-Host "`n==================================="
Write-Host "TESTS TERMINÉS"
Write-Host "==================================="
```

---

## 📋 Résumé des résultats attendus

| Test | Attendu | Signification |
|------|---------|---------------|
| Weather Forecast | ✅ 200 OK | API fonctionnelle |
| Variables cycloniques | ✅ Données présentes | Vents + pression disponibles |
| Marine SST | ✅ 20-32°C | Température surface océan |
| Tropical Cyclone | ❌ 404 | Confirme absence endpoint |
| ECMWF Model | ✅ ~240 timestamps | Modèle haute résolution OK |

---

## 🚨 Si vous avez toujours des erreurs

### Erreur 403 Forbidden
**Cause** : Vous utilisez un navigateur web au lieu de Postman/PowerShell
**Solution** : Utiliser les commandes PowerShell ci-dessus

### Erreur de réseau
**Cause** : Firewall ou proxy
**Solution** : Vérifier connexion internet, désactiver VPN temporairement

### Erreur SSL/TLS
**Cause** : Certificats non reconnus
**Solution** : 
```powershell
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
```

---

**Recommandation : Exécuter le script complet PowerShell pour valider toute l'API en 30 secondes !**
