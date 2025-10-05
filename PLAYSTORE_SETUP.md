# 📱 KathaPe Customer - Play Store Publishing Guide

## Complete Guide to Convert PWA to Android App using TWA

---

## 🎯 **Overview**

This guide will help you convert your KathaPe Customer PWA into a native Android app and publish it on Google Play Store using **Trusted Web Activities (TWA)**.

**Your App Details:**
- **Domain**: https://khatape.tech
- **Package Name**: com.kathape.customer
- **App Name**: KathaPe Customer

---

## 📋 **Prerequisites Checklist**

### **1. Google Play Console Account**
- [ ] Create account at: https://play.google.com/console/
- [ ] Pay $25 one-time registration fee
- [ ] Complete account setup and verification

### **2. Development Tools**
- [ ] Install Android Studio: https://developer.android.com/studio
- [ ] Install JDK 11 or higher: https://adoptium.net/
- [ ] Install Node.js (for Bubblewrap): https://nodejs.org/

### **3. Domain Setup**
- [ ] Verify https://khatape.tech is accessible
- [ ] Ensure HTTPS certificate is valid
- [ ] Confirm PWA manifest is available at https://khatape.tech/manifest.json

---

## 🚀 **PHASE 1: Setup Digital Asset Links**

Digital Asset Links verify that you own the domain and authorize the Android app to open your website.

### **Step 1.1: Add Asset Links Route to Flask App**

Open `app.py` and add this route:

```python
@customer_app.route('/.well-known/assetlinks.json')
def asset_links():
    """Digital Asset Links for Android TWA"""
    return jsonify([{
        "relation": ["delegate_permission/common.handle_all_urls"],
        "target": {
            "namespace": "android_app",
            "package_name": "com.kathape.customer",
            "sha256_cert_fingerprints": [
                "REPLACE_WITH_YOUR_SHA256_FINGERPRINT"
            ]
        }
    }]), 200, {'Content-Type': 'application/json'}
```

### **Step 1.2: Generate SHA256 Fingerprint**

You'll get the fingerprint after creating your signing key in Phase 2. For now, leave it as placeholder.

---

## 🚀 **PHASE 2: Install Bubblewrap CLI**

Bubblewrap is Google's official tool for creating TWA apps.

### **Step 2.1: Install Bubblewrap**

```bash
npm install -g @bubblewrap/cli
```

### **Step 2.2: Verify Installation**

```bash
bubblewrap help
```

### **Step 2.3: Install Android SDK via Bubblewrap**

```bash
bubblewrap doctor
```

This will check your environment and help install missing components.

---

## 🚀 **PHASE 3: Initialize TWA Project**

### **Step 3.1: Create TWA Project**

```bash
cd /Users/sidhartha/Desktop
mkdir KathaPe-Customer-Android
cd KathaPe-Customer-Android

bubblewrap init --manifest=https://khatape.tech/manifest.json
```

### **Step 3.2: Answer the Setup Questions**

When prompted, enter:

```
Domain being opened in the TWA: khatape.tech
Name of the application: KathaPe Customer
Application package name: com.kathape.customer
Launcher name: KathaPe
Display mode (fullscreen/standalone): standalone
Orientation (any/portrait/landscape): portrait
Theme color: #1a1a2e (or your brand color)
Background color: #16213e (or your brand color)
Icon URL: https://khatape.tech/static/icon-512x512.png
Maskable icon URL: (leave blank if not available)
Splash screen color: #16213e
Status bar color: #1a1a2e
```

---

## 🚀 **PHASE 4: Create Signing Key**

### **Step 4.1: Generate Release Keystore**

```bash
cd KathaPe-Customer-Android

keytool -genkey -v -keystore kathape-release-key.keystore -alias kathape-key -keyalg RSA -keysize 2048 -validity 10000
```

**Enter the following information when prompted:**
- Password: Choose a strong password (save it securely!)
- First and Last Name: Your name or company name
- Organizational Unit: Development
- Organization: KathaPe
- City/Locality: Your city
- State/Province: Your state
- Country Code: IN (for India)

**⚠️ IMPORTANT: Save these details securely!**
- Keystore file location
- Keystore password
- Key alias: `kathape-key`
- Key password

### **Step 4.2: Get SHA256 Fingerprint**

```bash
keytool -list -v -keystore kathape-release-key.keystore -alias kathape-key
```

Look for the line starting with `SHA256:` and copy the fingerprint (format: `AA:BB:CC:...`).

### **Step 4.3: Update Digital Asset Links**

Go back to your Flask app and update the `asset_links()` route with the real SHA256 fingerprint:

```python
"sha256_cert_fingerprints": [
    "AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99"
]
```

### **Step 4.4: Deploy Updated Asset Links**

```bash
cd /Users/sidhartha/Desktop/KathaPe-Customer
git add app.py
git commit -m "Add Digital Asset Links for Android TWA"
git push origin main
```

Wait for Render to deploy, then verify:
```bash
curl https://khatape.tech/.well-known/assetlinks.json
```

---

## 🚀 **PHASE 5: Build the Android App**

