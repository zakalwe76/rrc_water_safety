# Reading Rowing Club - Water Safety App

A Docker-based web application that evaluates weather data and water conditions against Reading Rowing Club's water safety rules to determine if it is safe to row.

## Features

- **Real-time Data Fetching**: Automatically retrieves river flow data from the UK Environment Agency and weather data from University of Reading
- **Smart Caching**: Caches data for 15 minutes to reduce API calls and improve performance
- **Safety Evaluation**: Evaluates conditions for two boat categories:
  - Fours, Quads, Eights
  - Singles, Doubles, Pairs
- **Visual Status Display**: Color-coded conditions (Green, Amber, Red, Black, NO ROWING)
- **Responsive Design**: Works on desktop and mobile devices
- **Docker Deployment**: Easy deployment using Docker containers

## Safety Rules

The app evaluates three parameters:

### River Flow (m³/s)
- **Black**: Dangerous conditions
- **Red**: Unsafe conditions
- **Amber**: Caution required
- **Green**: Safe conditions

### Wind Speed (m/s)
- **Black**: Too windy to row
- **Red**: High winds
- **Amber**: Moderate winds
- **Green**: Calm conditions

### Air Temperature (°C)
- **Black**: Hypothermia risk
- **Red**: Cold conditions
- **Amber**: Cool conditions
- **Green**: Safe temperature

### Overall Rowing Decision
- **NO ROWING**: If there is 1 or more Black condition OR 2 or more Red conditions
- Otherwise, the overall condition is the most severe of the three parameters

## Prerequisites

- Docker and Docker Compose installed on your system
- Internet connection to fetch external data

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. Clone or download this repository
2. Navigate to the project directory:
   ```bash
   cd rrc_water_safety
   ```

3. Build and start the application:
   ```bash
   docker-compose up -d
   ```

4. Access the application at: http://localhost:5000

5. To stop the application:
   ```bash
   docker-compose down
   ```

### Option 2: Using Docker Directly

1. Build the Docker image:
   ```bash
   docker build -t rrc-water-safety .
   ```

2. Run the container:
   ```bash
   docker run -d -p 5000:5000 --name rrc-water-safety rrc-water-safety
   ```

3. Access the application at: http://localhost:5000

4. To stop and remove the container:
   ```bash
   docker stop rrc-water-safety
   docker rm rrc-water-safety
   ```

## Local Development (Without Docker)

1. Install Python 3.11 or higher

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Access the application at: http://localhost:5000

## Project Structure

```
rrc_water_safety/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── style.css          # Stylesheet
│   └── script.js          # Frontend JavaScript
├── rules.md               # Safety rules specification
├── spec.md                # Functional specifications
└── README.md              # This file
```

## Data Sources

- **River Flow**: UK Environment Agency Flood Monitoring API
  - Station: 2200TH (River Thames at Reading)
  - Updates: Every 15 minutes
  - URL: http://environment.data.gov.uk/flood-monitoring/

- **Weather Data**: University of Reading METFiDAS
  - Observations: Air temperature and wind gust
  - Updates: Real-time weather observations
  - URL: https://www.met.reading.ac.uk/weatherdata/

## How It Works

1. **On Startup**: The app fetches initial data from both sources and caches it
2. **On Page View**: 
   - Checks if cached data is older than 15 minutes
   - Refreshes data if needed
   - Evaluates conditions against safety rules
   - Displays results with color-coded status
3. **Auto-refresh**: Frontend automatically refreshes every 5 minutes
4. **Manual Refresh**: Users can click "Refresh Now" to update immediately

## Configuration

### Changing the Port

To run on a different port, modify the port mapping in `docker-compose.yml`:

```yaml
ports:
  - "8080:5000"  # Access via http://localhost:8080
```

Or when using Docker directly:
```bash
docker run -d -p 8080:5000 rrc-water-safety
```

### Cache Duration

To change the cache expiry time, edit `CACHE_EXPIRY_MINUTES` in `app.py`:

```python
CACHE_EXPIRY_MINUTES = 15  # Change to desired minutes
```

## Troubleshooting

### Application Won't Start

1. Check if port 5000 is already in use:
   ```bash
   docker ps
   ```

2. View container logs:
   ```bash
   docker-compose logs
   ```

### Data Not Loading

1. Check internet connectivity
2. Verify that external data sources are accessible
3. Check container logs for error messages

### Build Errors

1. Ensure Docker is running
2. Try rebuilding without cache:
   ```bash
   docker-compose build --no-cache
   ```

## API Endpoints

### GET /
Returns the main HTML page

### GET /api/conditions
Returns JSON with current conditions:

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "data": {
    "river_flow": 45.5,
    "temperature": 8.2,
    "wind_speed": 7.3
  },
  "conditions": {
    "Fours, Quads, Eights": {
      "overall": "Green",
      "river": "Green",
      "wind": "Green",
      "temperature": "Amber"
    },
    "Singles, Doubles, Pairs": {
      "overall": "Amber",
      "river": "Green",
      "wind": "Green",
      "temperature": "Amber"
    }
  }
}
```

## Deployment to Production

For production deployment:

1. Use a reverse proxy (nginx) for HTTPS
2. Set appropriate environment variables
3. Configure proper logging
4. Set up monitoring and alerts
5. Use Docker Compose with restart policies

Example production `docker-compose.yml`:

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## License

This project is for use by Reading Rowing Club.

## Support

For issues or questions, please contact the development team.
