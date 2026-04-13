// ==================== ADMOB NATIVE (Capacitor) ====================
// This file handles AdMob ads when running as a native app via Capacitor.
// It replaces the web-based AdSense ads with native AdMob ads for better
// performance and revenue on mobile apps.

(function() {
  'use strict';
  
  // Detect if running in Capacitor native app
  var isNative = window.Capacitor && window.Capacitor.isNativePlatform();
  if (!isNative) return; // Only run in native app context
  
  var ADMOB_CONFIG = {
    // REPLACE THESE with your actual AdMob IDs from https://admob.google.com
    android: {
      banner: 'ca-app-pub-XXXXXXXXXXXXXXXX/XXXXXXXXXX',
      interstitial: 'ca-app-pub-XXXXXXXXXXXXXXXX/XXXXXXXXXX',
      // Test IDs (use during development, remove for production):
      // banner: 'ca-app-pub-3940256099942544/6300978111',
      // interstitial: 'ca-app-pub-3940256099942544/1033173712',
    },
    ios: {
      banner: 'ca-app-pub-XXXXXXXXXXXXXXXX/XXXXXXXXXX',
      interstitial: 'ca-app-pub-XXXXXXXXXXXXXXXX/XXXXXXXXXX',
      // Test IDs (use during development, remove for production):
      // banner: 'ca-app-pub-3940256099942544/2934735716',
      // interstitial: 'ca-app-pub-3940256099942544/4411468910',
    },
    interstitialFrequency: 3,  // Show every N game overs
    consentRequired: true       // GDPR consent (EU users)
  };

  var platform = window.Capacitor.getPlatform(); // 'android' or 'ios'
  var ids = ADMOB_CONFIG[platform] || ADMOB_CONFIG.android;
  var nativeGameOverCount = 0;
  var AdMob = null;

  // Wait for Capacitor plugins to load
  document.addEventListener('DOMContentLoaded', function() {
    // Import AdMob from Capacitor Community plugin
    if (window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.AdMob) {
      AdMob = window.Capacitor.Plugins.AdMob;
      initAdMob();
    }
  });

  function initAdMob() {
    if (!AdMob) return;
    
    AdMob.initialize({
      requestTrackingAuthorization: true, // iOS ATT prompt
      initializeForTesting: false          // Set true during development
    }).then(function() {
      console.log('AdMob initialized');
      showBannerAd();
      prepareInterstitial();
    }).catch(function(err) {
      console.log('AdMob init error:', err);
    });
  }

  function showBannerAd() {
    if (!AdMob) return;
    AdMob.showBanner({
      adId: ids.banner,
      adSize: 'BANNER',          // BANNER, LARGE_BANNER, MEDIUM_RECTANGLE
      position: 'BOTTOM_CENTER', // or TOP_CENTER
      margin: 0,
      isTesting: false            // Set true during development
    }).catch(function(err) {
      console.log('Banner error:', err);
    });
  }

  function hideBannerAd() {
    if (!AdMob) return;
    AdMob.hideBanner().catch(function() {});
  }

  function prepareInterstitial() {
    if (!AdMob) return;
    AdMob.prepareInterstitial({
      adId: ids.interstitial,
      isTesting: false  // Set true during development
    }).catch(function(err) {
      console.log('Interstitial prep error:', err);
    });
  }

  function showNativeInterstitial() {
    if (!AdMob) return;
    nativeGameOverCount++;
    if (nativeGameOverCount % ADMOB_CONFIG.interstitialFrequency !== 0) return;
    
    AdMob.showInterstitial().then(function() {
      // Prepare next one
      prepareInterstitial();
    }).catch(function(err) {
      console.log('Interstitial show error:', err);
      prepareInterstitial(); // Try to prepare again
    });
  }

  // Override the web ad system with native ads
  // Hide banner during gameplay, show on menu/game over
  window._nativeAdMob = {
    showBanner: showBannerAd,
    hideBanner: hideBannerAd,
    showInterstitial: showNativeInterstitial
  };

  // Hook into game state changes
  var origStartGame = window.startGame;
  if (origStartGame) {
    window.startGame = function() {
      hideBannerAd(); // Hide banner during gameplay
      origStartGame.apply(this, arguments);
    };
  }

  var origGameOver = window.gameOver;
  if (origGameOver) {
    window.gameOver = function() {
      origGameOver.apply(this, arguments);
      showBannerAd(); // Show banner on game over
      showNativeInterstitial(); // Possibly show interstitial
    };
  }

  var origRestartGame = window.restartGame;
  if (origRestartGame) {
    window.restartGame = function() {
      origRestartGame.apply(this, arguments);
      showBannerAd(); // Show banner on menu
    };
  }

})();
