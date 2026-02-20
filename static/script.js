// Load conditions when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadConditions();
    // Auto-refresh every 5 minutes
    setInterval(loadConditions, 5 * 60 * 1000);
});

async function loadConditions(forceRefresh = false) {
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const contentDiv = document.getElementById('content');
    const refreshBtn = document.getElementById('refresh-btn');
    
    // Show loading state
    loadingDiv.style.display = 'block';
    errorDiv.style.display = 'none';
    contentDiv.style.display = 'none';
    
    if (refreshBtn) {
        refreshBtn.disabled = true;
        refreshBtn.textContent = 'Refreshing...';
    }
    
    try {
        // Add force parameter if requested
        const url = forceRefresh ? '/api/conditions?force=true' : '/api/conditions';
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error('Failed to fetch conditions');
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        displayConditions(data);
        
        // Hide loading, show content
        loadingDiv.style.display = 'none';
        contentDiv.style.display = 'block';
        
    } catch (error) {
        console.error('Error loading conditions:', error);
        document.getElementById('error-message').textContent = 
            'Unable to load water safety conditions. Please try again later.';
        loadingDiv.style.display = 'none';
        errorDiv.style.display = 'block';
    } finally {
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.textContent = 'Refresh Now';
        }
    }
}

function displayConditions(data) {
    // Update timestamp
    const timestamp = new Date(data.timestamp);
    document.getElementById('timestamp').textContent = timestamp.toLocaleString();
    
    // Update cache age
    if (data.cache_age) {
        document.getElementById('cache-river').textContent = data.cache_age.river || 0;
        document.getElementById('cache-weather').textContent = data.cache_age.weather || 0;
    }
    
    // Update current measurements
    document.getElementById('river-flow-value').textContent = 
        `${data.data.river_flow.toFixed(2)} m³/s`;
    document.getElementById('wind-speed-value').textContent = 
        `${data.data.wind_speed.toFixed(1)} m/s`;
    document.getElementById('temperature-value').textContent = 
        `${data.data.temperature.toFixed(1)}°C`;
    
    // Update data sources
    document.getElementById('river-source').textContent = 
        `Environment Agency - ${formatDateTime(data.data.river_datetime)}`;
    document.getElementById('weather-source').textContent = 
        `University of Reading - ${data.data.weather_observation || 'Recent observation'}`;
    
    // Update Fours, Quads, Eights
    const foursConditions = data.conditions['Fours, Quads, Eights'];
    updateCategoryDisplay('fours', foursConditions);
    
    // Update Singles, Doubles, Pairs
    const singlesConditions = data.conditions['Singles, Doubles, Pairs'];
    updateCategoryDisplay('singles', singlesConditions);
}

function updateCategoryDisplay(categoryId, conditions) {
    // Update overall condition
    const overallElement = document.getElementById(`overall-${categoryId}`);
    const overallTextElement = document.getElementById(`overall-${categoryId}-text`);
    
    overallTextElement.textContent = conditions.overall;
    
    // Remove all condition classes
    overallElement.className = 'condition-badge';
    
    // Add appropriate class
    if (conditions.overall === 'NO ROWING') {
        overallElement.classList.add('no-rowing');
    } else {
        overallElement.classList.add(conditions.overall.toLowerCase());
    }
    
    // Update individual conditions
    updateConditionBadge(`river-${categoryId}`, conditions.river);
    updateConditionBadge(`wind-${categoryId}`, conditions.wind);
    updateConditionBadge(`temp-${categoryId}`, conditions.temperature);
}

function updateConditionBadge(elementId, condition) {
    const element = document.getElementById(elementId);
    element.textContent = condition;
    
    // Remove all condition classes
    element.className = 'condition-badge small';
    
    // Add appropriate class
    element.classList.add(condition.toLowerCase());
}

function formatDateTime(dateTimeString) {
    if (!dateTimeString) return 'Unknown';
    
    try {
        const date = new Date(dateTimeString);
        return date.toLocaleString('en-GB', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return dateTimeString;
    }
}
