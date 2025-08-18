@echo off
REM KathaPe Customer App - Complete Windows Deployment Script
REM This script sets up and starts both the Flask app and Nginx

echo ========================================
echo KathaPe Customer - Windows Deployment
echo ========================================
echo.

REM Check if running as administrator (optional, but recommended)
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Not running as administrator. Some features may not work properly.
    echo For full functionality, please run as administrator.
    echo.
    timeout /t 5 >nul
)

REM Set up Python virtual environment and Flask app
echo [1/4] Setting up Flask Application...
echo.

if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment.
        echo Please ensure Python 3.8+ is installed and added to PATH.
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements-windows.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

REM Check environment configuration
echo [2/4] Checking Configuration...
echo.

if not exist ".env" (
    echo WARNING: .env file not found!
    if exist ".env.example" (
        echo Copying .env.example to .env...
        copy .env.example .env
        echo.
        echo IMPORTANT: Please edit .env file with your database credentials and settings.
        echo Press any key to open .env file for editing...
        pause >nul
        notepad .env
        echo.
        echo Make sure you've configured the database URL and other settings.
        echo Press any key to continue after saving the .env file...
        pause >nul
    ) else (
        echo ERROR: Neither .env nor .env.example file found!
        echo Please create .env file with your configuration.
        pause
        exit /b 1
    )
)

REM Create necessary directories
if not exist "logs" mkdir logs
if not exist "static\uploads\bills" mkdir static\uploads\bills

REM Start the Flask application
echo [3/4] Starting Flask Application...
echo.

echo Starting KathaPe Customer App with Waitress...
echo Application will be available at: http://localhost:8080
start "KathaPe Customer App" /min python wsgi.py

REM Wait a moment for the app to start
timeout /t 3 >nul

REM Check if the app is running
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8080/health' -UseBasicParsing -TimeoutSec 5; if ($response.StatusCode -eq 200) { Write-Host 'Flask app started successfully!' -ForegroundColor Green } else { Write-Host 'Flask app may not be running properly.' -ForegroundColor Yellow } } catch { Write-Host 'Flask app is not responding. Check the logs.' -ForegroundColor Red }"

REM Set up and start Nginx
echo.
echo [4/4] Setting up Nginx...
echo.

REM Check if Nginx is available
where nginx >nul 2>&1
if %errorlevel% neq 0 (
    echo Nginx not found in PATH. Checking common locations...
    set NGINX_PATH=""
    
    if exist "C:\nginx\nginx.exe" set NGINX_PATH=C:\nginx
    if exist "C:\nginx-*\nginx.exe" set NGINX_PATH=C:\nginx-*
    if exist "%ProgramFiles%\nginx\nginx.exe" set NGINX_PATH=%ProgramFiles%\nginx
    
    if "%NGINX_PATH%"=="" (
        echo.
        echo WARNING: Nginx not found!
        echo Please download and install Nginx from: http://nginx.org/en/download.html
        echo Suggested location: C:\nginx\
        echo.
        echo The Flask app is running on: http://localhost:8080
        echo You can access it directly without Nginx.
        echo.
        echo Would you like to download Nginx now? [Y/N]
        set /p DOWNLOAD_NGINX=
        if /i "%DOWNLOAD_NGINX%"=="Y" (
            start https://nginx.org/en/download.html
        )
        echo.
        echo Setup completed. Flask app is running on: http://localhost:8080
        pause
        exit /b 0
    )
    
    REM Add Nginx to PATH for this session
    set PATH=%PATH%;%NGINX_PATH%
    cd /d %NGINX_PATH%
) else (
    REM Find nginx directory
    for /f "tokens=*" %%i in ('where nginx') do set NGINX_EXE=%%i
    for %%i in ("%NGINX_EXE%") do set NGINX_PATH=%%~dpi
    cd /d %NGINX_PATH%
)

REM Copy nginx configuration if it doesn't exist or ask to update
if not exist "conf\nginx.conf.backup" (
    if exist "conf\nginx.conf" (
        echo Backing up original nginx.conf...
        copy conf\nginx.conf conf\nginx.conf.backup
    )
)

echo Copying KathaPe nginx configuration...
copy "%~dp0nginx.conf" conf\nginx.conf
if %errorlevel% neq 0 (
    echo WARNING: Failed to copy nginx configuration.
    echo You may need to manually copy nginx.conf to your Nginx conf directory.
)

REM Update paths in nginx.conf for current installation
powershell -Command "(Get-Content 'conf\nginx.conf') -replace 'C:/path/to/your/KathaPe-Customer/', '%~dp0' -replace '\\', '/' | Set-Content 'conf\nginx.conf'"

REM Test nginx configuration
echo Testing Nginx configuration...
nginx -t
if %errorlevel% neq 0 (
    echo ERROR: Nginx configuration test failed!
    echo Please check the nginx.conf file.
    pause
    exit /b 1
)

REM Start Nginx
echo Starting Nginx...
start "Nginx" /min nginx

REM Wait a moment for nginx to start
timeout /t 2 >nul

REM Final status check
echo.
echo ========================================
echo Deployment Status
echo ========================================

REM Check Flask app
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8080/health' -UseBasicParsing -TimeoutSec 5; Write-Host 'Flask App (Direct): Running on http://localhost:8080' -ForegroundColor Green } catch { Write-Host 'Flask App: Not responding' -ForegroundColor Red }"

REM Check Nginx
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost/' -UseBasicParsing -TimeoutSec 5; Write-Host 'Nginx Proxy: Running on http://localhost' -ForegroundColor Green } catch { Write-Host 'Nginx Proxy: Not responding' -ForegroundColor Red }"

echo.
echo Your KathaPe Customer application is now running!
echo.
echo Access URLs:
echo   Direct Flask App: http://localhost:8080
echo   Through Nginx:     http://localhost
echo.
echo Log files:
echo   Flask logs: %~dp0logs\
echo   Nginx logs: %NGINX_PATH%logs\
echo.
echo To stop services, run: stop-services.bat
echo To install as Windows services, run: install-service.ps1 (as Administrator)
echo.
pause
