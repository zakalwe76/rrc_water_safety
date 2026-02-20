from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import logging
import os
from typing import Dict, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Cache storage
cache = {
    'river_data': None,
    'river_timestamp': None,
    'weather_data': None,
    'weather_timestamp': None
}

# Constants
CACHE_EXPIRY_MINUTES = 15
RIVER_API_URL = "http://environment.data.gov.uk/flood-monitoring/id/measures/2200TH-flow--Mean-15_min-m3_s"
WEATHER_URL = "https://www.met.reading.ac.uk/weatherdata/Reading_AWS_weather_report.html"
DEMO_MODE = os.getenv('DEMO_MODE', 'false').lower() == 'true'


def is_cache_expired(timestamp: Optional[datetime]) -> bool:
    """Check if cached data is older than CACHE_EXPIRY_MINUTES"""
    if timestamp is None:
        return True
    return datetime.now() - timestamp > timedelta(minutes=CACHE_EXPIRY_MINUTES)


def get_demo_river_data() -> Dict:
    """Return demo river data for testing"""
    return {
        'flow': 45.5,
        'dateTime': datetime.now().isoformat(),
        'items': [{'value': 45.5, 'dateTime': datetime.now().isoformat()}]
    }


def get_demo_weather_data() -> Dict:
    """Return demo weather data for testing"""
    return {
        'temperature': 8.2,
        'wind_gust': 7.3,
        'observation_time': f'Latest observations at {datetime.now().strftime("%H:%M")}'
    }