### **Step 5.1: Update Bubblewrap Configuration**

Edit `twa-manifest.json` in your Android project:

```json
{
  "signingKey": {
    "path": "./kathape-release-key.keystore",
    "alias": "kathape-key"
  }
}
```

### **Step 5.2: Build the APK**

```bash
cd /Users/sidhartha/Desktop/KathaPe-Customer-Android

bubblewrap build
```

Enter your keystore password when prompted.

### **Step 5.3: Locate the Built APK**

The APK will be at:
```
KathaPe-Customer-Android/app/build/outputs/bundle/release/app-release-bundle.aab
```

---

## 🚀 **PHASE 6: Test the App**

### **Step 6.1: Install on Physical Device**

Connect your Android phone via USB and enable Developer Mode:

```bash
# Install the debug version first
bubblewrap install

# Or manually install the APK
adb install app/build/outputs/apk/release/app-release.apk
```

### **Step 6.2: Test Checklist**

- [ ] App launches and opens khatape.tech
- [ ] No browser UI visible (full screen)
- [ ] Login works correctly
- [ ] QR code scanning works
- [ ] Transaction creation works
- [ ] Bill photo upload works
- [ ] Back button navigation works
- [ ] App doesn't crash

---

## 🚀 **PHASE 7: Prepare Play Store Listing**

### **Step 7.1: Create Required Assets**

You need these assets for Play Store:

#### **App Icon**
- Size: 512x512 px
- Format: PNG (32-bit)
- Transparent background NOT allowed
- Location: Save as `playstore-icon-512.png`

#### **Feature Graphic**
- Size: 1024x500 px
- Format: PNG or JPG
- This appears at the top of your Play Store listing
- Location: Save as `playstore-feature-graphic.png`

#### **Screenshots (at least 2, max 8)**
- Size: 1080x1920 px (9:16 ratio)
- Format: PNG or JPG
- Show key features of your app
- Take screenshots from actual device
- Location: Save in `playstore-screenshots/` folder

#### **Promo Video (Optional)**
- Upload to YouTube
- 30 seconds to 2 minutes
- Shows app features

### **Step 7.2: Write App Description**

**Short Description (80 characters max):**
```
Manage your credit accounts and payments easily with KathaPe Customer app
```

**Full Description (4000 characters max):**
```
KathaPe Customer - Your Personal Credit Management Solution

Easily track and manage your credit accounts with local businesses. KathaPe Customer makes it simple to:

✅ Track Credit with Multiple Businesses
Keep tabs on all your credit accounts in one place. See your outstanding balance with each business instantly.

✅ Quick QR Code Transactions
Scan business QR codes to quickly add new transactions. No manual entry needed!

✅ Snap & Save Bill Photos
Take photos of your bills and attach them to transactions. Never lose a receipt again!

✅ Real-time Balance Updates
See your current balance with each business updated in real-time.

✅ Transaction History
View complete transaction history with all businesses including bill photos and notes.

✅ Secure & Private
Your financial data is encrypted and secure. Only you can access your account information.

Perfect for:
• Regular customers at local shops and businesses
• Managing credit accounts with multiple vendors
• Keeping track of khata/udhar transactions
• Digital record keeping of all purchases

Download KathaPe Customer today and experience hassle-free credit management!

For business owners, download KathaPe Business to manage customer credits.

Privacy Policy: https://khatape.tech/privacy
Terms of Service: https://khatape.tech/terms
```

### **Step 7.3: Category & Tags**

- **Category**: Finance
- **Tags**: credit, payments, khata, udhar, business, finance, transactions
- **Content Rating**: Everyone
- **Target Age**: 18+

---

## 🚀 **PHASE 8: Publish to Play Store**

### **Step 8.1: Create New App in Play Console**

1. Go to: https://play.google.com/console/
2. Click "Create app"
3. Fill in:
   - **App name**: KathaPe Customer
   - **Default language**: English (United States)
   - **App or game**: App
   - **Free or paid**: Free
4. Accept declarations and click "Create app"

### **Step 8.2: Set Up App Content**

Complete all required sections:

#### **Privacy Policy**
- URL: https://khatape.tech/privacy
- (You need to create this page)

#### **App Access**
- If your app requires login, provide test credentials
- Username: `test@kathape.tech`
- Password: (provide test password)

#### **Ads**
- Select: "No, my app does not contain ads" (if true)

#### **Content Rating**
- Complete the questionnaire
- Select category: Finance
- Answer questions about content

#### **Target Audience**
- Age: 18 and over

#### **Data Safety**
- Data collection: Yes (email, transactions)
- Data sharing: No
- Security practices: Data encrypted in transit and at rest

### **Step 8.3: Upload App Bundle**

1. Go to: **Production** → **Create new release**
2. Upload the AAB file:
   ```
   KathaPe-Customer-Android/app/build/outputs/bundle/release/app-release-bundle.aab
   ```
3. **Release name**: Version 1.0 (1)
4. **Release notes**:
   ```
   Initial release of KathaPe Customer app!
   
   Features:
   - Track credit accounts with multiple businesses
   - Scan QR codes for quick transactions
   - Attach bill photos to transactions
   - View complete transaction history
   - Real-time balance updates
   ```

