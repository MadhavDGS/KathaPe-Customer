# How to Get Cloudinary Credentials

## Step 1: Create Free Cloudinary Account

1. Visit: https://cloudinary.com/users/register/free
2. Sign up with your email
3. Verify your email account
4. Complete the onboarding process

## Step 2: Get Your Credentials

1. **Login to Cloudinary Console**: https://console.cloudinary.com/
2. **Go to Dashboard**: You'll see your account details
3. **Copy the following credentials**:

### From the Dashboard "Account Details" section:

```
Cloud name: [your_cloud_name]
API Key: [your_api_key] 
API Secret: [click "Copy" to reveal and copy]
```

## Step 3: Update Your .env File

Replace these placeholders in your `.env` file:

```env
# Replace with your actual Cloudinary credentials
CLOUDINARY_CLOUD_NAME=your_cloud_name_here
CLOUDINARY_API_KEY=your_api_key_here  
CLOUDINARY_API_SECRET=your_api_secret_here
```

## Step 4: Test Your Setup

Run this command to test:

```bash
python3 -c "
from dotenv import load_dotenv
load_dotenv()
from appwrite_utils import upload_bill_image
print('✅ Cloudinary configuration loaded successfully')
"
```

## Free Tier Limits

Cloudinary's free tier includes:
- **25 GB** of managed storage
- **25 GB** of monthly viewing bandwidth  
- **1,000** transformations per month
- **25** credits per month (for advanced features)

This is more than enough for most small to medium applications!

## Security Notes

- ✅ Keep your API Secret secure and never expose it in frontend code
- ✅ The Cloud Name and API Key can be public (they're used in URLs)
- ✅ API Secret should only be used in your backend server code
- ✅ Consider using signed URLs for sensitive images in production
