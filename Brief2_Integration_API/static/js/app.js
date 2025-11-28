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
    let severityColor = '#4bb543'; // Vert par défaut
    if (result.severity_score > 0.7) severityColor = '#ff6b6b';
    else if (result.severity_score > 0.4) severityColor = '#ffa500';
    else if (result.severity_score > 0.2) severityColor = '#ffff00';
    
    // Déterminer l'icône et le statut
    let icon = '<i class="fas fa-check-circle"></i>';
    let statusText = result.category;
    
    if (result.category.toLowerCase().includes('cyclone')) {
        icon = '<i class="fas fa-hurricane"></i>';
    } else if (result.category.toLowerCase().includes('tempête')) {
        icon = '<i class="fas fa-bolt"></i>';
    } else if (result.category.toLowerCase().includes('dépression')) {
        icon = '<i class="fas fa-cloud-rain"></i>';
    }
    
    // Calculer les statistiques des conditions
    const conditions = result.conditions;
    const details = result.details;
    
    resultDiv.innerHTML = `
        <div style="text-align: center; color: white;">
            <div class="icon">${icon}</div>
            <h2 style="color: ${severityColor}; margin-bottom: 1rem;">
                ${statusText}
            </h2>
            <div style="margin-bottom: 1rem;">
                <strong>Localisation:</strong> ${locationName}<br>
                <small>Coordonnées: ${result.location.latitude.toFixed(4)}, ${result.location.longitude.toFixed(4)}</small>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin: 1.5rem 0;">
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;">
                    <i class="fas fa-thermometer-half" style="color: #ff6b6b;"></i>
                    <strong>Température SST:</strong> ${conditions.sst ? conditions.sst.value.toFixed(1) + '°C' : 'N/A'}
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;">
                    <i class="fas fa-tachometer-alt" style="color: #4facfe;"></i>
                    <strong>Pression:</strong> ${conditions.pressure ? conditions.pressure.value.toFixed(1) + ' hPa' : 'N/A'}
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;">
                    <i class="fas fa-wind" style="color: #43e97b;"></i>
                    <strong>Vitesse du vent:</strong> ${conditions.wind ? conditions.wind.value.toFixed(1) + ' km/h' : 'N/A'}
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;">
                    <i class="fas fa-calendar-alt" style="color: #ffa500;"></i>
                    <strong>Date d'analyse:</strong> ${details.analysis_date ? new Date(details.analysis_date).toLocaleDateString('fr-FR') : new Date().toLocaleDateString('fr-FR')}
                </div>
            </div>
            
            <div style="background: rgba(${severityColor === '#ff6b6b' ? '255,107,107' : severityColor === '#ffa500' ? '255,165,0' : severityColor === '#ffff00' ? '255,255,0' : '75,181,67'},0.2); padding: 1.5rem; border-radius: 15px; border: 2px solid ${severityColor};">
                <h3 style="margin-bottom: 1rem;">Niveau de risque: ${Math.round(result.severity_score * 100)}%</h3>
                <div style="background: rgba(255,255,255,0.2); border-radius: 20px; height: 20px; overflow: hidden;">
                    <div style="background: ${severityColor}; height: 100%; width: ${result.severity_score * 100}%; border-radius: 20px; transition: width 1s ease;"></div>
                </div>
            </div>
            
            ${conditions ? `
            <div style="margin-top: 1.5rem; background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;">
                <h4>Conditions détaillées:</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.5rem; margin-top: 1rem; font-size: 0.9rem;">
                    ${conditions.sst ? `
                    <div>SST: ${conditions.sst.value.toFixed(1)}°C ${conditions.sst.met ? '✅' : '❌'}</div>
                    ` : ''}
                    ${conditions.pressure ? `
                    <div>Pression: ${conditions.pressure.value.toFixed(1)} hPa ${conditions.pressure.met ? '✅' : '❌'}</div>
                    ` : ''}
                    ${conditions.wind ? `
                    <div>Vent: ${conditions.wind.value.toFixed(1)} km/h ${conditions.wind.met ? '✅' : '❌'}</div>
                    ` : ''}
                </div>
            </div>
            ` : ''}
        </div>
    `;
    
    resultDiv.style.display = 'block';
    
    // Scroll vers les résultats avec animation
    setTimeout(() => {
        resultDiv.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
        });
    }, 100);
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