### **Step 8.4: Add Store Listing**

1. **App name**: KathaPe Customer
2. **Short description**: (Use from Step 7.2)
3. **Full description**: (Use from Step 7.2)
4. **App icon**: Upload 512x512 icon
5. **Feature graphic**: Upload 1024x500 graphic
6. **Screenshots**: Upload at least 2 screenshots
7. **Phone**: Upload screenshots
8. **7-inch tablet**: (Optional)
9. **10-inch tablet**: (Optional)

### **Step 8.5: Review and Publish**

1. Review all sections - ensure all are marked complete (green checkmarks)
2. Click "Review release"
3. Review the summary
4. Click "Start rollout to Production"
5. Confirm rollout

### **Step 8.6: Wait for Review**

- Google Play review takes **1-7 days**
- You'll receive email updates
- Check Play Console for status updates
- App will be published automatically after approval

---

## 🎉 **PHASE 9: Post-Launch**

### **Step 9.1: Monitor App Performance**

- Check Play Console for crash reports
- Monitor user reviews and ratings
- Track download statistics
- Respond to user feedback

### **Step 9.2: Update App (Future)**

When you need to update:

```bash
cd /Users/sidhartha/Desktop/KathaPe-Customer-Android

# Update version in twa-manifest.json
# Increment versionCode and versionName

# Rebuild
bubblewrap update
bubblewrap build

# Upload new AAB to Play Console
```

---

## 📝 **Important Notes**

### **Keystore Security**
- ⚠️ **NEVER lose your keystore file!**
- ⚠️ **NEVER forget your keystore password!**
- ⚠️ **Backup keystore to multiple secure locations**
- Without the original keystore, you CANNOT update your app

### **Version Management**
- Increment `versionCode` for every release
- Update `versionName` for user-visible versions
- Follow semantic versioning (1.0.0, 1.1.0, 2.0.0)

### **Digital Asset Links**
- Must be accessible at https://khatape.tech/.well-known/assetlinks.json
- Must return valid JSON with correct SHA256 fingerprint
- Must be publicly accessible (no authentication required)

### **Domain Changes**
- If you change hosting platforms, keep khatape.tech pointing to new server
- No app update needed if domain stays same
- If domain changes, you must rebuild and resubmit app

---

## 🆘 **Troubleshooting**

### **Issue: App shows browser UI instead of full screen**
- Verify Digital Asset Links JSON is accessible
- Confirm SHA256 fingerprint matches your keystore
- Check package name matches in all places
- Wait 24 hours for Google to cache asset links

### **Issue: Bubblewrap build fails**
- Run `bubblewrap doctor` to check environment
- Ensure Android SDK is installed correctly
- Check Java/JDK version (needs JDK 11+)
- Try `bubblewrap update` then `bubblewrap build`

### **Issue: Play Console rejects app**
- Ensure all content policies are met
- Complete all required sections (green checkmarks)
- Provide valid privacy policy URL
- Add screenshots and descriptions

### **Issue: App crashes on launch**
- Check if https://khatape.tech is accessible
- Verify HTTPS certificate is valid
- Test PWA in mobile Chrome browser first
- Check Play Console crash reports for details

---

## 📚 **Useful Resources**

- **TWA Documentation**: https://developer.chrome.com/docs/android/trusted-web-activity/
- **Bubblewrap GitHub**: https://github.com/GoogleChromeLabs/bubblewrap
- **Play Console Help**: https://support.google.com/googleplay/android-developer/
- **Digital Asset Links**: https://developers.google.com/digital-asset-links/v1/getting-started

---

## ✅ **Quick Reference Checklist**

### **Before Building:**
- [ ] PWA working on khatape.tech
- [ ] Manifest.json accessible
- [ ] Icons available (192x192, 512x512)
- [ ] Android Studio installed
- [ ] Bubblewrap CLI installed
- [ ] Play Console account created

### **During Build:**
- [ ] TWA project initialized
- [ ] Signing key generated
- [ ] SHA256 fingerprint copied
- [ ] Digital Asset Links deployed
- [ ] App built successfully
- [ ] App tested on device

### **Before Publishing:**
- [ ] All Play Console sections complete
- [ ] Privacy policy page created
- [ ] App icon ready (512x512)
- [ ] Feature graphic ready (1024x500)
- [ ] Screenshots ready (2-8 images)
- [ ] App description written
- [ ] Content rating completed

### **After Publishing:**
- [ ] App submitted for review
- [ ] Keystore backed up securely
- [ ] Test credentials provided (if needed)
- [ ] Monitor review status
- [ ] Respond to reviewer feedback

---

## 🎊 **Congratulations!**

Once your app is published, users can download **KathaPe Customer** from Google Play Store!

**Play Store URL will be:**
```
https://play.google.com/store/apps/details?id=com.kathape.customer
```

Share this link with your users to start growing your customer base! 📱✨

---

**Need help?** Check the troubleshooting section or reach out to Google Play Developer Support.
