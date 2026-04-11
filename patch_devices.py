#!/usr/bin/env python3
"""
Patch UNLEASHED! game for:
1. Cross-device voice compatibility (iOS Safari, Android, all browsers)
2. Music fade-in on game start, fade-out on game end
"""

import re

with open('/home/user/unleashed-deploy/index.html', 'r') as f:
    code = f.read()

# ============================================================
# PATCH 1: Replace the voice system (lines 220-340) with a 
# robust cross-device version
# ============================================================

old_voice_section = '''// Uses the browser's built-in text-to-speech for that funny electronic voice
var lastShoutTime = 0;

function getOwnerVoice() {
  if (typeof speechSynthesis === 'undefined') return null;
  var voices = speechSynthesis.getVoices();
  if (typeof ownerGender !== 'undefined' && ownerGender === 'female') {
    // Try to find a distinctly female voice - prioritize voices with female/woman/fiona/samantha/victoria/karen in the name
    return voices.find(function(v) { return v.lang.includes('en') && /female|woman|fiona|samantha|victoria|karen|zira|hazel|susan/i.test(v.name); })
      || voices.find(function(v) { return v.lang.includes('en-GB') && !/male|daniel|george|james/i.test(v.name) && /female|woman/i.test(v.name); })
      || voices.find(function(v) { return v.lang.includes('en') && !/male|daniel|george|james/i.test(v.name) && v.name.toLowerCase().includes('female'); })
      || voices.find(function(v) { return v.lang.includes('en-GB'); })
      || voices.find(function(v) { return v.lang.includes('en'); });
  } else {
    // Male voice - DO NOT CHANGE THIS
    return voices.find(function(v) { return v.lang.includes('en-GB') && v.name.toLowerCase().includes('male'); })
      || voices.find(function(v) { return v.name.toLowerCase().includes('male') && v.lang.includes('en'); })
      || voices.find(function(v) { return v.lang.includes('en-GB'); })
      || voices.find(function(v) { return v.lang.includes('en'); });
  }
}

function speakLine(text, rate, pitch) {
  if (!text) return;
  if (typeof speechSynthesis === 'undefined') return;
  try {
    speechSynthesis.cancel();
    var utter = new SpeechSynthesisUtterance(text);
    var voice = getOwnerVoice();
    if (voice) utter.voice = voice;
    if (typeof ownerGender !== 'undefined' && ownerGender === 'female') {
      // Female voice: higher pitch + slightly faster rate for a distinctly different sound
      utter.rate = (rate || 1.0) * 1.15;
      utter.pitch = (pitch || 1.0) * 1.5;
    } else {
      // Male voice - DO NOT CHANGE THIS
      utter.rate = rate || 1.0;
      utter.pitch = pitch || 1.0;
    }
    utter.volume = 1.0;
    speechSynthesis.speak(utter);
  } catch(e) {}
}'''

