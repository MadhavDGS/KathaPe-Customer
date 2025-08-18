# KathaPe Customer App - Windows Deployment Guide

## Prerequisites

1. **Python 3.8+** - Download from https://python.org
2. **PostgreSQL** - For the database (or use a remote database)
3. **Nginx** - Download from http://nginx.org/en/download.html
4. **NSSM** (Optional, for Windows Service) - Download from https://nssm.cc/download

## Quick Setup Instructions

### Step 1: Application Setup

1. **Clone/Download** your application to a folder (e.g., `C:\KathaPe-Customer`)

2. **Create environment file**:
   ```cmd
   copy .env.example .env
   ```
   Edit `.env` with your actual database credentials and settings.

3. **Install and start the application**:
   ```cmd
   start-windows.bat
   ```
   This will:
   - Create a Python virtual environment
   - Install all dependencies
   - Start the application with Waitress on port 8080

### Step 2: Nginx Setup

1. **Download Nginx** for Windows from http://nginx.org/en/download.html

2. **Extract** to a folder (e.g., `C:\nginx`)

3. **Replace** the default `C:\nginx\conf\nginx.conf` with the provided `nginx.conf`

4. **Update paths** in the nginx.conf file:
   - Change `C:/path/to/your/KathaPe-Customer/static/` to your actual path
   - Change `C:/path/to/your/KathaPe-Customer/static/favicon.ico` to your actual path

5. **Start Nginx**:
   ```cmd
   cd C:\nginx
   nginx.exe
   ```

### Step 3: Test the Setup

1. **Application direct access**: http://localhost:8080
2. **Through Nginx**: http://localhost (port 80)

## Production Deployment

### Option 1: Manual Service (Simple)

1. Create a batch file to start both services:
   ```batch
   @echo off
   echo Starting KathaPe Customer Application...
   cd C:\KathaPe-Customer
   start /min cmd /c start-windows.bat
   
   echo Starting Nginx...
   cd C:\nginx
   start /min cmd /c nginx.exe
   
   echo Services started!
   pause
   ```

### Option 2: Windows Services (Recommended)

1. **Install NSSM** (Non-Sucking Service Manager):
   - Download from https://nssm.cc/download
   - Or install via Chocolatey: `choco install nssm`

2. **Run PowerShell as Administrator** and execute:
   ```powershell
   cd C:\KathaPe-Customer
   .\install-service.ps1
   ```

3. **Install Nginx as Service** (optional):
   ```cmd
   nssm install "NginxService" "C:\nginx\nginx.exe"
   nssm set "NginxService" AppDirectory "C:\nginx"
   nssm set "NginxService" DisplayName "Nginx Web Server"
   nssm start "NginxService"
   ```

## Directory Structure After Setup

```
C:\KathaPe-Customer\
├── app.py                 # Main Flask application
├── wsgi.py               # WSGI entry point for Waitress
├── requirements-windows.txt # Dependencies
├── .env                  # Environment variables
├── .env.example          # Environment template
├── nginx.conf            # Nginx configuration
├── start-windows.bat     # Application startup script
├── install-service.ps1   # Windows service installer
├── venv\                 # Python virtual environment
├── logs\                 # Application logs
├── static\               # Static files (CSS, JS, images)
└── templates\            # HTML templates
```

## Configuration Files

### .env Configuration
```env
# Database
EXTERNAL_DATABASE_URL=postgresql://username:password@localhost:5432/kathape_db

# Flask
SECRET_KEY=your-super-secret-key-change-this
FLASK_ENV=production
FLASK_DEBUG=False

# Waitress
WAITRESS_HOST=127.0.0.1
WAITRESS_PORT=8080
WAITRESS_THREADS=4
```

### Nginx Configuration
- The provided `nginx.conf` includes:
  - Reverse proxy to Waitress (port 8080)
  - Static file serving
  - Rate limiting for security
  - File upload handling
  - Gzip compression
  - Security headers

## Service Management

### Application Service (if using NSSM)
```cmd
# Service management
nssm start KathaPeCustomer     # Start
nssm stop KathaPeCustomer      # Stop
nssm restart KathaPeCustomer   # Restart
nssm status KathaPeCustomer    # Check status
```

### Nginx Service (if using NSSM)
```cmd
# Nginx management
nginx -s reload    # Reload configuration
nginx -s quit      # Graceful shutdown
nginx -s stop      # Fast shutdown
```

## Monitoring and Logs

### Application Logs
- **Service logs**: `C:\KathaPe-Customer\logs\service-stdout.log`
- **Error logs**: `C:\KathaPe-Customer\logs\service-stderr.log`

### Nginx Logs
- **Access logs**: `C:\nginx\logs\access.log`
- **Error logs**: `C:\nginx\logs\error.log`

## Security Considerations

1. **Firewall**: Open only necessary ports (80, 443)
2. **SSL/HTTPS**: Configure SSL certificates in nginx.conf
3. **Database**: Secure PostgreSQL installation
4. **Updates**: Keep Python, Nginx, and dependencies updated
5. **Backups**: Regular database backups

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 80 and 8080 are available
2. **Permission issues**: Run services with appropriate user permissions
3. **Database connection**: Verify PostgreSQL is running and accessible
4. **Static files**: Check nginx.conf paths are correct

### Debug Steps

1. **Check application logs** in the logs directory
2. **Test direct Waitress access**: http://localhost:8080
3. **Verify Nginx configuration**: `nginx -t`
4. **Check Windows Event Viewer** for service errors

## Performance Tuning

### Waitress Configuration
- Adjust `WAITRESS_THREADS` in .env based on your server capacity
- Monitor memory usage and adjust as needed

### Nginx Configuration
- Enable gzip compression (already included)
- Configure caching for static assets
- Adjust worker processes based on CPU cores

### Database
- Configure PostgreSQL connection pooling
- Optimize database queries
- Regular maintenance and vacuuming

## SSL/HTTPS Setup

1. **Obtain SSL certificate** (Let's Encrypt, commercial CA, or self-signed)
2. **Uncomment HTTPS server block** in nginx.conf
3. **Update certificate paths** in the configuration
4. **Enable HTTP to HTTPS redirect**

## Backup Strategy

1. **Database**: Use pg_dump for PostgreSQL backups
2. **Application files**: Backup the entire application directory
3. **Configuration**: Backup nginx.conf and .env files
4. **Logs**: Archive old logs periodically

This setup provides a robust, production-ready deployment of your KathaPe Customer application on Windows 11 Pro.
