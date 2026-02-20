@echo off
echo ========================================
echo Reading Rowing Club - Water Safety App
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running.
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo Docker is running...
echo.

REM Build and start the application
echo Building and starting the application...
docker-compose up -d --build

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start the application.
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Application is running.
echo ========================================
echo.
echo Access the app at: http://localhost:5000
echo.
echo To stop the application, run: docker-compose down
echo.
pause
