# Schéma de Flux d'Intégration - API Open-Meteo Cyclones

## 🔄 Schémas Simplifiés pour le Suivi Cyclonique

Ce document présente les flux d'intégration de manière simple et claire.

---

## 1. Vue d'Ensemble Simple - Comment ça marche ?

```mermaid
graph LR
    A[👤 Utilisateur] --> B[🌐 Application Web]
    B --> C[🔄 Système]
    C --> D[☁️ Open-Meteo API]
    D --> C
    C --> E[💾 Base de Données]
    C --> B
    B --> A
    C --> F[📧 Alertes]
    F --> A
    
    style D fill:#e1f5ff
    style C fill:#fff3e0
    style F fill:#ffebee
```

**Explication** : L'utilisateur demande les cyclones → Le système appelle Open-Meteo → Les données sont analysées → Résultats affichés + alertes envoyées si cyclone détecté.

---

## 2. Flux Simple - De la Requête à la Réponse

```mermaid
sequenceDiagram
    participant U as 👤 Utilisateur
    participant A as 🌐 Application
    participant O as ☁️ Open-Meteo
    participant D as 💾 Base de Données
    
    U->>A: Je veux voir les cyclones
    A->>O: Demande météo (lat, lon)
    O->>A: Données: vent, pression, SST
    A->>A: Analyse: Cyclone détecté ?
    A->>D: Sauvegarde résultat
    A->>U: Affiche: CYCLONE DÉTECTÉ ⚠️
    A->>U: Envoie alerte par email 📧
```

**Temps total** : ~3 secondes

---

## 3. Détection de Cyclone - Algorithme Simple

```mermaid
flowchart TD
    Start([🌊 Nouvelle Donnée]) --> SST{SST > 26.5°C ?}
    
    SST -->|❌ Non| Safe[✅ PAS DE RISQUE]
    SST -->|✅ Oui| Pressure{Pression < 980 hPa ?}
    
    Pressure -->|❌ Non| Check[🔍 Surveiller]
    Pressure -->|✅ Oui| Wind{Vent > 117 km/h ?}
    
    Wind -->|❌ Non| Tempete[🟡 TEMPÊTE]
    Wind -->|✅ Oui| Cyclone[🔴 CYCLONE]
    
    Cyclone --> Alert[📢 ALERTE URGENTE]
    Tempete --> Notify[📧 Notification]
    
    style Cyclone fill:#ffcdd2
    style Tempete fill:#fff9c4
    style Safe fill:#c8e6c9
```

**Critères** :
- 🌡️ SST > 26.5°C
- 📉 Pression < 980 hPa  
- 💨 Vent > 117 km/h
= **🔴 CYCLONE**

---

## 4. Les 3 APIs Open-Meteo Utilisées

```mermaid
graph TB
    System[🔄 Système de Détection]
    
    System --> API1[☁️ Weather API<br/>Vent + Pression]
    System --> API2[🌊 Marine API<br/>Température Mer]
    System --> API3[📊 Ensemble API<br/>Incertitudes]
    
    API1 --> Result[📊 Résultat Final]
    API2 --> Result
    API3 --> Result
    
    style API1 fill:#e1f5ff
    style API2 fill:#e1f5ff
    style API3 fill:#e1f5ff
    style Result fill:#c8e6c9
```

**3 sources de données** combinées pour détecter les cyclones.

---

## 5. Gestion du Cache - Éviter les Appels Inutiles

```mermaid
graph TD
    Request[📥 Nouvelle Requête] --> Check{Données en<br/>cache ?}
    
    Check -->|✅ Oui| Fast[⚡ Réponse Rapide<br/>< 1 seconde]
    Check -->|❌ Non| Call[☁️ Appeler Open-Meteo<br/>~3 secondes]
    
    Call --> Save[💾 Sauvegarder<br/>Valide 6 heures]
    Save --> Response[📤 Retourner Résultat]
    Fast --> Response
    
    style Fast fill:#c8e6c9
    style Call fill:#e1f5ff
```

**Cache = 6 heures** : Les données météo ne changent que toutes les 6h.

---

## 6. Système d'Alertes - 3 Niveaux

```mermaid
graph LR
    Detection[🔍 Détection] --> Level{Niveau<br/>Risque ?}
    
    Level -->|🔴 ÉLEVÉ| Critical[CYCLONE<br/>Email + SMS + Push]
    Level -->|🟡 MOYEN| Warning[TEMPÊTE<br/>Email + Push]
    Level -->|🟢 FAIBLE| Info[SURVEILLANCE<br/>Email seulement]
    
    Critical --> Users[👥 Utilisateurs]
    Warning --> Users
    Info --> Users
    
    style Critical fill:#ffcdd2
    style Warning fill:#fff9c4
    style Info fill:#c8e6c9
```

**Plus le risque est élevé, plus on envoie d'alertes.**

---

## 7. Que Faire si Open-Meteo ne Répond Pas ?

```mermaid
flowchart TD
    Call[☁️ Appel API] --> Response{Réponse ?}
    
    Response -->|✅ OK| Success[📊 Données Reçues]
    Response -->|❌ Erreur| Retry[🔄 Réessayer<br/>3 fois]
    
    Retry --> Check{Succès ?}
    Check -->|✅ Oui| Success
    Check -->|❌ Non| Cache{Cache<br/>disponible ?}
    
    Cache -->|✅ Oui| OldData[📦 Données Anciennes<br/>avec Avertissement]
    Cache -->|❌ Non| Error[❌ Erreur 503<br/>Service Indisponible]
    
    style Success fill:#c8e6c9
    style OldData fill:#fff9c4
    style Error fill:#ffcdd2
```

