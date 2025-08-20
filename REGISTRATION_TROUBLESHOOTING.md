# Registration Troubleshooting Guide

## Common Registration Issues

### 1. "Database not found" Error
- **Cause**: Appwrite database not properly configured
- **Solution**: 
  - Verify `APPWRITE_DATABASE_ID` is correct
  - Ensure the database exists in your Appwrite project
  - Check that all collections are created

### 2. "Phone number already registered" Error  
- **Cause**: User already exists in the database
- **Solution**: Use a different phone number or check the existing user

### 3. "Failed to create customer" Error
- **Cause**: Customer profile creation failed after user creation
- **Solution**: 
  - Check that the `customers` collection exists
  - Verify collection permissions allow document creation
  - Check Appwrite API key has sufficient permissions

### 4. Registration Form Not Submitting
- **Cause**: Frontend form validation or connectivity issues
- **Solution**:
  - Check browser console for JavaScript errors
  - Verify form fields are filled correctly
  - Ensure phone number is exactly 10 digits

## Required Environment Variables

For registration to work, these environment variables must be set:

```bash
APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=your_project_id
APPWRITE_API_KEY=your_api_key
APPWRITE_DATABASE_ID=your_database_id
USERS_COLLECTION_ID=users
CUSTOMERS_COLLECTION_ID=customers
```

## Testing Registration

1. **Set up environment variables** in your Render dashboard or .env file
2. **Create required collections** in your Appwrite database:
   - users
   - customers  
   - businesses
   - transactions
   - customer_credits
3. **Test with valid data**:
   - Name: Any string
   - Phone: Exactly 10 digits (e.g., 9876543210)
   - Password: Any string

## Debug Steps

1. Check Render service logs for specific error messages
2. Verify Appwrite project is accessible
3. Test database connection in Appwrite console
4. Ensure all required collections exist with proper permissions

## Collection Permissions

In Appwrite, ensure your collections have these permissions:
- **Create**: API Key role
- **Read**: API Key role  
- **Update**: API Key role
- **Delete**: API Key role (optional)
