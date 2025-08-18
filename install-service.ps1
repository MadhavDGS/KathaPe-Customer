# KathaPe Customer App - Windows Service Installation
# PowerShell script to install the app as a Windows Service using NSSM

param(
    [Parameter(Mandatory=$false)]
    [string]$ServiceName = "KathaPeCustomer",
    
    [Parameter(Mandatory=$false)]
    [string]$DisplayName = "KathaPe Customer Application",
    
    [Parameter(Mandatory=$false)]
    [string]$Description = "KathaPe Customer Management Flask Application"
)

# Check if running as administrator
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "This script requires administrator privileges. Please run as administrator." -ForegroundColor Red
    exit 1
}

# Get the current directory
$AppPath = Get-Location
$PythonExe = Join-Path $AppPath "venv\Scripts\python.exe"
$WSGIScript = Join-Path $AppPath "wsgi.py"

Write-Host "Installing KathaPe Customer as Windows Service..." -ForegroundColor Green
Write-Host "Service Name: $ServiceName"
Write-Host "App Path: $AppPath"
Write-Host "Python Executable: $PythonExe"
Write-Host "WSGI Script: $WSGIScript"
Write-Host ""

# Check if NSSM is available
$nssm = Get-Command nssm -ErrorAction SilentlyContinue
if (-not $nssm) {
    Write-Host "NSSM (Non-Sucking Service Manager) is required but not found." -ForegroundColor Red
    Write-Host "Please install NSSM from: https://nssm.cc/download" -ForegroundColor Yellow
    Write-Host "Or use Chocolatey: choco install nssm" -ForegroundColor Yellow
    exit 1
}

# Check if Python virtual environment exists
if (-not (Test-Path $PythonExe)) {
    Write-Host "Python virtual environment not found at: $PythonExe" -ForegroundColor Red
    Write-Host "Please run start-windows.bat first to create the virtual environment." -ForegroundColor Yellow
    exit 1
}

# Check if service already exists
$existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "Service '$ServiceName' already exists. Removing..." -ForegroundColor Yellow
    nssm stop $ServiceName
    nssm remove $ServiceName confirm
}

# Install the service
Write-Host "Installing service..." -ForegroundColor Green
nssm install $ServiceName $PythonExe $WSGIScript

# Configure the service
Write-Host "Configuring service..." -ForegroundColor Green
nssm set $ServiceName DisplayName "$DisplayName"
nssm set $ServiceName Description "$Description"
nssm set $ServiceName AppDirectory $AppPath
nssm set $ServiceName AppStdout "$AppPath\logs\service-stdout.log"
nssm set $ServiceName AppStderr "$AppPath\logs\service-stderr.log"
nssm set $ServiceName AppRotateFiles 1
nssm set $ServiceName AppRotateOnline 1
nssm set $ServiceName AppRotateSeconds 86400
nssm set $ServiceName AppRotateBytes 1048576

# Set startup type to automatic
nssm set $ServiceName Start SERVICE_AUTO_START

# Create logs directory if it doesn't exist
$LogsDir = Join-Path $AppPath "logs"
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force
    Write-Host "Created logs directory: $LogsDir" -ForegroundColor Green
}

# Start the service
Write-Host "Starting service..." -ForegroundColor Green
nssm start $ServiceName

# Check service status
Start-Sleep -Seconds 3
$serviceStatus = nssm status $ServiceName
Write-Host "Service Status: $serviceStatus" -ForegroundColor $(if ($serviceStatus -eq "SERVICE_RUNNING") { "Green" } else { "Red" })

if ($serviceStatus -eq "SERVICE_RUNNING") {
    Write-Host ""
    Write-Host "SUCCESS! KathaPe Customer service has been installed and started." -ForegroundColor Green
    Write-Host "The application should be available at: http://localhost:8080" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Service Management Commands:" -ForegroundColor Yellow
    Write-Host "  Start:   nssm start $ServiceName"
    Write-Host "  Stop:    nssm stop $ServiceName"
    Write-Host "  Restart: nssm restart $ServiceName"
    Write-Host "  Remove:  nssm remove $ServiceName confirm"
    Write-Host "  Status:  nssm status $ServiceName"
} else {
    Write-Host ""
    Write-Host "ERROR: Service failed to start. Check logs in: $LogsDir" -ForegroundColor Red
    Write-Host "You can also check Windows Event Viewer for more details." -ForegroundColor Yellow
}