def fetch_river_data() -> Optional[Dict]:
    """Fetch river flow data from Environment Agency API"""
    if DEMO_MODE:
        logger.info("DEMO MODE: Using demo river data")
        return get_demo_river_data()
    
    try:
        logger.info(f"Fetching river data from {RIVER_API_URL}")
        response = requests.get(RIVER_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract the latest flow value from items
        if 'items' in data and len(data['items']) > 0:
            # Get the most recent reading
            latest = data['items'][0]
            result = {
                'flow': latest.get('value'),
                'dateTime': latest.get('dateTime'),
                'items': data['items']
            }
            logger.info(f"Successfully fetched river data: flow={result['flow']} m³/s")
            return result
        logger.warning("No items found in river data response")
        return None
    except Exception as e:
        logger.error(f"Error fetching river data: {e}")
        return None


def fetch_weather_data() -> Optional[Dict]:
    """Fetch weather data from University of Reading"""
    if DEMO_MODE:
        logger.info("DEMO MODE: Using demo weather data")
        return get_demo_weather_data()
    
    try:
        logger.info(f"Fetching weather data from {WEATHER_URL}")
        response = requests.get(WEATHER_URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the observation timestamp from the top of the page
        observation_time = None
        for p in soup.find_all('p'):
            text = p.get_text()
            if 'Observation time:' in text or 'latest observations' in text.lower():
                observation_time = text
                break
        
        # Extract temperature
        temperature = None
        temp_pattern = r'Air temperature:\s*([-+]?\d+\.?\d*)\s*ºC'
        
        # Extract wind gust
        wind_gust = None
        wind_pattern = r'10-metre maximum 3-sec wind gust:\s*([-+]?\d+\.?\d*)\s*m/s'
        
        # Search through all text content
        page_text = soup.get_text()
        
        temp_match = re.search(temp_pattern, page_text)
        if temp_match:
            temperature = float(temp_match.group(1))
        
        wind_match = re.search(wind_pattern, page_text)
        if wind_match:
            wind_gust = float(wind_match.group(1))
        
        if temperature is not None and wind_gust is not None:
            result = {
                'temperature': temperature,
                'wind_gust': wind_gust,
                'observation_time': observation_time
            }
            logger.info(f"Successfully fetched weather data: temp={temperature}°C, wind={wind_gust} m/s")
            return result
        
        logger.warning(f"Failed to parse weather data. Temp: {temperature}, Wind: {wind_gust}")
        return None
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        return None


def get_river_condition(flow: float, boat_category: str) -> str:
    """Determine river flow condition based on rules"""
    if boat_category == "Fours, Quads, Eights":
        if flow >= 120:
            return "Black"
        elif flow >= 100:
            return "Red"
        elif flow >= 75:
            return "Amber"
        else:
            return "Green"
    else:  # Singles, Doubles, Pairs
        if flow >= 100:
            return "Black"
        elif flow >= 75:
            return "Red"
        elif flow >= 50:
            return "Amber"
        else:
            return "Green"


def get_wind_condition(wind_speed: float, boat_category: str) -> str:
    """Determine wind condition based on rules"""
    if boat_category == "Fours, Quads, Eights":
        if wind_speed >= 15.6:
            return "Black"
        elif wind_speed >= 13.6:
            return "Red"
        elif wind_speed >= 11.3:
            return "Amber"
        else:
            return "Green"
    else:  # Singles, Doubles, Pairs
        if wind_speed >= 13.6:
            return "Black"
        elif wind_speed >= 11.3:
            return "Red"
        elif wind_speed >= 9.0:
            return "Amber"
        else:
            return "Green"


def get_temperature_condition(temperature: float, boat_category: str) -> str:
    """Determine temperature condition based on rules"""
    if boat_category == "Fours, Quads, Eights":
        if temperature <= -3.0:
            return "Black"
        elif temperature <= 2.9:
            return "Red"
        elif temperature <= 6.9:
            return "Amber"
        else:
            return "Green"
    else:  # Singles, Doubles, Pairs
        if temperature <= 0.0:
            return "Black"
        elif temperature <= 4.9:
            return "Red"
        elif temperature <= 8.9:
            return "Amber"
        else:
            return "Green"


def calculate_overall_condition(river_cond: str, wind_cond: str, temp_cond: str) -> str:
    """Calculate overall rowing condition based on individual conditions"""
    conditions = [river_cond, wind_cond, temp_cond]
    
    # Check for NO ROWING conditions
    black_count = conditions.count("Black")
    red_count = conditions.count("Red")
    
    if black_count >= 1 or red_count >= 2:
        return "NO ROWING"
    
    # Return most severe condition
    severity_order = ["Green", "Amber", "Red", "Black"]
    most_severe = "Green"
    
    for condition in conditions:
        if severity_order.index(condition) > severity_order.index(most_severe):
            most_severe = condition
    
    return most_severe


def update_cache_if_needed():
    """Update cached data if expired"""
    # Check and update river data
    if is_cache_expired(cache['river_timestamp']):
        river_data = fetch_river_data()
        if river_data:
            cache['river_data'] = river_data
            cache['river_timestamp'] = datetime.now()
    
    # Check and update weather data
    if is_cache_expired(cache['weather_timestamp']):
        weather_data = fetch_weather_data()
        if weather_data:
            cache['weather_data'] = weather_data
            cache['weather_timestamp'] = datetime.now()


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/conditions')
def get_conditions():
    """API endpoint to get current rowing conditions"""
    update_cache_if_needed()
    
    # Check if we have valid cached data
    if cache['river_data'] is None or cache['weather_data'] is None:
        return jsonify({
            'error': 'Unable to fetch required data. Please try again later.'
        }), 503
    
    river_flow = cache['river_data']['flow']
    temperature = cache['weather_data']['temperature']
    wind_speed = cache['weather_data']['wind_gust']
    
    # Calculate conditions for both boat categories
    categories_data = {}
    
    for category in ["Fours, Quads, Eights", "Singles, Doubles, Pairs"]:
        river_cond = get_river_condition(river_flow, category)
        wind_cond = get_wind_condition(wind_speed, category)
        temp_cond = get_temperature_condition(temperature, category)
        overall_cond = calculate_overall_condition(river_cond, wind_cond, temp_cond)
        
        categories_data[category] = {
            'overall': overall_cond,
            'river': river_cond,
            'wind': wind_cond,
            'temperature': temp_cond
        }
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'data': {
            'river_flow': river_flow,
            'river_datetime': cache['river_data']['dateTime'],
            'temperature': temperature,
            'wind_speed': wind_speed,
            'weather_observation': cache['weather_data']['observation_time']
        },
        'conditions': categories_data,
        'cache_age': {
            'river': (datetime.now() - cache['river_timestamp']).seconds if cache['river_timestamp'] else None,
            'weather': (datetime.now() - cache['weather_timestamp']).seconds if cache['weather_timestamp'] else None
        }
    })


if __name__ == '__main__':
    # Initialize cache on startup
    print("Starting application...")
    update_cache_if_needed()
    app.run(host='0.0.0.0', port=5000, debug=False)
