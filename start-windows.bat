@echo off
REM KathaPe Customer App - Windows Production Startup Script
REM This script starts the application using Waitress

echo Starting KathaPe Customer Application...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment. Please ensure Python is installed.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing/updating dependencies...
pip install -r requirements-windows.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and configure your settings.
    echo.
    pause
    exit /b 1
)

REM Start the application
echo.
echo Starting KathaPe Customer App with Waitress...
echo Server will be available at: http://localhost:8080
echo Press Ctrl+C to stop the server
echo.

python wsgi.py

pause
