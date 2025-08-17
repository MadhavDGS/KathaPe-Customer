# Bill Photo Feature Documentation

## Overview
The customer app now supports taking photos of bills/receipts during transactions for better record-keeping.

## Features Added

### 1. **File Upload in Transaction Form**
- Added file input field in transaction form (`templates/customer/transaction.html`)
- Accepts image files: PNG, JPG, JPEG, GIF
- Optional field - transactions can still be created without photos
- Camera capture support on mobile devices (`capture="camera"`)

### 2. **Photo Preview**
- Real-time preview of selected image before submission
- Remove photo option before submitting
- Responsive design for mobile and desktop

### 3. **Backend Processing**
- File validation and security (`app.py`)
- Secure filename generation with timestamp and customer ID
- Files stored in `static/uploads/bills/` directory
- Database integration with `receipt_image_url` field

### 4. **Database Storage**
- Photos stored in filesystem: `/static/uploads/bills/`
- Database stores relative URL path in `receipt_image_url` field
- Compatible with existing database schema

### 5. **Transaction History Display**
- Bill photos shown in transaction history
- Click to view full-size image in new tab
- Visual indicator when photo is available

## Technical Implementation

### File Upload Configuration
```python
UPLOAD_FOLDER = 'static/uploads/bills'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 16MB
```

### Security Features
- File type validation
- Secure filename generation
- Protected route for serving images
- Login required to access uploaded images

### Database Schema
Uses the `receipt_image_url` field in `transactions` table from `database_schema.sql`:
```sql
receipt_image_url TEXT,
```

## Usage

### For Customers
1. Navigate to any transaction form (Take Credit / Make Payment)
2. Fill amount and notes as usual
3. **Optional**: Click "Choose File" to select/take a bill photo
4. Preview the photo and remove if needed
5. Submit the transaction

### For Developers
- Files are automatically organized by date and customer
- Filename format: `YYYYMMDD_HHMMSS_{customer_id_prefix}_{original_filename}`
- Error handling for upload failures
- Graceful degradation if photo upload fails

## File Structure
```
static/
├── uploads/
│   └── bills/
│       ├── 20250817_143022_550e8400_receipt.jpg
│       └── 20250817_151245_a2b4c6d8_bill.png
```

## Browser Compatibility
- **Desktop**: File picker with drag-and-drop support
- **Mobile**: Camera capture option available
- **Preview**: Modern browsers with FileReader API support

## Future Enhancements
1. **Image compression** before upload
2. **Multiple photos** per transaction
3. **OCR integration** to extract amount from bill
4. **PhonePe integration** with bill photo
5. **Cloud storage** integration (AWS S3, etc.)

## Error Handling
- Invalid file types show user-friendly error
- Upload failures allow transaction to continue
- Missing permissions handled gracefully
- File size limits enforced

## Security Considerations
- Images only accessible to logged-in users
- No direct file access without authentication
- Secure filename prevents path traversal
- File type validation prevents malicious uploads

---

**Status**: ✅ **IMPLEMENTED AND TESTED**
**Date**: August 17, 2025
**Version**: 1.0
