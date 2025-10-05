# 🚀 Quick Start Guide - TWA Setup

Follow these steps in order to publish your app to Google Play Store.

---

## ✅ PHASE 1: Prerequisites (30 minutes)

### 1. Install Android Studio
```bash
# Download from: https://developer.android.com/studio
# Install and complete first-time setup
```

### 2. Install Node.js (if not already installed)
```bash
# Download from: https://nodejs.org/
# Verify installation:
node --version
npm --version
```

### 3. Install Bubblewrap CLI
```bash
npm install -g @bubblewrap/cli

# Verify installation:
bubblewrap help
```

### 4. Run Bubblewrap Doctor
```bash
# This checks your environment and installs missing components
bubblewrap doctor
```

### 5. Create Google Play Console Account
- Visit: https://play.google.com/console/
- Pay $25 one-time registration fee
- Complete account setup

---

## ✅ PHASE 2: Deploy Digital Asset Links (10 minutes)

### 1. Commit and push the changes
```bash
cd /Users/sidhartha/Desktop/KathaPe-Customer

# Check what's changed
git status

# Add all changes
git add app.py templates/privacy.html templates/terms.html

# Commit
git commit -m "Add Digital Asset Links, Privacy Policy, and Terms of Service for Play Store"

# Push to trigger Render deployment
git push origin main
```

### 2. Wait for Render to deploy (5-10 minutes)
- Check your Render dashboard
- Wait for deployment to complete

### 3. Verify the endpoints
```bash
# Test Digital Asset Links endpoint (should return JSON with placeholder fingerprint)
curl https://khatape.tech/.well-known/assetlinks.json

# Test Privacy Policy (should return HTML)
curl https://khatape.tech/privacy

# Test Terms of Service (should return HTML)
curl https://khatape.tech/terms
```

---

## ✅ PHASE 3: Create Android App (30 minutes)

### 1. Create project directory
```bash
cd /Users/sidhartha/Desktop
mkdir KathaPe-Customer-Android
cd KathaPe-Customer-Android
```

### 2. Initialize TWA project
```bash
bubblewrap init --manifest=https://khatape.tech/manifest.json
```

### 3. Answer the prompts:
```
Domain: khatape.tech
App name: KathaPe Customer
Package: com.kathape.customer
Launcher name: KathaPe
Display: standalone
Orientation: portrait
Theme color: #1a1a2e
Background: #16213e
Icon URL: https://khatape.tech/static/icon-512x512.png
Status bar: #1a1a2e
```

### 4. Generate signing key
```bash
keytool -genkey -v \
  -keystore kathape-release-key.keystore \
  -alias kathape-key \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000
```

**⚠️ SAVE THESE SECURELY:**
- Keystore password
- Key password
- Keystore file location

### 5. Get SHA256 fingerprint
```bash
keytool -list -v \
  -keystore kathape-release-key.keystore \
  -alias kathape-key
```

**Copy the SHA256 fingerprint** (format: AA:BB:CC:DD:...)

---

## ✅ PHASE 4: Update Digital Asset Links (10 minutes)

### 1. Edit app.py
Open `/Users/sidhartha/Desktop/KathaPe-Customer/app.py` and find this line:
```python
"REPLACE_WITH_YOUR_SHA256_FINGERPRINT_FROM_KEYSTORE"
```

Replace it with your actual SHA256 fingerprint (with colons):
```python
"AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99"
```

### 2. Deploy the update
```bash
cd /Users/sidhartha/Desktop/KathaPe-Customer

git add app.py
git commit -m "Update Digital Asset Links with real SHA256 fingerprint"
git push origin main
```

### 3. Wait for Render deployment

### 4. Verify the update
```bash
curl https://khatape.tech/.well-known/assetlinks.json
# Should show your real fingerprint
```

---

## ✅ PHASE 5: Build Android App (15 minutes)

### 1. Configure signing in TWA project
```bash
cd /Users/sidhartha/Desktop/KathaPe-Customer-Android

# Edit twa-manifest.json to add signing key path
# Add these lines:
#   "signingKey": {
#     "path": "./kathape-release-key.keystore",
#     "alias": "kathape-key"
#   }
```

### 2. Build the app
```bash
bubblewrap build
```

Enter your keystore password when prompted.

### 3. Find the built files
```
Location of AAB (for Play Store):
./app/build/outputs/bundle/release/app-release-bundle.aab

Location of APK (for testing):
./app/build/outputs/apk/release/app-release.apk
```

---

## ✅ PHASE 6: Test on Device (20 minutes)

### 1. Enable Developer Mode on your Android phone
- Go to Settings → About Phone
- Tap "Build Number" 7 times
- Go back → Developer Options
- Enable "USB Debugging"

### 2. Connect phone and install
```bash
# Install debug version
bubblewrap install

# Or install APK manually
adb install ./app/build/outputs/apk/release/app-release.apk
```

### 3. Test checklist
- [ ] App launches and shows khatape.tech
- [ ] No browser UI visible (fullscreen)
- [ ] Login works
- [ ] QR scanning works
- [ ] Transactions work
- [ ] Bill upload works
- [ ] Navigation works properly

---

## ✅ PHASE 7: Prepare Store Assets (1-2 hours)

### 1. Create app icon (512x512)
- Use Figma, Canva, or design tool
- Save as `playstore-icon-512.png`
- Must NOT have transparent background

### 2. Create feature graphic (1024x500)
- Banner for top of Play Store listing
- Save as `playstore-feature-graphic.png`

### 3. Take screenshots (1080x1920)
- At least 2, maximum 8 screenshots
- Show key app features
- Take from real device
- Save in `playstore-screenshots/` folder

### 4. Write descriptions
- Short (80 chars): Already provided in guide
- Full (4000 chars): Already provided in guide

---

## ✅ PHASE 8: Publish to Play Store (1-2 hours)

### 1. Go to Play Console
- https://play.google.com/console/

### 2. Create new app
- App name: KathaPe Customer
- Language: English (United States)
- Type: App
- Price: Free

### 3. Complete all sections
- ✅ App content (Privacy Policy: https://khatape.tech/privacy)
- ✅ Data safety
- ✅ Content rating
- ✅ Target audience
- ✅ Store presence

### 4. Upload AAB
- Go to Production → Create release
- Upload: `app-release-bundle.aab`
- Add release notes
- Review and rollout

### 5. Wait for review
- Takes 1-7 days
- Monitor email for updates
- Check Play Console for status

---

## 📝 Important Files to Backup

**CRITICAL - Store these securely:**
```
✅ kathape-release-key.keystore (signing key)
✅ Keystore password
✅ Key alias: kathape-key
✅ Key password
```

**Without these, you CANNOT update your app!**

Backup locations:
1. External hard drive
2. Secure cloud storage (encrypted)
3. Password manager (for passwords)

---

## 🎉 Success!

Once approved, your app will be live at:
```
https://play.google.com/store/apps/details?id=com.kathape.customer
```

---

## 🆘 Need Help?

1. Check PLAYSTORE_SETUP.md for detailed troubleshooting
2. Run `bubblewrap doctor` to diagnose issues
3. Check Play Console for specific rejection reasons
4. Email: support@khatape.tech

---

## 📊 Post-Launch Checklist

After app is published:
- [ ] Test download from Play Store
- [ ] Monitor crash reports in Play Console
- [ ] Respond to user reviews
- [ ] Track download statistics
- [ ] Plan first update/improvements

---

**Ready to start? Begin with PHASE 1! 🚀**
