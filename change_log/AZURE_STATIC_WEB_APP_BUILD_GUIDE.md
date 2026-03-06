# Building RRC Water Safety as Azure Static Web App (Free Tier)

## Overview

Complete guide to building the Reading Rowing Club Water Safety application from scratch as an Azure Static Web App, optimized for the **free tier**.

**Target Architecture:** Static HTML/CSS/JS frontend + Azure Functions (Python) API + Azure Table Storage for caching

**Total Cost:** $0/month (free tier)

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Prerequisites](#prerequisites)
3. [Frontend Implementation](#frontend-implementation)
4. [Backend (Azure Functions) Implementation](#backend-implementation)
5. [Azure Table Storage Cache](#azure-table-storage-cache)
6. [Local Development](#local-development)
7. [Azure Deployment](#azure-deployment)
8. [Configuration](#configuration)
9. [Testing](#testing)
10. [Monitoring](#monitoring)

---

## Project Structure

```
rrc-water-safety-azure/
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── api/
│   ├── GetConditions/
│   │   ├── __init__.py
│   │   └── function.json
│   ├── requirements.txt
│   ├── host.json
│   └── local.settings.json
├── staticwebapp.config.json
├── .gitignore
└── README.md
```

---

## Prerequisites

### Install Required Tools

```bash
# Node.js (for Azure Static Web Apps CLI)
# Download from: https://nodejs.org/ (LTS version)

# Azure Functions Core Tools
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Azure Static Web Apps CLI
npm install -g @azure/static-web-apps-cli

# Python 3.11
# Download from: https://www.python.org/downloads/

# Git
# Download from: https://git-scm.com/
```

### Azure Account

1. Create free Azure account: https://azure.microsoft.com/free/
2. No credit card required for free tier services
3. Free tier includes:
   - Azure Static Web Apps (free tier)
   - Azure Functions (1M executions/month)
   - Azure Table Storage (25k operations/month)

---

## Frontend Implementation

### 1. index.html

Create `frontend/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reading Rowing Club - Water Safety</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Reading Rowing Club</h1>
            <h2>Water Safety Conditions</h2>
        </header>

        <!-- Top Safety Disclaimer -->
        <div class="safety-notice-top">
            <span class="notice-icon">⚠️</span>
            <div class="notice-content">
                <strong>Safety Reminder</strong><br>
                This tool assesses water conditions based on club safety rules, but you are responsible 
                for your own safety. Always use your judgment and consider your personal experience level. 
                If you're uncertain about conditions or your ability to row safely, consult your coach 
                or squad vice captain before going on the water.
            </div>
        </div>

        <!-- Loading State -->
        <div id="loading" class="loading">
            <p>Loading conditions...</p>
        </div>

        <!-- Error State -->
        <div id="error" class="error" style="display: none;">
            <p id="error-message"></p>
        </div>

        <!-- Main Content -->
        <div id="content" style="display: none;">
            <!-- Last Updated -->
            <div class="last-updated">
                <p>Last updated: <span id="timestamp"></span></p>
            </div>

            <!-- Current Measurements -->
            <div class="measurements">
                <div class="measurement">
                    <h3>River Flow</h3>
                    <div class="value" id="river-flow-value"></div>
                    <div class="source" id="river-source"></div>
                </div>
                <div class="measurement">
                    <h3>Wind Speed</h3>
                    <div class="value" id="wind-speed-value"></div>
                    <div class="source" id="weather-source"></div>
                </div>
                <div class="measurement">
                    <h3>Air Temperature</h3>
                    <div class="value" id="temperature-value"></div>
                </div>
            </div>

            <!-- Boat Categories -->
            <div class="categories">
                <!-- Fours, Quads, Eights -->
                <div class="category">
                    <h3>Fours, Quads, Eights</h3>
                    <div class="overall-condition">
                        <div class="condition-badge" id="overall-fours">
                            <span id="overall-fours-text"></span>
                        </div>
                        <div class="condition-guidance" id="guidance-fours"></div>
                    </div>
                    <div class="conditions-detail">
                        <div class="detail-item">
                            <span>River Flow:</span>
                            <span class="condition-badge small" id="river-fours"></span>
                        </div>
                        <div class="detail-item">
                            <span>Wind Speed:</span>
                            <span class="condition-badge small" id="wind-fours"></span>
                        </div>
                        <div class="detail-item">
                            <span>Temperature:</span>
                            <span class="condition-badge small" id="temp-fours"></span>
                        </div>
                    </div>
                </div>

                <!-- Singles, Doubles, Pairs -->
                <div class="category">
                    <h3>Singles, Doubles, Pairs</h3>
                    <div class="overall-condition">
                        <div class="condition-badge" id="overall-singles">
                            <span id="overall-singles-text"></span>
                        </div>
                        <div class="condition-guidance" id="guidance-singles"></div>
                    </div>
                    <div class="conditions-detail">
                        <div class="detail-item">
                            <span>River Flow:</span>
                            <span class="condition-badge small" id="river-singles"></span>
                        </div>
                        <div class="detail-item">
                            <span>Wind Speed:</span>
                            <span class="condition-badge small" id="wind-singles"></span>
                        </div>
                        <div class="detail-item">
                            <span>Temperature:</span>
                            <span class="condition-badge small" id="temp-singles"></span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Refresh Button -->
            <div class="refresh-info">
                <p>Data automatically refreshes every 15 minutes</p>
                <button id="refresh-btn" onclick="loadConditions(true)">Refresh Now</button>
            </div>

            <!-- Bottom Legal Disclaimer -->
            <div class="safety-disclaimer-bottom">
                <h4>IMPORTANT SAFETY DISCLAIMER</h4>
                <p>
                    The information provided by this application is for guidance purposes only and does not 
                    constitute professional safety advice. You must take personal responsibility for your safety 
                    on the water. This tool should be used in conjunction with your own assessment, experience, 
                    and judgment. If you are uncertain about water conditions or your ability to row safely, 
                    you must consult with your coach or squad vice captain before proceeding. The club and 
                    application developers accept no liability for incidents arising from use of this tool.
                </p>
            </div>
        </div>
    </div>

    <script src="js/app.js"></script>
</body>
</html>
```

### 2. CSS (frontend/css/style.css)

```css
/* Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    background: white;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    padding: 40px;
}

/* Header */
header {
    text-align: center;
    margin-bottom: 30px;
    border-bottom: 3px solid #667eea;
    padding-bottom: 20px;
}

header h1 {
    font-size: 2.5em;
    color: #667eea;
    margin-bottom: 10px;
}

header h2 {
    font-size: 1.2em;
    font-weight: 400;
    color: #666;
}

/* Safety Notice - Top */
.safety-notice-top {
    display: flex;
    align-items: flex-start;
    gap: 15px;
    background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
    border-left: 5px solid #ff9800;
    padding: 20px;
    margin: 20px 0;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(255, 152, 0, 0.2);
}

.safety-notice-top .notice-icon {
    font-size: 2em;
    line-height: 1;
    flex-shrink: 0;
}

.safety-notice-top .notice-content {
    flex: 1;
    color: #333;
    line-height: 1.6;
}

.safety-notice-top .notice-content strong {
    color: #d84315;
    font-size: 1.1em;
}

/* Loading and Error States */
.loading, .error {
    padding: 40px;
    text-align: center;
    font-size: 1.2em;
}

.error {
    color: #d32f2f;
    background: #ffebee;
    border-radius: 8px;
}

/* Last Updated */
.last-updated {
    text-align: center;
    color: #666;
    font-size: 0.9em;
    margin-bottom: 20px;
}

/* Measurements Grid */
.measurements {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.measurement {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
}

.measurement h3 {
    color: #667eea;
    margin-bottom: 10px;
    font-size: 1.1em;
}

.measurement .value {
    font-size: 2em;
    font-weight: bold;
    color: #333;
    margin: 10px 0;
}

.measurement .source {
    font-size: 0.85em;
    color: #666;
    margin-top: 10px;
}

.measurement .source a {
    color: #667eea;
    text-decoration: none;
}

.measurement .source a:hover {
    text-decoration: underline;
}

/* Categories */
.categories {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 30px;
    margin: 30px 0;
}

.category {
    background: #f8f9fa;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.category h3 {
    color: #667eea;
    font-size: 1.3em;
    margin-bottom: 20px;
    text-align: center;
}

/* Overall Condition */
.overall-condition {
    margin-bottom: 20px;
}

.condition-badge {
    padding: 15px 30px;
    border-radius: 8px;
    text-align: center;
    font-weight: bold;
    font-size: 1.5em;
    text-transform: uppercase;
    margin: 10px 0;
}

.condition-badge.small {
    padding: 5px 15px;
    font-size: 0.9em;
    display: inline-block;
}

/* Condition Colors */
.condition-badge.green {
    background: #4caf50;
    color: white;
}

.condition-badge.amber {
    background: #ff9800;
    color: white;
}

.condition-badge.red {
    background: #f44336;
    color: white;
}

.condition-badge.black {
    background: #212121;
    color: white;
}

.condition-badge.no-rowing {
    background: #d32f2f;
    color: white;
}

/* Condition Guidance */
.condition-guidance {
    margin-top: 15px;
    padding: 12px 20px;
    background: rgba(0, 0, 0, 0.05);
    border-radius: 6px;
    font-size: 1em;
    font-weight: 500;
    color: #333;
    line-height: 1.4;
}

/* Conditions Detail */
.conditions-detail {
    margin-top: 15px;
}

.detail-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #e0e0e0;
}

.detail-item:last-child {
    border-bottom: none;
}

/* Refresh Info */
.refresh-info {
    text-align: center;
    margin: 30px 0;
}

.refresh-info p {
    color: #666;
    margin-bottom: 15px;
}

.refresh-info button {
    background: #667eea;
    color: white;
    border: none;
    padding: 12px 30px;
    border-radius: 25px;
    font-size: 1em;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

.refresh-info button:hover {
    background: #764ba2;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.refresh-info button:disabled {
    background: #999;
    cursor: not-allowed;
}

/* Safety Disclaimer - Bottom */
.safety-disclaimer-bottom {
    margin-top: 40px;
    padding: 25px;
    background: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 0.85em;
    color: #555;
    line-height: 1.6;
}

.safety-disclaimer-bottom h4 {
    margin: 0 0 15px 0;
    font-size: 1.1em;
    color: #d32f2f;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.safety-disclaimer-bottom p {
    margin: 0;
    text-align: justify;
}

/* Responsive Design */
@media (max-width: 768px) {
    .container {
        padding: 20px;
    }

    header h1 {
        font-size: 1.8em;
    }

    .categories {
        grid-template-columns: 1fr;
    }

    .measurements {
        grid-template-columns: 1fr;
    }

    .condition-badge {
        font-size: 1.2em;
        padding: 12px 20px;
    }
}
```

### 3. JavaScript (frontend/js/app.js)

```javascript
// Configuration
const API_BASE_URL = '/api';
const REFRESH_INTERVAL = 5 * 60 * 1000; // 5 minutes

// Load conditions when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadConditions();
    // Auto-refresh every 5 minutes
    setInterval(loadConditions, REFRESH_INTERVAL);
});

/**
 * Load water safety conditions from API
 * @param {boolean} forceRefresh - Force fresh data from external APIs
 */
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
        // Build API URL
        let url = `${API_BASE_URL}/conditions`;
        if (forceRefresh) {
            url += '?force=true';
        }
        
        // Fetch conditions from API
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Display the conditions
        displayConditions(data);
        
        // Hide loading, show content
        loadingDiv.style.display = 'none';
        contentDiv.style.display = 'block';
        
    } catch (error) {
        console.error('Error loading conditions:', error);
        
        // Show error message
        document.getElementById('error-message').textContent = 
            `Unable to load water safety conditions: ${error.message}. Please try again later.`;
        loadingDiv.style.display = 'none';
        errorDiv.style.display = 'block';
    } finally {
        // Re-enable refresh button
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.textContent = 'Refresh Now';
        }
    }
}

/**
 * Display conditions data in the UI
 * @param {Object} data - Conditions data from API
 */
function displayConditions(data) {
    // Update timestamp
    const timestamp = new Date(data.timestamp);
    document.getElementById('timestamp').textContent = timestamp.toLocaleString();
    
    // Update current measurements
    document.getElementById('river-flow-value').textContent = 
        `${data.data.river_flow.toFixed(2)} m³/s`;
    document.getElementById('wind-speed-value').textContent = 
        `${data.data.wind_speed.toFixed(1)} m/s`;
    document.getElementById('temperature-value').textContent = 
        `${data.data.temperature.toFixed(1)}°C`;
    
    // Update data sources with links
    const riverDateTime = formatDateTime(data.data.river_datetime);
    document.getElementById('river-source').innerHTML = 
        `<a href="http://environment.data.gov.uk/flood-monitoring/id/measures/2200TH-flow--Mean-15_min-m3_s" target="_blank" rel="noopener noreferrer">Environment Agency</a> - ${riverDateTime}`;
    
    const weatherObs = data.data.weather_observation || 'Recent observation';
    document.getElementById('weather-source').innerHTML = 
        `<a href="https://www.met.reading.ac.uk/weatherdata/Reading_AWS_weather_report.html" target="_blank" rel="noopener noreferrer">University of Reading</a> - ${weatherObs}`;
    
    // Update Fours, Quads, Eights
    const foursConditions = data.conditions['Fours, Quads, Eights'];
    updateCategoryDisplay('fours', foursConditions);
    
    // Update Singles, Doubles, Pairs
    const singlesConditions = data.conditions['Singles, Doubles, Pairs'];
    updateCategoryDisplay('singles', singlesConditions);
}

/**
 * Update display for a boat category
 * @param {string} categoryId - Category identifier (fours/singles)
 * @param {Object} conditions - Conditions object for the category
 */
function updateCategoryDisplay(categoryId, conditions) {
    // Update overall condition
    const overallElement = document.getElementById(`overall-${categoryId}`);
    const overallTextElement = document.getElementById(`overall-${categoryId}-text`);
    const guidanceElement = document.getElementById(`guidance-${categoryId}`);
    
    overallTextElement.textContent = conditions.overall;
    
    // Remove all condition classes
    overallElement.className = 'condition-badge';
    
    // Add appropriate class
    if (conditions.overall === 'NO ROWING') {
        overallElement.classList.add('no-rowing');
    } else {
        overallElement.classList.add(conditions.overall.toLowerCase());
    }
    
    // Update guidance text
    if (guidanceElement && conditions.guidance) {
        guidanceElement.textContent = conditions.guidance;
    }
    
    // Update individual conditions
    updateConditionBadge(`river-${categoryId}`, conditions.river);
    updateConditionBadge(`wind-${categoryId}`, conditions.wind);
    updateConditionBadge(`temp-${categoryId}`, conditions.temperature);
}

/**
 * Update a condition badge with proper styling
 * @param {string} elementId - Element ID
 * @param {string} condition - Condition value (Green/Amber/Red/Black)
 */
function updateConditionBadge(elementId, condition) {
    const element = document.getElementById(elementId);
    element.textContent = condition;
    
    // Remove all condition classes
    element.className = 'condition-badge small';
    
    // Add appropriate class
    element.classList.add(condition.toLowerCase());
}

/**
 * Format datetime string for display
 * @param {string} dateTimeString - ISO datetime string
 * @returns {string} Formatted datetime
 */
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
```

---

## Backend (Azure Functions) Implementation

### 1. Function Configuration (api/host.json)

```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 20
      }
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  }
}
```

### 2. Function App Configuration (api/function.json)

Create `api/GetConditions/function.json`:

```json
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "authLevel": "anonymous",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["get"],
      "route": "conditions"
    },
    {
      "type": "http",
      "direction": "out",
      "name": "$return"
    }
  ]
}
```

### 3. Main Function Code (api/GetConditions/__init__.py)

```python
import azure.functions as func
import logging
import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
from typing import Dict, Optional

# Azure Table Storage (for caching)
from azure.data.tables import TableServiceClient, TableEntity
from azure.core.exceptions import ResourceNotFoundError

# Configuration
CACHE_EXPIRY_MINUTES = 15
RIVER_API_URL = "http://environment.data.gov.uk/flood-monitoring/id/measures/2200TH-flow--Mean-15_min-m3_s"
WEATHER_URL = "https://www.met.reading.ac.uk/weatherdata/Reading_AWS_weather_report.html"

# Azure Table Storage connection (from environment variable)
STORAGE_CONNECTION_STRING = os.getenv('AzureWebJobsStorage')


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function to get rowing conditions
    """
    logging.info('GetConditions function triggered')
    
    try:
        # Check for force refresh parameter
        force_refresh = req.params.get('force', 'false').lower() == 'true'
        
        if force_refresh:
            logging.info('Force refresh requested')
        
        # Get conditions (with caching)
        conditions_data = get_conditions(force_refresh)
        
        if not conditions_data:
            return func.HttpResponse(
                json.dumps({'error': 'Unable to fetch required data'}),
                status_code=503,
                mimetype="application/json",
                headers={'Access-Control-Allow-Origin': '*'}
            )
        
        # Return successful response
        return func.HttpResponse(
            json.dumps(conditions_data),
            status_code=200,
            mimetype="application/json",
            headers={'Access-Control-Allow-Origin': '*'}
        )
        
    except Exception as e:
        logging.error(f'Error in GetConditions: {str(e)}')
        return func.HttpResponse(
            json.dumps({'error': str(e)}),
            status_code=500,
            mimetype="application/json",
            headers={'Access-Control-Allow-Origin': '*'}
        )


def get_conditions(force_refresh: bool = False) -> Optional[Dict]:
    """Get rowing conditions with caching"""
    
    # Try to get from cache
    if not force_refresh:
        cached = get_from_cache('conditions')
        if cached and not is_cache_expired(cached.get('timestamp')):
            logging.info('Returning cached conditions')
            return cached
    
    logging.info('Fetching fresh data')
    
    # Fetch fresh data
    river_data = fetch_river_data()
    weather_data = fetch_weather_data()
    
    if not river_data or not weather_data:
        logging.error('Failed to fetch required data')
        return None
    
    # Calculate conditions
    conditions_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'data': {
            'river_flow': river_data['flow'],
            'river_datetime': river_data['dateTime'],
            'temperature': weather_data['temperature'],
            'wind_speed': weather_data['wind_gust'],
            'weather_observation': weather_data.get('observation_time', '')
        },
        'conditions': {}
    }
    
    # Calculate for both boat categories
    for category in ["Fours, Quads, Eights", "Singles, Doubles, Pairs"]:
        river_cond = get_river_condition(river_data['flow'], category)
        wind_cond = get_wind_condition(weather_data['wind_gust'], category)
        temp_cond = get_temperature_condition(weather_data['temperature'], category)
        overall_cond = calculate_overall_condition(river_cond, wind_cond, temp_cond)
        
        conditions_data['conditions'][category] = {
            'overall': overall_cond,
            'guidance': get_condition_guidance(overall_cond),
            'river': river_cond,
            'wind': wind_cond,
            'temperature': temp_cond
        }
    
    # Save to cache
    save_to_cache('conditions', conditions_data)
    
    return conditions_data


def fetch_river_data() -> Optional[Dict]:
    """Fetch river flow data from Environment Agency API"""
    try:
        logging.info(f'Fetching river data from {RIVER_API_URL}')
        response = requests.get(RIVER_API_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if 'items' in data:
            items = data['items']
            if isinstance(items, dict) and 'latestReading' in items:
                latest = items['latestReading']
                result = {
                    'flow': latest.get('value'),
                    'dateTime': latest.get('dateTime')
                }
                logging.info(f'Successfully fetched river data: flow={result["flow"]} m³/s')
                return result
        
        logging.warning('Unexpected API structure')
        return None
    except Exception as e:
        logging.error(f'Error fetching river data: {e}')
        return None


def fetch_weather_data() -> Optional[Dict]:
    """Fetch weather data from University of Reading"""
    try:
        logging.info(f'Fetching weather data from {WEATHER_URL}')
        response = requests.get(WEATHER_URL, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract observation timestamp from h2 tag
        observation_time = None
        h2_tag = soup.find('h2')
        if h2_tag:
            observation_time = h2_tag.get_text(strip=True)
        
        page_text = soup.get_text()
        
        # Extract temperature
        temp_pattern = r'Air temperature:\s*ºC\s*([-+]?\d+\.?\d*)'
        temp_match = re.search(temp_pattern, page_text)
        temperature = float(temp_match.group(1)) if temp_match else None
        
        # Extract wind gust
        wind_pattern = r'10-metre maximum 3-sec wind gust:\s*m/s\s*([-+]?\d+\.?\d*)'
        wind_match = re.search(wind_pattern, page_text)
        wind_gust = float(wind_match.group(1)) if wind_match else None
        
        if temperature is not None and wind_gust is not None:
            result = {
                'temperature': temperature,
                'wind_gust': wind_gust,
                'observation_time': observation_time
            }
            logging.info(f'Successfully fetched weather data: temp={temperature}°C, wind={wind_gust} m/s')
            return result
        
        logging.warning('Failed to parse weather data')
        return None
    except Exception as e:
        logging.error(f'Error fetching weather data: {e}')
        return None


# Safety condition calculation functions
def get_river_condition(flow: float, boat_category: str) -> str:
    """Determine river flow condition based on rules"""
    if boat_category == "Fours, Quads, Eights":
        if flow >= 120: return "Black"
        elif flow >= 100: return "Red"
        elif flow >= 75: return "Amber"
        else: return "Green"
    else:  # Singles, Doubles, Pairs
        if flow >= 100: return "Black"
        elif flow >= 75: return "Red"
        elif flow >= 50: return "Amber"
        else: return "Green"


def get_wind_condition(wind_speed: float, boat_category: str) -> str:
    """Determine wind condition based on rules"""
    if boat_category == "Fours, Quads, Eights":
        if wind_speed >= 15.6: return "Black"
        elif wind_speed >= 13.6: return "Red"
        elif wind_speed >= 11.3: return "Amber"
        else: return "Green"
    else:  # Singles, Doubles, Pairs
        if wind_speed >= 13.6: return "Black"
        elif wind_speed >= 11.3: return "Red"
        elif wind_speed >= 9.0: return "Amber"
        else: return "Green"


def get_temperature_condition(temperature: float, boat_category: str) -> str:
    """Determine temperature condition based on rules"""
    if boat_category == "Fours, Quads, Eights":
        if temperature <= -3.0: return "Black"
        elif temperature <= 2.9: return "Red"
        elif temperature <= 6.9: return "Amber"
        else: return "Green"
    else:  # Singles, Doubles, Pairs
        if temperature <= 0.0: return "Black"
        elif temperature <= 4.9: return "Red"
        elif temperature <= 8.9: return "Amber"
        else: return "Green"


def calculate_overall_condition(river_cond: str, wind_cond: str, temp_cond: str) -> str:
    """Calculate overall rowing condition"""
    conditions = [river_cond, wind_cond, temp_cond]
    black_count = conditions.count("Black")
    red_count = conditions.count("Red")
    
    if black_count >= 1 or red_count >= 2:
        return "NO ROWING"
    
    severity_order = ["Green", "Amber", "Red", "Black"]
    most_severe = "Green"
    
    for condition in conditions:
        if severity_order.index(condition) > severity_order.index(most_severe):
            most_severe = condition
    
    return most_severe


def get_condition_guidance(condition: str) -> str:
    """Get guidance text for a condition"""
    guidance = {
        "NO ROWING": "No Rowing",
        "Black": "No Rowing",
        "Red": "Dangerously high flow. See Club rules for limited exceptions.",
        "Amber": "No novice coxes or steerpersons.",
        "Green": "No Restrictions."
    }
    return guidance.get(condition, "Unknown condition")


# Cache functions using Azure Table Storage
def get_from_cache(key: str) -> Optional[Dict]:
    """Get data from Azure Table Storage cache"""
    if not STORAGE_CONNECTION_STRING:
        logging.warning('No storage connection string configured')
        return None
    
    try:
        table_service = TableServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
        table_client = table_service.get_table_client('cache')
        
        # Get entity
        entity = table_client.get_entity(partition_key='cache', row_key=key)
        
        # Deserialize JSON data
        return json.loads(entity['data'])
    except ResourceNotFoundError:
        logging.info(f'Cache miss for key: {key}')
        return None
    except Exception as e:
        logging.error(f'Error reading from cache: {e}')
        return None


def save_to_cache(key: str, data: Dict) -> bool:
    """Save data to Azure Table Storage cache"""
    if not STORAGE_CONNECTION_STRING:
        logging.warning('No storage connection string configured')
        return False
    
    try:
        table_service = TableServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
        table_client = table_service.get_table_client('cache')
        
        # Create table if it doesn't exist
        table_service.create_table_if_not_exists('cache')
        
        # Create entity
        entity = {
            'PartitionKey': 'cache',
            'RowKey': key,
            'data': json.dumps(data),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Upsert entity
        table_client.upsert_entity(entity)
        logging.info(f'Saved to cache: {key}')
        return True
    except Exception as e:
        logging.error(f'Error saving to cache: {e}')
        return False


def is_cache_expired(timestamp_str: Optional[str]) -> bool:
    """Check if cached data is expired"""
    if not timestamp_str:
        return True
    
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        age = datetime.utcnow() - timestamp
        is_expired = age > timedelta(minutes=CACHE_EXPIRY_MINUTES)
        logging.info(f'Cache age: {age.seconds // 60} minutes, expired: {is_expired}')
        return is_expired
    except Exception as e:
        logging.error(f'Error checking cache expiry: {e}')
        return True
```

### 4. Requirements (api/requirements.txt)

```txt
azure-functions
requests==2.32.5
beautifulsoup4==4.14.3
azure-data-tables==12.5.0
```

### 5. Local Settings (api/local.settings.json)

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}
```

---

## Azure Table Storage Cache

No separate implementation needed - handled in the Azure Function code above using `azure-data-tables` library.

**Key Points:**
- Free tier: 25,000 operations/month
- Low latency (~10-20ms)
- Serverless-native
- Automatically created on first use
- Simple key-value storage

---

## Static Web App Configuration

Create `staticwebapp.config.json` in project root:

```json
{
  "routes": [
    {
      "route": "/api/*",
      "allowedRoles": ["anonymous"]
    },
    {
      "route": "/*",
      "serve": "/index.html",
      "statusCode": 200
    }
  ],
  "navigationFallback": {
    "rewrite": "/index.html",
    "exclude": ["/images/*.{png,jpg,gif}", "/css/*", "/js/*", "/api/*"]
  },
  "responseOverrides": {
    "404": {
      "rewrite": "/index.html",
      "statusCode": 200
    }
  },
  "globalHeaders": {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: https:;"
  }
}
```

---

## Local Development

### 1. Start Azure Functions Locally

```bash
# Navigate to api folder
cd api

# Install Python dependencies
pip install -r requirements.txt

# Start Azure Functions runtime
func start
```

Functions will run on `http://localhost:7071`

### 2. Start Static Web Apps CLI

```bash
# In project root (separate terminal)
swa start frontend --api-location api --api-devserver-url http://localhost:7071
```

Application will be available at `http://localhost:4280`

### 3. Testing

Open browser to `http://localhost:4280`

**Note:** Azure Table Storage emulator (Azurite) recommended for local development:

```bash
# Install Azurite
npm install -g azurite

# Start Azurite
azurite --silent --location ./azurite --debug ./azurite/debug.log
```

---

## Azure Deployment

### Option 1: Azure Portal (Easiest)

1. **Go to Azure Portal:** https://portal.azure.com
2. **Create Resource** → Search "Static Web Apps"
3. **Click "Create"**
4. **Configure:**
   - Subscription: Your subscription
   - Resource Group: Create new "rrc-water-safety-rg"
   - Name: "rrc-water-safety"
   - Plan: **Free tier**
   - Region: Choose closest
   - Deployment: GitHub
   - Organization: Your GitHub account
   - Repository: Your repo
   - Branch: main
5. **Build Details:**
   - Build Presets: Custom
   - App location: `/frontend`
   - Api location: `/api`
   - Output location: (leave empty)
6. **Review + Create**

Azure will:
- Create GitHub Actions workflow automatically
- Deploy on every push to main
- Provide URL: `https://your-app.azurestaticapps.net`

### Option 2: GitHub Actions (Manual)

Create `.github/workflows/azure-static-web-apps.yml`:

```yaml
name: Azure Static Web Apps CI/CD

on:
  push:
    branches:
      - main
  pull_request:
    types: [opened, synchronize, reopened, closed]
    branches:
      - main

jobs:
  build_and_deploy_job:
    if: github.event_name == 'push' || (github.event_name == 'pull_request' && github.event.action != 'closed')
    runs-on: ubuntu-latest
    name: Build and Deploy Job
    steps:
      - uses: actions/checkout@v3
        with:
          submodules: true
      - name: Build And Deploy
        id: builddeploy
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: "upload"
          app_location: "/frontend"
          api_location: "/api"
          output_location: ""

  close_pull_request_job:
    if: github.event_name == 'pull_request' && github.event.action == 'closed'
    runs-on: ubuntu-latest
    name: Close Pull Request Job
    steps:
      - name: Close Pull Request
        id: closepullrequest
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          action: "close"
```

Add `AZURE_STATIC_WEB_APPS_API_TOKEN` to GitHub Secrets (from Azure Portal).

### Option 3: Azure CLI

```bash
# Login
az login

# Create resource group
az group create --name rrc-water-safety-rg --location eastus

# Create static web app
az staticwebapp create \
  --name rrc-water-safety \
  --resource-group rrc-water-safety-rg \
  --source https://github.com/yourusername/your-repo \
  --location "East US 2" \
  --branch main \
  --app-location "/frontend" \
  --api-location "/api" \
  --login-with-github
```

---

## Configuration

### Environment Variables

Set in Azure Portal:
1. Go to Static Web App resource
2. **Configuration** → **Application settings**
3. Add setting: `AzureWebJobsStorage` (auto-configured)

No additional configuration needed for free tier.

### CORS

Handled automatically by Azure Static Web Apps.

### Custom Domain (Optional, but requires paid tier)

Free tier uses: `https://your-app.azurestaticapps.net`

For custom domain, upgrade to Standard tier ($9/month).

---

## Testing

### Local Testing

```bash
# Start application
swa start frontend --api-location api --api-devserver-url http://localhost:7071

# Open browser
open http://localhost:4280
```

### Production Testing

After deployment:

```bash
# Test API endpoint
curl https://your-app.azurestaticapps.net/api/conditions

# Test force refresh
curl "https://your-app.azurestaticapps.net/api/conditions?force=true"

# Check response
# Should return JSON with conditions data
```

### Automated Testing

Create `tests/test_api.py`:

```python
import requests
import json

def test_api_conditions():
    """Test conditions API endpoint"""
    response = requests.get('https://your-app.azurestaticapps.net/api/conditions')
    assert response.status_code == 200
    
    data = response.json()
    assert 'timestamp' in data
    assert 'data' in data
    assert 'conditions' in data
    assert 'Fours, Quads, Eights' in data['conditions']
    assert 'Singles, Doubles, Pairs' in data['conditions']

def test_force_refresh():
    """Test force refresh parameter"""
    response = requests.get('https://your-app.azurestaticapps.net/api/conditions?force=true')
    assert response.status_code == 200

if __name__ == '__main__':
    test_api_conditions()
    test_force_refresh()
    print("All tests passed!")
```

---

## Monitoring

### Application Insights (Free tier included)

1. **Azure Portal** → Your Static Web App → **Application Insights**
2. **Enable** Application Insights (free tier)
3. **View:**
   - Request counts
   - Response times
   - Failure rates
   - API performance

### Logs

**Via Azure Portal:**
1. Static Web App → **Functions** → **Function logs**
2. View real-time logs

**Via CLI:**
```bash
az staticwebapp logs show \
  --name rrc-water-safety \
  --resource-group rrc-water-safety-rg
```

### Alerts (Optional, requires configuration)

Set up alerts for:
- Function failures
- High response times
- API errors

---

## Cost Analysis (Free Tier)

### What's Included (Free)

| Service | Free Tier Allowance | Your Usage | Status |
|---------|-------------------|------------|--------|
| **Static Web Apps** | 100 GB bandwidth/month | ~1-5 GB | ✅ FREE |
| **Azure Functions** | 1M executions/month | ~20k-50k | ✅ FREE |
| **Table Storage** | 25k operations/month | ~5k-10k | ✅ FREE |
| **Application Insights** | 5 GB/month | ~100 MB | ✅ FREE |

**Total Monthly Cost:** **$0.00** 🎉

### Usage Estimates

Assuming 1,000 visitors/month:
- **Static page views:** 1,000 (included)
- **API calls:** ~1,000-5,000 (auto-refresh every 5 min)
- **Cache operations:** ~2,000-10,000 (read/write)
- **Bandwidth:** ~500 MB - 2 GB

All well within free tier limits! ✅

### When You'd Need to Upgrade

**Standard Tier ($9/month) needed for:**
- Custom domains
- No cold starts (always warm functions)
- More bandwidth (>100 GB/month)
- More function executions (>1M/month)

For Reading Rowing Club: **Free tier is perfect** ✅

---

## Limitations & Workarounds

### Cold Starts

**Problem:** Functions may take 2-5 seconds on first request after inactivity

**Workarounds:**
1. **Accept it** - Free tier limitation
2. **Loading indicator** - Already implemented in UI
3. **Schedule pings** - Create timer function to keep warm (uses executions)
4. **Upgrade** - Standard tier ($9/month) eliminates cold starts

**Recommendation:** Accept it. 2-5 seconds occasionally is acceptable for free hosting.

### Cache Consistency

**Problem:** Multiple function instances may have different cache states

**Solution:** Using Azure Table Storage (shared cache) solves this ✅

### Execution Time

**Limit:** 10 minutes per function execution (free tier)

**Your app:** <30 seconds typical ✅

No issue for this application.

---

## Troubleshooting

### Common Issues

#### 1. "CORS error" in browser

**Solution:** Check CORS headers in function:
```python
headers={'Access-Control-Allow-Origin': '*'}
```

#### 2. "Cold start taking forever"

**Solution:** Wait 30-60 seconds on first request after inactivity. Subsequent requests will be fast.

#### 3. "Cache not working"

**Solution:** Check Azure Table Storage connection string:
```bash
# In Azure Portal
Static Web App → Configuration → Application settings
# Verify AzureWebJobsStorage is set
```

#### 4. "Function not found"

**Solution:** Check `function.json` route configuration:
```json
"route": "conditions"
```

#### 5. "External APIs timing out"

**Solution:** Increase timeout in function:
```python
response = requests.get(url, timeout=30)  # Increase from 10 to 30
```

### Debug Logs

```bash
# View function logs in real-time
func azure functionapp fetch-app-settings <app-name>
func azure functionapp logstream <app-name>
```

---

## Comparison: Flask Docker vs Azure Static Web App

| Aspect | Flask/Docker (Current) | Azure Static Web App (Free) |
|--------|----------------------|----------------------------|
| **Cost** | $0 (Fly.io) | $0 (Azure) |
| **Cold Starts** | None | 2-5 seconds |
| **Architecture** | Monolithic | Separated (static + API) |
| **Cache** | In-memory | Azure Table Storage |
| **Deployment** | Docker container | Static files + Functions |
| **Complexity** | Low (single container) | Medium (multiple services) |
| **Scalability** | Manual | Automatic |
| **Response Time** | Fast (~50-100ms) | Good (~100-300ms after warm) |
| **Setup Time** | 2 hours | 4-6 hours |
| **Maintenance** | Low | Medium |
| **Learning Curve** | Easy (standard Flask) | Medium (Azure-specific) |

### When to Choose Azure Static Web App

✅ **Choose Azure if:**
- Organization requires Azure
- Learning Azure ecosystem
- Need Azure AD integration
- Building larger microservices app
- Want automatic scaling

✅ **Choose Flask/Docker if:**
- Want simplest solution
- Cost is critical ($0 with no catches)
- Prefer monolithic architecture
- Don't need Azure-specific features
- Want faster response times

---

## Next Steps

1. **Create project structure** following layout above
2. **Implement frontend** (HTML/CSS/JS)
3. **Implement Azure Function** (Python)
4. **Test locally** with SWA CLI
5. **Create Azure resources** via Portal
6. **Deploy via GitHub Actions**
7. **Test production deployment**
8. **Set up monitoring** in Application Insights

---

## Summary

### What You Get (Free Tier)

✅ **Fully functional water safety app**
✅ **Global CDN distribution**
✅ **Automatic HTTPS**
✅ **Serverless API** (Azure Functions)
✅ **Shared cache** (Azure Table Storage)
✅ **Automatic scaling**
✅ **CI/CD via GitHub Actions**
✅ **Application monitoring**
✅ **Zero monthly cost**

### Trade-offs vs Current Solution

✅ **Pros:**
- Learn Azure ecosystem
- Automatic scaling
- Azure integration
- Enterprise ready

❌ **Cons:**
- Cold starts (2-5 sec)
- More complex setup
- Separated architecture
- More services to manage

### Effort Required

- **Initial development:** 6-10 hours
- **Testing & debugging:** 2-4 hours
- **Documentation:** 1-2 hours
- **Total:** 10-16 hours

### Final Recommendation

**For learning Azure:** ✅ Great project
**For production use:** 🟡 Consider if Azure is required
**For simplicity:** ❌ Flask/Docker is simpler

---

**Document Status:** ✅ **Complete Build Guide**
**Target Platform:** Azure Static Web Apps (Free Tier)
**Estimated Build Time:** 10-16 hours
**Monthly Cost:** $0.00
**Date:** March 4, 2026
