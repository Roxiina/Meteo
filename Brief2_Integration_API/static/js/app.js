/**
 * Définition d'une localisation prédéfinie
 */
function setLocation(name, lat, lng) {
    document.getElementById('locationName').value = name;
    document.getElementById('latitude').value = lat;
    document.getElementById('longitude').value = lng;
}

/**
 * Détection des cyclones
 */
async function detectCyclone() {
    const locationName = document.getElementById('locationName').value.trim();
    const latitude = parseFloat(document.getElementById('latitude').value);
    const longitude = parseFloat(document.getElementById('longitude').value);
    
    // Validation des données
    if (!locationName || isNaN(latitude) || isNaN(longitude)) {
        showError('Veuillez remplir tous les champs avec des valeurs valides.');
        return;
    }
    
    if (latitude < -90 || latitude > 90) {
        showError('La latitude doit être comprise entre -90 et 90.');
        return;
    }
    
    if (longitude < -180 || longitude > 180) {
        showError('La longitude doit être comprise entre -180 et 180.');
        return;
    }
    
    // Affichage du loading
    showLoading();
    hideError();
    hideResult();
    
    try {
        const response = await fetch('/api/detect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                location_name: locationName,
                latitude: latitude,
                longitude: longitude
            })
        });
        
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        showResult(data);
        
    } catch (error) {
        console.error('Erreur lors de la détection:', error);
        showError(`Erreur lors de l'analyse: ${error.message}`);
    } finally {
        hideLoading();
    }
}

/**
 * Affichage du loading
 */
function showLoading() {
    const loadingDiv = document.getElementById('loading');
    if (loadingDiv) {
        loadingDiv.style.display = 'block';
    }
}

/**
 * Masquage du loading
 */
function hideLoading() {
    const loadingDiv = document.getElementById('loading');
    if (loadingDiv) {
        loadingDiv.style.display = 'none';
    }
}

/**
 * Affichage des résultats
 */
function showResult(apiResponse) {
    const resultDiv = document.getElementById('result');
    if (!resultDiv) return;
    
    // Extraire les données de la réponse API
    const result = apiResponse.data;
    const locationName = apiResponse.location_name;
    
    // Déterminer la couleur selon la sévérité
    let severityColor = '#22c55e'; // Vert par défaut
    let severityBg = 'rgba(34, 197, 94, 0.1)';
    if (result.severity_score > 0.7) {
        severityColor = '#ef4444';
        severityBg = 'rgba(239, 68, 68, 0.1)';
    } else if (result.severity_score > 0.4) {
        severityColor = '#f59e0b';
        severityBg = 'rgba(245, 158, 11, 0.1)';
    } else if (result.severity_score > 0.2) {
        severityColor = '#eab308';
        severityBg = 'rgba(234, 179, 8, 0.1)';
    }
    
    // Déterminer l'icône et le statut
    let icon = '<i class="fas fa-check-circle" style="color: #22c55e;"></i>';
    let statusText = result.category;
    
    if (result.category.toLowerCase().includes('cyclone')) {
        icon = '<i class="fas fa-hurricane" style="color: #ef4444;"></i>';
    } else if (result.category.toLowerCase().includes('tempête')) {
        icon = '<i class="fas fa-bolt" style="color: #f59e0b;"></i>';
    } else if (result.category.toLowerCase().includes('dépression')) {
        icon = '<i class="fas fa-cloud-rain" style="color: #6366f1;"></i>';
    }
    
    // Calculer les statistiques des conditions
    const conditions = result.conditions;
    const details = result.details;
    
    resultDiv.innerHTML = `
        <div class="result-header">
            <div class="result-icon">${icon}</div>
            <div class="result-title">
                <h2 style="color: ${severityColor}; margin: 0; font-size: 1.5rem; font-weight: 800;">
                    ${statusText}
                </h2>
                <p class="result-location">
                    <i class="fas fa-map-marker-alt" style="color: #64748b;"></i>
                    ${locationName}
                </p>
                <p class="result-coordinates">
                    ${result.location.latitude.toFixed(4)}, ${result.location.longitude.toFixed(4)}
                </p>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card temperature">
                <div class="metric-icon">
                    <i class="fas fa-thermometer-half"></i>
                </div>
                <div class="metric-content">
                    <span class="metric-label">Température SST</span>
                    <span class="metric-value">${conditions.sst ? conditions.sst.value.toFixed(1) + '°C' : 'N/A'}</span>
                </div>
                <div class="metric-status ${conditions.sst?.met ? 'status-success' : 'status-warning'}">
                    <i class="fas ${conditions.sst?.met ? 'fa-check' : 'fa-times'}"></i>
                </div>
            </div>
            
            <div class="metric-card pressure">
                <div class="metric-icon">
                    <i class="fas fa-tachometer-alt"></i>
                </div>
                <div class="metric-content">
                    <span class="metric-label">Pression</span>
                    <span class="metric-value">${conditions.pressure ? conditions.pressure.value.toFixed(1) + ' hPa' : 'N/A'}</span>
                </div>
                <div class="metric-status ${conditions.pressure?.met ? 'status-success' : 'status-warning'}">
                    <i class="fas ${conditions.pressure?.met ? 'fa-check' : 'fa-times'}"></i>
                </div>
            </div>
            
            <div class="metric-card wind">
                <div class="metric-icon">
                    <i class="fas fa-wind"></i>
                </div>
                <div class="metric-content">
                    <span class="metric-label">Vitesse du vent</span>
                    <span class="metric-value">${conditions.wind ? conditions.wind.value.toFixed(1) + ' km/h' : 'N/A'}</span>
                </div>
                <div class="metric-status ${conditions.wind?.met ? 'status-success' : 'status-warning'}">
                    <i class="fas ${conditions.wind?.met ? 'fa-check' : 'fa-times'}"></i>
                </div>
            </div>
            
            <div class="metric-card date">
                <div class="metric-icon">
                    <i class="fas fa-calendar-alt"></i>
                </div>
                <div class="metric-content">
                    <span class="metric-label">Date d'analyse</span>
                    <span class="metric-value">${details.analysis_date ? new Date(details.analysis_date).toLocaleDateString('fr-FR') : new Date().toLocaleDateString('fr-FR')}</span>
                </div>
                <div class="metric-status status-info">
                    <i class="fas fa-info"></i>
                </div>
            </div>
        </div>
        
        <div class="risk-assessment" style="background: ${severityBg}; border: 1px solid ${severityColor};">
            <div class="risk-header">
                <h3 style="margin: 0; color: ${severityColor}; font-size: 1.2rem; font-weight: 700;">
                    <i class="fas fa-exclamation-triangle" style="margin-right: 8px;"></i>
                    Niveau de risque
                </h3>
                <span class="risk-percentage" style="color: ${severityColor}; font-size: 2rem; font-weight: 800;">
                    ${Math.round(result.severity_score * 100)}%
                </span>
            </div>
            <div class="risk-bar-container">
                <div class="risk-bar-bg">
                    <div class="risk-bar-fill" style="background: linear-gradient(90deg, ${severityColor}, ${severityColor}80); width: ${result.severity_score * 100}%;"></div>
                </div>
            </div>
            <div class="risk-description">
                ${getRiskDescription(result.severity_score)}
            </div>
        </div>
    `;
    
    resultDiv.style.display = 'block';
    
    // Animation d'apparition des cartes métriques
    setTimeout(() => {
        const metricCards = document.querySelectorAll('.metric-card');
        metricCards.forEach((card, index) => {
            card.style.animation = `slideInUp 0.6s ease-out ${index * 0.1}s both`;
        });
    }, 100);
    
    // Scroll vers les résultats avec animation
    setTimeout(() => {
        resultDiv.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
        });
    }, 300);
}

