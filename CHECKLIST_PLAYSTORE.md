# 📱 KathaPe Customer - Play Store Publishing Checklist

**Track your progress as you publish your app to Google Play Store**

---

## 📊 Overall Progress

**Current Status:** 🟡 Phase 1 - Prerequisites Setup

**Estimated Time to Publish:** 4-6 hours of active work + 1-7 days Google review

---

## ✅ PHASE 1: Prerequisites & Account Setup

**Estimated Time:** 30-60 minutes

### Development Environment
- [ ] Android Studio installed and configured
- [ ] JDK 11+ installed
- [ ] Node.js and npm installed
- [ ] Bubblewrap CLI installed (`npm install -g @bubblewrap/cli`)
- [ ] Run `bubblewrap doctor` successfully

### Google Play Console
- [ ] Google Play Console account created
- [ ] $25 registration fee paid
- [ ] Account verification completed
- [ ] Developer profile filled out

### Documentation Review
- [ ] Read PLAYSTORE_SETUP.md completely
- [ ] Reviewed QUICKSTART_PLAYSTORE.md
- [ ] Understand TWA concept and requirements

**Phase 1 Status:** ⬜ Not Started / 🟡 In Progress / ✅ Complete

---

## ✅ PHASE 2: Server-Side Setup (COMPLETE ✅)

**Estimated Time:** 10 minutes

### Backend Endpoints
- [x] Digital Asset Links route added (`/.well-known/assetlinks.json`)
- [x] Privacy Policy page created (`/privacy`)
- [x] Terms of Service page created (`/terms`)
- [x] Changes committed to Git
- [x] Changes pushed to GitHub
- [ ] **YOUR TASK:** Verify Render deployment complete
- [ ] **YOUR TASK:** Test https://khatape.tech/.well-known/assetlinks.json
- [ ] **YOUR TASK:** Test https://khatape.tech/privacy
- [ ] **YOUR TASK:** Test https://khatape.tech/terms

**Phase 2 Status:** 🟡 Awaiting Your Verification

---

## ✅ PHASE 3: Android App Creation

**Estimated Time:** 30-45 minutes

### Project Initialization
- [ ] Created Android project directory (`KathaPe-Customer-Android`)
- [ ] Ran `bubblewrap init --manifest=https://khatape.tech/manifest.json`
- [ ] Answered all setup prompts correctly
  - [ ] Domain: `khatape.tech`
  - [ ] Package: `com.kathape.customer`
  - [ ] App name: `KathaPe Customer`

### Signing Key Generation
- [ ] Generated keystore with `keytool -genkey`
- [ ] Keystore saved at: `kathape-release-key.keystore`
- [ ] **CRITICAL:** Keystore password saved securely
- [ ] **CRITICAL:** Key alias saved: `kathape-key`
- [ ] **CRITICAL:** Key password saved securely
- [ ] Keystore backed up to safe location #1: _______________
- [ ] Keystore backed up to safe location #2: _______________

### SHA256 Fingerprint
- [ ] Extracted SHA256 fingerprint from keystore
- [ ] Fingerprint copied: `______________________________`
- [ ] Fingerprint format verified (AA:BB:CC:... with colons)

**Phase 3 Status:** ⬜ Not Started / 🟡 In Progress / ✅ Complete

---

## ✅ PHASE 4: Digital Asset Links Update

**Estimated Time:** 10 minutes

### Update Backend
- [ ] Opened `app.py` in code editor
- [ ] Found `REPLACE_WITH_YOUR_SHA256_FINGERPRINT_FROM_KEYSTORE`
- [ ] Replaced with actual SHA256 fingerprint
- [ ] Verified fingerprint includes colons (AA:BB:CC:...)
- [ ] Committed changes: `git add app.py`
- [ ] Pushed to GitHub: `git push origin main`

### Verify Deployment
- [ ] Render deployment completed successfully
- [ ] Verified assetlinks.json shows real fingerprint
- [ ] Tested: `curl https://khatape.tech/.well-known/assetlinks.json`
- [ ] JSON response contains your fingerprint

**Phase 4 Status:** ⬜ Not Started / 🟡 In Progress / ✅ Complete

---

## ✅ PHASE 5: Build Android App

**Estimated Time:** 15-20 minutes

### Configuration
- [ ] Edited `twa-manifest.json`
- [ ] Added signing key configuration
- [ ] Verified keystore path is correct

### Build Process
- [ ] Ran `bubblewrap build`
- [ ] Entered keystore password when prompted
- [ ] Build completed without errors
- [ ] AAB file located at: `app/build/outputs/bundle/release/app-release-bundle.aab`
- [ ] APK file located at: `app/build/outputs/apk/release/app-release.apk`

### File Verification
- [ ] AAB file exists and is > 1MB
- [ ] APK file exists and is > 1MB

**Phase 5 Status:** ⬜ Not Started / 🟡 In Progress / ✅ Complete

---

## ✅ PHASE 6: Device Testing

