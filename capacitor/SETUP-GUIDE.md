# 🐕 UNLEASHED! — Native App & Ad Setup Guide

## What's Been Set Up

Your game now has TWO ad systems ready to go:

### 1. Web Ads (Google AdSense) — for browser/itch.io
- Banner ads on menu & game over screens
- Interstitial ad every 3rd game over
- Disabled by default until you get an AdSense account

### 2. Native Ads (Google AdMob) — for App Store/Google Play
- Native banner ads (bottom of screen)
- Native interstitial ads between games
- Much higher revenue than web ads on mobile

---

## 🚀 Step 1: Set Up Google AdSense (Web Ads)

1. Go to https://adsense.google.com
2. Sign up with your Google account
3. Add your site: `art367.github.io`
4. Wait for approval (usually 1-3 days for game sites)
5. Once approved, get your:
   - **Publisher ID** (looks like: `ca-pub-1234567890123456`)
   - **Ad unit slot IDs** (create 3 units: menu banner, game over banner, interstitial)

6. Edit `index.html` and find `AD_CONFIG` near line 3500:
   ```javascript
   var AD_CONFIG = {
     enabled: true,  // ← Change to true
     publisherId: 'ca-pub-YOUR-ID-HERE',  // ← Your publisher ID
     bannerSlot: 'YOUR-BANNER-SLOT',
     interstitialSlot: 'YOUR-INTERSTITIAL-SLOT',
   };
   ```

That's it! Ads will start showing immediately.

---

## 📱 Step 2: Build Native Apps with Capacitor

### What You Need on Your Computer:
- **For Android**: Android Studio (free) — https://developer.android.com/studio
- **For iOS**: Xcode (free, Mac only) — from the Mac App Store
- **Node.js 22+**: https://nodejs.org

### Get the project on your computer:

```bash
# Clone your repo
git clone https://github.com/art367/unleashed-game.git

# Navigate to the Capacitor project
cd unleashed-game/capacitor

# Install dependencies
npm install

# Open in Android Studio
npx cap open android

# OR open in Xcode (Mac only)
npx cap open ios
```

### Building for Android:
1. Open Android Studio
2. Click **Build → Build Bundle / APK → Build APK**
3. The APK file will be in `android/app/build/outputs/apk/`
4. Test it on your phone!

### Building for iOS:
1. Open Xcode
2. Select your Apple Developer team in **Signing & Capabilities**
3. Click **Product → Build** then **Product → Archive**
4. Submit to App Store from the Organizer window

---

## 💰 Step 3: Set Up AdMob (Native App Ads)

1. Go to https://admob.google.com
2. Create an account (or use same Google account as AdSense)
3. Add two apps: one for Android, one for iOS
4. Create ad units for each app:
   - **Banner** ad unit
   - **Interstitial** ad unit
5. Edit `www/admob-native.js` and replace the IDs:
   ```javascript
   android: {
     banner: 'ca-app-pub-YOUR-ID/YOUR-ANDROID-BANNER',
     interstitial: 'ca-app-pub-YOUR-ID/YOUR-ANDROID-INTERSTITIAL',
   },
   ios: {
     banner: 'ca-app-pub-YOUR-ID/YOUR-IOS-BANNER',
     interstitial: 'ca-app-pub-YOUR-ID/YOUR-IOS-INTERSTITIAL',
   }
   ```
6. Run `npx cap sync` to update the native projects

### For Testing (During Development):
Uncomment the test IDs in `admob-native.js` and set `isTesting: true`.
This shows Google's test ads so you don't violate AdMob policies.

---

## 🏪 Step 4: Publish to App Stores

### Google Play Store:
1. Create developer account at https://play.google.com/console ($25 one-time fee)
2. Create a new app, fill in details
3. Upload the signed AAB (Android App Bundle) from Android Studio
4. Add screenshots, description, and icon
5. Submit for review (usually 1-3 days)

### Apple App Store:
1. Enrol in Apple Developer Program at https://developer.apple.com ($99/year)
2. Create app in App Store Connect
3. Upload build from Xcode
4. Add screenshots, description, and icon
5. Submit for review (usually 1-2 days)

---

## 💵 Expected Revenue

| Platform | Revenue Model | Est. Monthly (1K daily players) |
|----------|--------------|--------------------------------|
| Web (AdSense) | Banner + Interstitial | £15-40 |
| Android (AdMob) | Banner + Interstitial | £30-80 |
| iOS (AdMob) | Banner + Interstitial | £40-120 |
| itch.io | Donations ($2 suggested) | £10-50 |
| **Total** | | **£95-290/month** |

Revenue scales with players. At 10K daily players: £950-2,900/month.

---

## 📁 Project Structure

```
unleashed-capacitor/
├── capacitor.config.json    # Capacitor settings
├── package.json             # Dependencies
├── www/                     # Web game files
│   ├── index.html           # The game (with ad containers)
│   ├── admob-native.js      # AdMob for native apps
│   ├── manifest.json        # PWA manifest
│   ├── sw.js                # Service worker
│   └── icon-*.png           # App icons
├── android/                 # Android Studio project
│   └── app/src/main/...
└── ios/                     # Xcode project
    └── App/...
```

---

## ❓ Need Help?

- **Capacitor docs**: https://capacitorjs.com/docs
- **AdSense help**: https://support.google.com/adsense
- **AdMob help**: https://support.google.com/admob
- **Play Console help**: https://support.google.com/googleplay/android-developer
