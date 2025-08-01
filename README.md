# KhataPe Customer App

A Flask-based customer application for managing business interactions and credit tracking.

## Features

- ✅ Customer registration and authentication  
- ✅ Business discovery via PIN/QR code
- ✅ Credit balance tracking
- ✅ Transaction history
- ✅ Profile management
- ✅ Mobile-friendly interface

## Deployment on Render

1. **Create a new Web Service** on Render
2. **Connect your GitHub repository**
3. **Configure deployment settings**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:customer_app --bind 0.0.0.0:$PORT`
   - **Environment**: `Python 3`

4. **Set Environment Variables**:
   ```
   RENDER=true
   DATABASE_URL=your_database_connection_string
   EXTERNAL_DATABASE_URL=your_external_database_connection_string
   SECRET_KEY=your_secret_key
   ```

5. **Deploy** and your customer app will be live!

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The app will be available at `http://localhost:5002`

## Database Schema

The app shares database tables with the business app:
- `users` - Customer user accounts
- `customers` - Customer profiles
- `businesses` - Business information
- `customer_credits` - Business-customer credit relationships
- `transactions` - Transaction history

## Tech Stack

- **Backend**: Flask 2.2.3
- **Database**: PostgreSQL (via psycopg2-binary)
- **Deployment**: Render
- **Authentication**: Session-based
- **QR Codes**: qrcode + Pillow
