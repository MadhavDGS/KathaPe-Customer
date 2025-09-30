# Cloudinary Image Storage Setup for Bill Receipts

## Create Cloudinary Account and Get Credentials

1. **Sign up for Cloudinary**: https://cloudinary.com/users/register/free
2. **Go to Dashboard**: After login, you'll see your dashboard with credentials
3. **Copy Your Credentials**:
   - **Cloud Name**: Found at the top of dashboard
   - **API Key**: Found in the "Account Details" section
   - **API Secret**: Click "Reveal" next to API Secret

4. **Update Environment Variables** in `.env`:
   ```env
   CLOUDINARY_CLOUD_NAME=your_cloud_name_here
   CLOUDINARY_API_KEY=your_api_key_here
   CLOUDINARY_API_SECRET=your_api_secret_here
   ```

## Install Dependencies

```bash
pip install cloudinary==1.36.0
```

## Benefits of Cloudinary

✅ **Unlimited Storage**: No file size restrictions (within reason)
✅ **Automatic Optimization**: Auto quality, format, and compression
✅ **Global CDN**: Fast delivery worldwide
✅ **Image Transformations**: Resize, crop, format conversion on-the-fly
✅ **Advanced Features**: AI-powered optimization, responsive images
✅ **Backup & Security**: Enterprise-grade infrastructure
✅ **Analytics**: Detailed usage and performance metrics
✅ **Free Tier**: 25GB storage, 25GB bandwidth/month free

## Image Upload Process

1. **Upload**: Images uploaded to `bill_receipts/` folder in Cloudinary
2. **Optimization**: Automatic quality and format optimization
3. **Transformations**: Resized to max 1200px, optimized for web
4. **Storage**: Public ID stored in database (e.g., `bill_receipts/bill_abc123_def456`)
5. **Delivery**: Served via Cloudinary's global CDN

## Image Transformations Applied

- **Quality**: Auto-optimized based on content
- **Format**: Auto-format (WebP, AVIF for modern browsers)
- **Size**: Max 1200px width/height, maintain aspect ratio
- **Compression**: Automatic lossless/lossy compression
- **Responsive**: Auto-width for different screen sizes

## File Organization

Images are stored with public IDs like:
```
bill_receipts/bill_<transaction_id>_<random_hash>
```

Example: `bill_receipts/bill_ef0032f1-31ba-4605-88c7-ad2edb7ff5fe_a1b2c3d4`

## Database Schema

The `receipt_image_url` field in transactions now stores:
- **New**: Cloudinary public_id (e.g., `bill_receipts/bill_abc123_def456`)
- **Legacy**: Base64 data or file paths (handled with fallback messages)

## URL Generation

Cloudinary automatically generates optimized URLs:
```
https://res.cloudinary.com/your-cloud-name/image/upload/q_auto,f_auto,w_auto,c_scale/bill_receipts/bill_abc123_def456
```

## Security Features

- **Secure URLs**: HTTPS by default
- **Access Control**: Can add authentication if needed  
- **Backup**: Automatic backups in Cloudinary infrastructure
- **Monitoring**: Real-time upload and access monitoring
