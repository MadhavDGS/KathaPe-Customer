@echo off
REM KathaPe Customer App - Windows Service Stop Script

echo Stopping KathaPe Customer Application Services...
echo.

REM Check if NSSM is available and service is installed
nssm status KathaPeCustomer >nul 2>&1
if %errorlevel% equ 0 (
    echo Stopping KathaPe Customer Service...
    nssm stop KathaPeCustomer
    if %errorlevel% equ 0 (
        echo KathaPe Customer Service stopped successfully.
    ) else (
        echo Failed to stop KathaPe Customer Service.
    )
) else (
    echo KathaPe Customer Service not found or NSSM not available.
    echo Attempting to kill Python processes...
    taskkill /f /im python.exe /fi "WINDOWTITLE eq KathaPe*" >nul 2>&1
)

REM Stop Nginx if running as service
nssm status NginxService >nul 2>&1
if %errorlevel% equ 0 (
    echo Stopping Nginx Service...
    nssm stop NginxService
    if %errorlevel% equ 0 (
        echo Nginx Service stopped successfully.
    ) else (
        echo Failed to stop Nginx Service.
    )
) else (
    echo Nginx Service not found. Attempting to stop Nginx manually...
    taskkill /f /im nginx.exe >nul 2>&1
    if %errorlevel% equ 0 (
        echo Nginx processes terminated.
    ) else (
        echo No Nginx processes found.
    )
)

echo.
echo All services stopped.
pause