**Stratégie** : Retry 3× → Cache ancien → Erreur seulement si tout échoue.

---

## 8. Construction d'une Requête API - Étape par Étape

```mermaid
graph LR
    A[📍 Position<br/>lat=-20<br/>lon=55] --> B[➕ Variables<br/>vent<br/>pression<br/>SST]
    B --> C[➕ Config<br/>10 jours<br/>horaire]
    C --> D[🔗 URL Complète]
    D --> E[📡 Envoi HTTP GET]
    E --> F[📥 Réception JSON]
    
    style D fill:#e1f5ff
    style F fill:#c8e6c9
```

**Exemple URL** :  
`api.open-meteo.com/v1/forecast?latitude=-20&longitude=55&hourly=wind_speed_10m,pressure_msl`

---

## 9. Workflow Complet - Vue Simplifiée

```mermaid
graph TB
    subgraph "1️⃣ ENTRÉE"
        User[👤 Utilisateur]
    end
    
    subgraph "2️⃣ RÉCUPÉRATION"
        API[☁️ Open-Meteo<br/>3 APIs]
    end
    
    subgraph "3️⃣ ANALYSE"
        Algo[🤖 Algorithme<br/>Détection]
    end
    
    subgraph "4️⃣ STOCKAGE"
        DB[💾 Base de Données]
    end
    
    subgraph "5️⃣ SORTIE"
        Display[🖥️ Affichage]
        Alert[📧 Alertes]
    end
    
    User --> API
    API --> Algo
    Algo --> DB
    DB --> Display
    Algo --> Alert
    Display --> User
    Alert --> User
    
    style API fill:#e1f5ff
    style Algo fill:#fff3e0
    style Alert fill:#ffebee
```

**5 étapes simples** : Entrée → API → Analyse → Stockage → Sortie

---

## 10. Monitoring Simple - Surveiller le Système

```mermaid
graph TB
    subgraph "📊 Ce qu'on Surveille"
        M1[⏱️ Temps de Réponse<br/>< 5 secondes]
        M2[❌ Taux d'Erreur<br/>< 1%]
        M3[📈 Nombre Requêtes<br/>par jour]
    end
    
    subgraph "🔔 Alertes Automatiques"
        A1[Si lent → Email équipe]
        A2[Si erreurs → SMS urgence]
        A3[Si surchauffe → Alerte]
    end
    
    M1 --> A1
    M2 --> A2
    M3 --> A3
    
    style M1 fill:#e1f5ff
    style M2 fill:#e1f5ff
    style M3 fill:#e1f5ff
    style A1 fill:#ffebee
    style A2 fill:#ffebee
    style A3 fill:#ffebee
```

**On surveille** : vitesse, erreurs, charge → alertes automatiques si problème.

---

## 📋 Tableau Récapitulatif Simple

| Élément | Valeur | Explication |
|---------|--------|-------------|
| **Temps de réponse** | 2-4 secondes | Temps pour détecter un cyclone |
| **Cache** | 6 heures | Données valides pendant 6h |
| **Retry** | 3 tentatives | On réessaye 3× si erreur |
| **APIs utilisées** | 3 APIs | Weather + Marine + Ensemble |
| **Niveaux d'alerte** | 3 niveaux | Élevé, Moyen, Faible |

---

## 🎯 Points Clés à Retenir

### ✅ Ce qui est Simple
- **1 requête** → 3 APIs appelées en parallèle
- **Cache intelligent** → Réponse rapide si données récentes
- **3 tentatives** → Le système réessaye si erreur
- **3 niveaux d'alerte** → Plus c'est grave, plus on alerte

### ⚠️ Ce qui est Important
- Les données météo sont **mises à jour toutes les 6 heures**
- Le système **analyse automatiquement** les conditions cycloniques
- Les alertes sont **envoyées automatiquement** si cyclone détecté
- Le **cache permet d'économiser** des appels API

### 🔄 Le Cycle Complet
1. **Utilisateur** demande info cyclone
2. **Système** vérifie le cache
3. Si pas de cache → **Appel Open-Meteo**
4. **Analyse** des données reçues
5. **Détection** cyclone si critères remplis
6. **Sauvegarde** en base de données
7. **Alerte** envoyée si nécessaire
8. **Affichage** résultat à l'utilisateur

---

## 🚀 Comment Utiliser ces Schémas ?

### Pour Comprendre
- **Schéma 1** : Vue générale du système
- **Schéma 2** : Ordre des événements
- **Schéma 3** : Comment on détecte un cyclone
- **Schéma 5** : Comment on accélère avec le cache
- **Schéma 7** : Comment on gère les erreurs

### Pour Développer
- **Schéma 4** : Quelles APIs appeler
- **Schéma 8** : Comment construire une requête
- **Schéma 9** : Les 5 étapes de développement

### Pour Surveiller
- **Schéma 10** : Ce qu'il faut monitorer

---

## 📝 Glossaire Simple

| Terme | Explication Simple |
|-------|-------------------|
| **API** | Interface pour récupérer des données météo |
| **Cache** | Mémoire temporaire pour accélérer |
| **SST** | Température de l'eau de mer |
| **Retry** | Réessayer quand ça échoue |
| **Webhook** | Notification automatique vers autre système |
| **JSON** | Format de données structuré |
| **HTTP GET** | Demander des données à une API |

---

**Document simplifié - Créé le 24/11/2025**  
**Basé sur l'API Open-Meteo pour le suivi cyclonique dans l'Océan Indien**