/**
 * Obtenir la description du risque selon le score
 */
function getRiskDescription(score) {
    if (score > 0.7) return '<i class="fas fa-shield-alt"></i> Risque élevé - Surveillance renforcée recommandée';
    if (score > 0.4) return '<i class="fas fa-exclamation-circle"></i> Risque modéré - Vigilance nécessaire';
    if (score > 0.2) return '<i class="fas fa-info-circle"></i> Risque faible - Conditions à surveiller';
    return '<i class="fas fa-check-circle"></i> Conditions normales - Aucun risque détecté';
}

/**
 * Obtenir l'icône selon la sévérité
 */
function getSeverityIcon(severity_score) {
    if (severity_score > 0.7) return 'exclamation-triangle';
    if (severity_score > 0.4) return 'exclamation-circle';
    if (severity_score > 0.2) return 'info-circle';
    return 'check-circle';
}

/**
 * Masquage des résultats
 */
function hideResult() {
    const resultDiv = document.getElementById('result');
    if (resultDiv) {
        resultDiv.style.display = 'none';
    }
}

/**
 * Affichage des erreurs
 */
function showError(message) {
    const errorDiv = document.getElementById('error');
    if (!errorDiv) return;
    
    errorDiv.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <i class="fas fa-exclamation-triangle"></i>
            <strong>Erreur:</strong> ${message}
        </div>
    `;
    
    errorDiv.style.display = 'block';
    
    // Auto-hide après 5 secondes
    setTimeout(() => {
        errorDiv.style.opacity = '0';
        setTimeout(() => {
            errorDiv.style.display = 'none';
            errorDiv.style.opacity = '1';
        }, 500);
    }, 5000);
}

/**
 * Masquage des erreurs
 */
function hideError() {
    const errorDiv = document.getElementById('error');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

/**
 * Initialisation au chargement de la page
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM chargé');
    
    // Animation d'entrée du container
    const container = document.querySelector('.container');
    if (container) {
        container.style.opacity = '0';
        container.style.transform = 'scale(0.9) translateY(20px)';
        
        setTimeout(() => {
            container.style.transition = 'all 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
            container.style.opacity = '1';
            container.style.transform = 'scale(1) translateY(0)';
        }, 100);
    }
    
    // Gestion des touches Enter sur les inputs
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                detectCyclone();
            }
        });
    });
});