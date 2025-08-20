# KathaPe Customer - Deployment Guide

## Render Cloud Deployment

### Prerequisites
1. Appwrite 11.1.0 database setup
2. Render account
3. Git repository connected to Render

### Environment Variables (Render Dashboard)
Set these in your Render service environment:

```
# Appwrite Configuration
APPWRITE_PROJECT_ID=your_appwrite_project_id
APPWRITE_API_KEY=your_appwrite_api_key
APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
APPWRITE_DATABASE_ID=your_database_id

# Collection IDs
USERS_COLLECTION_ID=users
CUSTOMERS_COLLECTION_ID=customers
BUSINESSES_COLLECTION_ID=businesses
CUSTOMER_CREDITS_COLLECTION_ID=customer_credits
TRANSACTIONS_COLLECTION_ID=transactions

# Flask Configuration
SECRET_KEY=your-secure-secret-key-here
FLASK_ENV=production

# Optional: File Upload Configuration
MAX_CONTENT_LENGTH=16777216
```

### Deployment Steps

1. **Connect Repository**
   - Connect your GitHub repository to Render
   - Select the KathaPe-Customer repository

2. **Configure Service**
   - Service Type: Web Service
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:customer_app --bind 0.0.0.0:$PORT`
   - Environment: Python 3

3. **Set Environment Variables**
   - Add all the environment variables listed above
   - Make sure they match your Appwrite project configuration

4. **Deploy**
   - Render will automatically build and deploy your application
   - Monitor the build logs for any issues

### Database Collections

Your Appwrite database should have these collections:

1. **users**
   - user_id (string, key)
   - name (string)
   - phone_number (string, unique)
   - user_type (string) - 'customer' or 'business'
   - password (string)
   - created_at (datetime)

2. **customers**
   - customer_id (string, key)
   - user_id (string)
   - name (string)
   - phone_number (string, unique)
   - created_at (datetime)

3. **businesses**
   - business_id (string, key)
   - business_name (string)
   - owner_name (string)
   - business_phone (string, unique)
   - business_password (string)
   - business_upi_id (string)
   - qr_code_path (string)
   - created_at (datetime)

4. **transactions**
   - transaction_id (string, key)
   - customer_id (string)
   - business_id (string)
   - amount (float)
   - transaction_type (string)
   - transaction_date (datetime)
   - description (string)
   - bill_image_path (string, optional)
   - business_confirmation (boolean, default: false)

5. **customer_credits**
   - credit_id (string, key)
   - customer_id (string)
   - business_id (string)
   - amount (float)
   - created_at (datetime)
   - updated_at (datetime)

### File Structure
```
KathaPe-Customer/
├── app.py                 # Main Flask application
├── appwrite_utils.py      # Appwrite database utilities
├── requirements.txt       # Python dependencies
├── Procfile              # Render deployment configuration
├── .env.example          # Environment variables template
├── static/               # Static files (CSS, images)
├── templates/            # HTML templates
└── APPWRITE_MIGRATION.md # Migration documentation
```

### Health Check
After deployment, your application will be available at:
`https://your-render-service-name.onrender.com`

Test the following endpoints:
- `/` - Customer login page
- `/register` - Customer registration
- `/dashboard` - Customer dashboard (requires login)

### Troubleshooting

1. **Appwrite Connection Issues**
   - Verify all environment variables are set correctly
   - Check Appwrite project ID and API key
   - Ensure database and collections exist

2. **Build Failures**
   - Check requirements.txt for correct package versions
   - Monitor Render build logs for specific errors

3. **Runtime Errors**
   - Check Render service logs
   - Verify environment variables are accessible
   - Test Appwrite connectivity

### Monitoring

- Monitor your application through Render dashboard
- Check Appwrite database usage and logs
- Set up alerts for service availability

### Security Notes

- Never commit real environment variables to git
- Use strong secret keys
- Regularly rotate API keys
- Monitor Appwrite usage and access logs