new_voice_section = '''// Uses the browser's built-in text-to-speech for that funny electronic voice
// Cross-device compatible: iOS Safari, Android Chrome, desktop browsers
var lastShoutTime = 0;
var cachedVoices = [];
var voicesLoaded = false;
var speechUnlocked = false; // tracks if user gesture has unlocked speech

// Load voices - handles async loading on all platforms
function loadVoices() {
  if (typeof speechSynthesis === 'undefined') return;
  var v = speechSynthesis.getVoices();
  if (v && v.length > 0) {
    cachedVoices = v;
    voicesLoaded = true;
  }
}

// iOS Safari & Chrome load voices asynchronously
if (typeof speechSynthesis !== 'undefined') {
  loadVoices(); // try immediately
  if (speechSynthesis.onvoiceschanged !== undefined) {
    speechSynthesis.onvoiceschanged = function() { loadVoices(); };
  }
  // Fallback: poll for voices (some Android browsers need this)
  var voicePollCount = 0;
  var voicePoll = setInterval(function() {
    loadVoices();
    voicePollCount++;
    if (voicesLoaded || voicePollCount > 20) clearInterval(voicePoll);
  }, 250);
}

function getOwnerVoice() {
  if (!voicesLoaded) loadVoices(); // try again
  var voices = cachedVoices;
  if (!voices || voices.length === 0) return null;
  if (typeof ownerGender !== 'undefined' && ownerGender === 'female') {
    // Try to find a distinctly female voice
    return voices.find(function(v) { return v.lang.includes('en') && /female|woman|fiona|samantha|victoria|karen|zira|hazel|susan/i.test(v.name); })
      || voices.find(function(v) { return v.lang.includes('en-GB') && !/male|daniel|george|james/i.test(v.name) && /female|woman/i.test(v.name); })
      || voices.find(function(v) { return v.lang.includes('en') && !/male|daniel|george|james/i.test(v.name) && v.name.toLowerCase().includes('female'); })
      || voices.find(function(v) { return v.lang.includes('en-GB'); })
      || voices.find(function(v) { return v.lang.includes('en'); });
  } else {
    // Male voice - DO NOT CHANGE THIS
    return voices.find(function(v) { return v.lang.includes('en-GB') && v.name.toLowerCase().includes('male'); })
      || voices.find(function(v) { return v.name.toLowerCase().includes('male') && v.lang.includes('en'); })
      || voices.find(function(v) { return v.lang.includes('en-GB'); })
      || voices.find(function(v) { return v.lang.includes('en'); });
  }
}

function speakLine(text, rate, pitch) {
  if (!text) return;
  if (typeof speechSynthesis === 'undefined') return;
  try {
    // iOS Safari fix: cancel any pending speech first
    speechSynthesis.cancel();
    
    var utter = new SpeechSynthesisUtterance(text);
    var voice = getOwnerVoice();
    if (voice) utter.voice = voice;
    if (typeof ownerGender !== 'undefined' && ownerGender === 'female') {
      // Female voice: higher pitch + slightly faster rate for a distinctly different sound
      utter.rate = (rate || 1.0) * 1.15;
      utter.pitch = (pitch || 1.0) * 1.5;
    } else {
      // Male voice - DO NOT CHANGE THIS
      utter.rate = rate || 1.0;
      utter.pitch = pitch || 1.0;
    }
    utter.volume = 1.0;
    
    // iOS Safari workaround: speech sometimes gets stuck in a paused state
    // Resume before speaking to clear any stuck state
    if (speechSynthesis.paused) {
      speechSynthesis.resume();
    }
    
    speechSynthesis.speak(utter);
    speechUnlocked = true;
    
    // iOS Safari bug: long utterances get cut off after ~15 seconds
    // Set up a resume interval for this utterance
    var resumeTimer = setInterval(function() {
      if (!speechSynthesis.speaking) {
        clearInterval(resumeTimer);
      } else {
        speechSynthesis.pause();
        speechSynthesis.resume();
      }
    }, 10000);
    
    // Clean up timer when utterance ends
    utter.onend = function() { clearInterval(resumeTimer); };
    utter.onerror = function() { clearInterval(resumeTimer); };
  } catch(e) {}
}'''

assert old_voice_section in code, "Could not find old voice section!"
code = code.replace(old_voice_section, new_voice_section)

# ============================================================
# PATCH 2: Remove the OLD voice preload section (now handled above)
# ============================================================

old_preload = '''// Pre-load voices (browsers load them asynchronously)
if (typeof speechSynthesis !== 'undefined') {
  speechSynthesis.getVoices();
  if (speechSynthesis.onvoiceschanged !== undefined) {
    speechSynthesis.onvoiceschanged = function() { speechSynthesis.getVoices(); };
  }
}'''

code = code.replace(old_preload, '// Voice preloading handled in voice system above')

# ============================================================
# PATCH 3: Replace tryPlayMusic with fade-in version
# ============================================================