**Estimated Time:** 20-30 minutes

### Device Setup
- [ ] Android device connected via USB
- [ ] USB debugging enabled on device
- [ ] Device recognized by `adb devices`

### Installation
- [ ] App installed on device successfully
- [ ] App icon appears in launcher

### Functionality Testing
- [ ] App launches without errors
- [ ] Opens https://khatape.tech
- [ ] **No browser UI visible** (full-screen app mode)
- [ ] Login functionality works
- [ ] QR code scanning works
- [ ] Can create transactions
- [ ] Bill photo upload works
- [ ] Transaction history displays
- [ ] Balance updates correctly
- [ ] Navigation works properly
- [ ] Back button behaves correctly
- [ ] App doesn't crash during normal use

### Issues Found
```
Issue 1: ________________________________
Status: [ ] Fixed / [ ] Pending

Issue 2: ________________________________
Status: [ ] Fixed / [ ] Pending

Issue 3: ________________________________
Status: [ ] Fixed / [ ] Pending
```

**Phase 6 Status:** ⬜ Not Started / 🟡 In Progress / ✅ Complete

---

## ✅ PHASE 7: Store Assets Preparation

**Estimated Time:** 1-2 hours

### App Icon
- [ ] 512x512 px icon created
- [ ] Format: PNG, 32-bit
- [ ] No transparency
- [ ] Saved as: `playstore-icon-512.png`
- [ ] Icon looks good and represents brand

### Feature Graphic
- [ ] 1024x500 px banner created
- [ ] Format: PNG or JPG
- [ ] Saved as: `playstore-feature-graphic.png`
- [ ] Eye-catching and professional

### Screenshots
- [ ] Screenshot 1 captured (1080x1920)
- [ ] Screenshot 2 captured (1080x1920)
- [ ] Screenshot 3 captured (optional)
- [ ] Screenshot 4 captured (optional)
- [ ] Screenshot 5 captured (optional)
- [ ] Screenshot 6 captured (optional)
- [ ] Screenshot 7 captured (optional)
- [ ] Screenshot 8 captured (optional)
- [ ] All screenshots show key features
- [ ] Screenshots look professional
- [ ] Saved in: `playstore-screenshots/`

### Descriptions
- [ ] Short description written (80 chars max)
- [ ] Full description written (4000 chars max)
- [ ] App title finalized: `KathaPe Customer`
- [ ] Keywords identified for ASO

### Optional Assets
- [ ] Promo video created
- [ ] Video uploaded to YouTube
- [ ] Video URL saved: _______________

**Phase 7 Status:** ⬜ Not Started / 🟡 In Progress / ✅ Complete

---

## ✅ PHASE 8: Play Console Setup

**Estimated Time:** 1-2 hours

### App Creation
- [ ] Logged into Play Console
- [ ] Created new app
- [ ] App name: `KathaPe Customer`
- [ ] Default language: English (United States)
- [ ] App type: App
- [ ] Free or paid: Free

### App Content
- [ ] Privacy Policy URL: https://khatape.tech/privacy
- [ ] Terms of Service (optional): https://khatape.tech/terms
- [ ] App access instructions provided
- [ ] Test account credentials provided (if login required)
- [ ] Ads declaration: No ads ✅

### Content Rating
- [ ] Questionnaire completed
- [ ] Category: Finance
- [ ] Rating received
- [ ] Rating certificate downloaded

### Target Audience & Content
- [ ] Target age: 18+
- [ ] Target audience selected
- [ ] News app: No

### Data Safety
- [ ] Data collection disclosed
  - [ ] Email address collected
  - [ ] Phone number collected
  - [ ] Transaction data collected
  - [ ] Photos/images collected
- [ ] Data sharing: No
- [ ] Data security practices described
  - [ ] Data encrypted in transit
  - [ ] Data encrypted at rest
  - [ ] User can request data deletion
- [ ] Form submitted

### Store Listing
- [ ] App name: `KathaPe Customer`
- [ ] Short description added
- [ ] Full description added
- [ ] App icon uploaded (512x512)
- [ ] Feature graphic uploaded (1024x500)
- [ ] Screenshots uploaded (minimum 2)
- [ ] App category: Finance
- [ ] Contact email: support@khatape.tech
- [ ] Website: https://khatape.tech

### All Sections Complete
- [ ] Dashboard shows all green checkmarks
- [ ] No red warnings or errors
- [ ] All required sections completed

**Phase 8 Status:** ⬜ Not Started / 🟡 In Progress / ✅ Complete

---

## ✅ PHASE 9: App Submission

**Estimated Time:** 30 minutes

### Production Release
- [ ] Navigated to Production section
- [ ] Created new release
- [ ] Uploaded AAB file (`app-release-bundle.aab`)
- [ ] Release name: `Version 1.0 (1)`
- [ ] Release notes written

### Release Notes (Version 1.0)
```
Initial release of KathaPe Customer app!

Features:
- Track credit accounts with multiple businesses
- Scan QR codes for quick transactions
- Attach bill photos to transactions
- View complete transaction history
- Real-time balance updates
```

