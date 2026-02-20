# Quick Start Guide

## For Windows Users

### Starting the Application

1. Make sure Docker Desktop is running
2. Double-click `start.bat`
3. Wait for the application to build and start
4. Open your browser to: http://localhost:5000

### Stopping the Application

1. Double-click `stop.bat`

## For Linux/Mac Users

### Starting the Application

```bash
docker-compose up -d --build
```

Open your browser to: http://localhost:5000

### Stopping the Application

```bash
docker-compose down
```

## Using the Application

Once the application is running:

1. **View Current Conditions**: The page automatically loads the latest water safety conditions
2. **Understand the Status**:
   - **Green**: Safe to row
   - **Amber**: Caution advised
   - **Red**: Unsafe conditions
   - **Black**: Dangerous conditions
   - **NO ROWING**: Do not row (1 Black OR 2+ Red conditions)

3. **Refresh Data**: Click "Refresh Now" button to get latest conditions
4. **Auto-Refresh**: Page automatically updates every 5 minutes

## Viewing Logs

To see what's happening behind the scenes:

```bash
docker-compose logs -f
```

Press Ctrl+C to exit log view.

## Troubleshooting

### Port Already in Use

If port 5000 is already in use, edit `docker-compose.yml` and change:

```yaml
ports:
  - "8080:5000"  # Use port 8080 instead
```

Then access via: http://localhost:8080

### Cannot Connect to Data Sources

The app needs internet access to fetch:
- River flow data from Environment Agency
- Weather data from University of Reading

Check your internet connection if you see "Unable to fetch required data" errors.

### Docker Issues

1. Make sure Docker Desktop is running
2. Try restarting Docker Desktop
3. Run: `docker-compose down` then `docker-compose up -d --build`

## Need Help?

See the full `README.md` for detailed information and troubleshooting.