old_tryPlayMusic = '''function tryPlayMusic() {
  // Attempt to start music - call this on any user interaction
  ensureAudio();
  initBgMusic();
  if (bgMusicAudio && !musicStarted) {
    bgMusicAudio.volume = 0.35;
    const playPromise = bgMusicAudio.play();
    if (playPromise !== undefined) {
      playPromise.then(() => {
        musicStarted = true;
        musicPlaying = true;
        console.log("Music started successfully!");
      }).catch(e => {
        console.log("Music play blocked, will retry on next interaction:", e.message);
      });
    }
  } else if (bgMusicAudio && musicStarted && bgMusicAudio.paused) {
    // Music was started before but got paused somehow - resume it
    bgMusicAudio.volume = 0.35;
    bgMusicAudio.play().catch(e => {});
    musicPlaying = true;
  }
}'''

new_tryPlayMusic = '''var musicFadeInterval = null;

function fadeInMusic(targetVol, durationMs) {
  // Smoothly fade in music from 0 to targetVol
  if (!bgMusicAudio) return;
  if (musicFadeInterval) clearInterval(musicFadeInterval);
  var startVol = 0;
  bgMusicAudio.volume = startVol;
  var steps = Math.floor(durationMs / 50);
  var stepSize = targetVol / steps;
  var currentStep = 0;
  musicFadeInterval = setInterval(function() {
    currentStep++;
    var newVol = Math.min(startVol + stepSize * currentStep, targetVol);
    if (bgMusicAudio && !gameMuted) bgMusicAudio.volume = newVol;
    if (currentStep >= steps) {
      clearInterval(musicFadeInterval);
      musicFadeInterval = null;
    }
  }, 50);
}

function fadeOutMusic(durationMs, callback) {
  // Smoothly fade out music then pause
  if (!bgMusicAudio) { if (callback) callback(); return; }
  if (musicFadeInterval) clearInterval(musicFadeInterval);
  var startVol = bgMusicAudio.volume;
  if (startVol <= 0) { if (callback) callback(); return; }
  var steps = Math.floor(durationMs / 50);
  var stepSize = startVol / steps;
  var currentStep = 0;
  musicFadeInterval = setInterval(function() {
    currentStep++;
    var newVol = Math.max(startVol - stepSize * currentStep, 0);
    if (bgMusicAudio) bgMusicAudio.volume = newVol;
    if (currentStep >= steps) {
      clearInterval(musicFadeInterval);
      musicFadeInterval = null;
      if (bgMusicAudio) {
        bgMusicAudio.volume = 0;
        bgMusicAudio.pause();
      }
      musicPlaying = false;
      musicStarted = false;
      if (callback) callback();
    }
  }, 50);
}

function tryPlayMusic() {
  // Attempt to start music - call this on any user interaction
  ensureAudio();
  initBgMusic();
  if (bgMusicAudio && !musicStarted) {
    bgMusicAudio.volume = 0; // start silent for fade-in
    var playPromise = bgMusicAudio.play();
    if (playPromise !== undefined) {
      playPromise.then(function() {
        musicStarted = true;
        musicPlaying = true;
        // Fade in over 2 seconds
        fadeInMusic(0.35, 2000);
      }).catch(function(e) {
        console.log("Music play blocked, will retry on next interaction:", e.message);
      });
    }
  } else if (bgMusicAudio && musicStarted && bgMusicAudio.paused) {
    // Music was started before but got paused somehow - resume with fade
    bgMusicAudio.volume = 0;
    bgMusicAudio.play().catch(function(e) {});
    musicPlaying = true;
    fadeInMusic(0.35, 2000);
  }
}'''

assert old_tryPlayMusic in code, "Could not find old tryPlayMusic!"
code = code.replace(old_tryPlayMusic, new_tryPlayMusic)

# ============================================================
# PATCH 4: Replace stopMusic with proper fade-out
# ============================================================

old_stopMusic = '''function stopMusic() {
  musicPlaying = false;
  if (bgMusicAudio) {
    // Fade out over 1 second
    let vol = bgMusicAudio.volume;
    const fadeOut = setInterval(() => {
      vol -= 0.02;
      if (vol <= 0) {
        bgMusicAudio.volume = 0;
        bgMusicAudio.pause();
        clearInterval(fadeOut);
      } else {
        bgMusicAudio.volume = vol;
      }
    }, 50);
  }
}'''

new_stopMusic = '''function stopMusic() {
  // Fade out over 2 seconds then pause
  fadeOutMusic(2000);
}'''