### Final Review
- [ ] Reviewed all information for accuracy
- [ ] Checked all screenshots display correctly
- [ ] Verified descriptions are correct
- [ ] Confirmed privacy policy accessible
- [ ] Double-checked AAB version (1.0)

### Submission
- [ ] Clicked "Review release"
- [ ] Reviewed summary page
- [ ] Clicked "Start rollout to Production"
- [ ] Confirmed rollout
- [ ] **Submission confirmed!** 🎉

### Submission Details
```
Submission Date: _______________
Submission Time: _______________
Version Code: 1
Version Name: 1.0
```

**Phase 9 Status:** ⬜ Not Started / 🟡 In Progress / ✅ Complete

---

## ✅ PHASE 10: Review & Launch

**Estimated Time:** 1-7 days (Google's review time)

### Waiting for Review
- [ ] Confirmation email received
- [ ] Status: Under review
- [ ] Monitoring Play Console dashboard
- [ ] Monitoring email for updates

### If Rejected
- [ ] Read rejection reason carefully
- [ ] Fix issues mentioned
- [ ] Resubmit app
- [ ] Note rejection reason: _______________

### App Published! 🎉
- [ ] Approval email received
- [ ] App live on Play Store
- [ ] Play Store URL: `https://play.google.com/store/apps/details?id=com.kathape.customer`
- [ ] Tested downloading from Play Store
- [ ] App installs correctly from store
- [ ] App works after store installation

### Launch Date
```
Published Date: _______________
Play Store URL: https://play.google.com/store/apps/details?id=com.kathape.customer
```

**Phase 10 Status:** ⬜ Not Started / 🟡 In Progress / ✅ Complete

---

## 🎉 POST-LAUNCH CHECKLIST

### Week 1
- [ ] Monitor crash reports daily
- [ ] Respond to user reviews (within 24 hours)
- [ ] Track download statistics
- [ ] Check for technical issues
- [ ] Share Play Store link with users
- [ ] Post on social media

### Month 1
- [ ] Analyze user feedback
- [ ] Plan improvements based on feedback
- [ ] Monitor DAU (Daily Active Users)
- [ ] Check retention rate
- [ ] Prepare first update

### Ongoing
- [ ] Update app every 2-3 months minimum
- [ ] Keep Play Console policies compliant
- [ ] Monitor Android version compatibility
- [ ] Test on new Android releases
- [ ] Maintain keystore backups

---

## 📋 CRITICAL INFORMATION TO SAVE

### Signing Key Details
```
Keystore File: kathape-release-key.keystore
Keystore Password: _______________
Key Alias: kathape-key
Key Password: _______________
SHA256 Fingerprint: _______________

Backup Location 1: _______________
Backup Location 2: _______________
Backup Location 3: _______________
```

### Play Console
```
Developer Account Email: _______________
Package Name: com.kathape.customer
Initial Version Code: 1
Initial Version Name: 1.0
```

### Important URLs
```
Play Store Listing: https://play.google.com/store/apps/details?id=com.kathape.customer
Privacy Policy: https://khatape.tech/privacy
Terms of Service: https://khatape.tech/terms
App Website: https://khatape.tech
Support Email: support@khatape.tech
```

---

## 🆘 TROUBLESHOOTING QUICK REFERENCE

### App shows browser UI (not full-screen)
- ✅ Verify Digital Asset Links JSON is accessible
- ✅ Check SHA256 fingerprint matches keystore
- ✅ Wait 24-48 hours for Google to cache
- ✅ Clear app data and reinstall

### Build fails
- ✅ Run `bubblewrap doctor`
- ✅ Check JDK version (needs 11+)
- ✅ Update Android SDK
- ✅ Try `bubblewrap update` then rebuild

### Play Console rejection
- ✅ Read rejection email carefully
- ✅ Check all content policies met
- ✅ Verify privacy policy accessible
- ✅ Complete all required sections
- ✅ Fix issues and resubmit

---

## 📞 SUPPORT & RESOURCES

- **TWA Documentation:** https://developer.chrome.com/docs/android/trusted-web-activity/
- **Bubblewrap GitHub:** https://github.com/GoogleChromeLabs/bubblewrap
- **Play Console Help:** https://support.google.com/googleplay/android-developer/
- **Your Email:** support@khatape.tech

---

## 🎯 NEXT STEPS

**You are currently at:** Phase 2 - Awaiting Server Verification

**Your next action:**
1. Wait for Render deployment to complete (5-10 minutes)
2. Test these URLs in your browser:
   - https://khatape.tech/.well-known/assetlinks.json
   - https://khatape.tech/privacy
   - https://khatape.tech/terms
3. If all URLs work, proceed to Phase 3
4. Follow QUICKSTART_PLAYSTORE.md for commands

---

**Good luck! You're on your way to publishing your first Android app! 🚀📱**