assert old_stopMusic in code, "Could not find old stopMusic!"
code = code.replace(old_stopMusic, new_stopMusic)

# ============================================================
# PATCH 5: Update startGame to unlock speech on iOS properly
# ============================================================

old_startGame_speech = '''  // IMMEDIATELY play a voice clip on start - this is the user's click so audio is unlocked
  preloadVoiceClips();
  // Unlock speechSynthesis with initial speak
  if (typeof speechSynthesis !== 'undefined') {
    speechSynthesis.cancel();
    speechSynthesis.getVoices();
    var testUtter = new SpeechSynthesisUtterance(dogName + '!');
    testUtter.volume = 0.01; // near-silent unlock
    testUtter.rate = 2.0;
    speechSynthesis.speak(testUtter);
  }
  // Preload voice clips for the selected gender
  preloadVoiceClips();'''

new_startGame_speech = '''  // Unlock speechSynthesis on user gesture (critical for iOS Safari)
  if (typeof speechSynthesis !== 'undefined') {
    speechSynthesis.cancel();
    loadVoices(); // ensure voices are loaded
    // iOS Safari requires an actual utterance from user gesture to unlock speech
    var unlockUtter = new SpeechSynthesisUtterance('.');
    unlockUtter.volume = 0.01; // near-silent
    unlockUtter.rate = 3.0; // fast so it's barely audible
    speechSynthesis.speak(unlockUtter);
    speechUnlocked = true;
  }'''

assert old_startGame_speech in code, "Could not find old startGame speech section!"
code = code.replace(old_startGame_speech, new_startGame_speech)

# ============================================================
# PATCH 6: Update gameOver to fade out music
# ============================================================

old_gameover_music = '''  state = 'gameover';
  // Music keeps playing through game over screen
  // Voice cleanup on game over'''

new_gameover_music = '''  state = 'gameover';
  // Fade out music over 2 seconds on game over
  stopMusic();
  // Voice cleanup on game over'''

assert old_gameover_music in code, "Could not find gameOver music section!"
code = code.replace(old_gameover_music, new_gameover_music)

# ============================================================
# PATCH 7: Update restartGame to NOT say music keeps playing
#           (since it now fades out on game over)
# ============================================================

old_restart = '''function restartGame() {
  // Go back to the menu screen so player can choose breed/name/gender again
  state = 'menu';
  document.getElementById('gameOverScreen').classList.remove('active');
  document.getElementById('menuScreen').classList.add('active');
  // Music keeps playing through the menu
}'''

new_restart = '''function restartGame() {
  // Go back to the menu screen so player can choose breed/name/gender again
  state = 'menu';
  document.getElementById('gameOverScreen').classList.remove('active');
  document.getElementById('menuScreen').classList.add('active');
  // Music will restart with fade-in when they start a new game
}'''

assert old_restart in code, "Could not find restartGame!"
code = code.replace(old_restart, new_restart)

# ============================================================
# PATCH 8: Replace the bottom-of-file warmup and voice sections
#           with a more robust cross-device version
# ============================================================

old_bottom = '''// Pre-load voices
// Voice clips preloaded via preloadVoiceClips()
// Also preload speechSynthesis voices
if (typeof speechSynthesis !== 'undefined') {
  speechSynthesis.getVoices();
  speechSynthesis.onvoiceschanged = function() { speechSynthesis.getVoices(); };
  // Chrome bug: periodically resume to prevent speech from stopping
  setInterval(function() {
    if (typeof speechSynthesis !== 'undefined' && speechSynthesis.speaking) {
      speechSynthesis.resume();
    }
  }, 5000);
}

requestAnimationFrame(gameLoop);

// Warm up audio on ANY user interaction - browsers require gesture for audio playback
['click', 'touchstart', 'touchend', 'mousedown', 'keydown'].forEach(function(evt) {
  document.addEventListener(evt, function audioWarmup() {
    ensureAudio();
    // Warm up speechSynthesis
    try {
      if (typeof speechSynthesis !== 'undefined') {
        speechSynthesis.getVoices();
        var warmupUtter = new SpeechSynthesisUtterance('');
        warmupUtter.volume = 0;
        speechSynthesis.speak(warmupUtter);
        speechSynthesis.cancel();
      }
    } catch(e) {}
  }, { once: true });
});

// Start music on ANY user interaction (menu screen) - browsers require gesture for audio
document.addEventListener('click', function() { tryPlayMusic(); });
document.addEventListener('touchstart', function() { tryPlayMusic(); }, { passive: true });
document.addEventListener('keydown', function() { tryPlayMusic(); });'''

new_bottom = '''// Chrome/Edge bug: periodically resume to prevent speech from stopping after ~15s
if (typeof speechSynthesis !== 'undefined') {
  setInterval(function() {
    if (speechSynthesis.speaking) {
      speechSynthesis.resume();
    }
  }, 5000);
}

requestAnimationFrame(gameLoop);

// ==================== CROSS-DEVICE AUDIO WARMUP ====================
// Handles iOS Safari, Android Chrome, Firefox, Edge, and desktop browsers
// All require a user gesture to unlock audio playback

var audioWarmedUp = false;

function warmupAllAudio() {
  if (audioWarmedUp) return;
  audioWarmedUp = true;
  
  // 1. Warm up AudioContext (for sound effects)
  ensureAudio();
  if (audioCtx && audioCtx.state === 'suspended') {
    audioCtx.resume().catch(function() {});
  }
  
  // 2. Warm up speechSynthesis (critical for iOS Safari)
  try {
    if (typeof speechSynthesis !== 'undefined') {
      loadVoices();
      // iOS needs an actual utterance from a gesture to unlock
      var warmupUtter = new SpeechSynthesisUtterance('');
      warmupUtter.volume = 0;
      warmupUtter.rate = 2;
      speechSynthesis.speak(warmupUtter);
      // Small delay then cancel to avoid queueing issues
      setTimeout(function() { speechSynthesis.cancel(); }, 100);
    }
  } catch(e) {}
  
  // 3. Warm up music audio element
  initBgMusic();
}

// Warm up on first user interaction (covers all gesture types)
['click', 'touchstart', 'touchend', 'mousedown', 'keydown'].forEach(function(evt) {
  document.addEventListener(evt, function firstInteraction() {
    warmupAllAudio();
    document.removeEventListener(evt, firstInteraction);
  }, { passive: true });
});

// iOS Safari specific: also try to resume AudioContext on visibility change
document.addEventListener('visibilitychange', function() {
  if (!document.hidden && audioCtx && audioCtx.state === 'suspended') {
    audioCtx.resume().catch(function() {});
  }
  // Resume speech if it was interrupted by tab switch
  if (!document.hidden && typeof speechSynthesis !== 'undefined' && speechSynthesis.paused) {
    speechSynthesis.resume();
  }
});

// Start music on user interaction from menu screen (with fade-in)
document.addEventListener('click', function() { if (state === 'menu' || state === 'playing') tryPlayMusic(); });
document.addEventListener('touchstart', function() { if (state === 'menu' || state === 'playing') tryPlayMusic(); }, { passive: true });
document.addEventListener('keydown', function() { if (state === 'menu' || state === 'playing') tryPlayMusic(); });'''

assert old_bottom in code, "Could not find old bottom section!"
code = code.replace(old_bottom, new_bottom)

# ============================================================
# Write the patched file
# ============================================================

with open('/home/user/unleashed-deploy/index.html', 'w') as f:
    f.write(code)

print("SUCCESS! All patches applied:")
print("1. Cross-device voice system (iOS Safari, Android, desktop)")
print("   - Cached voices with async loading + polling fallback")
print("   - iOS Safari speech unlock on user gesture")
print("   - iOS pause/resume workaround for stuck speech")
print("   - Chrome resume interval to prevent 15s cutoff")
print("   - Visibility change handler for tab switching")
print("2. Music fade-in (2 seconds) on game start")
print("3. Music fade-out (2 seconds) on game over")
print("4. Comprehensive audio warmup for all device types")
print("5. Male voice: UNCHANGED")
print("6. Female voice: UNCHANGED (1.5x pitch, 1.15x rate)")
