#!/usr/bin/env python3
"""
Patch the UNLEASHED! game to use real ElevenLabs voice clips 
instead of broken browser speechSynthesis.
"""
import json, re, os

# Load the voice data
with open("voice_data.js") as f:
    voice_js = f.read()

# Read the current game file
with open("index.html") as f:
    html = f.read()

# ============================================================
# 1. Insert VOICE_CLIPS data right after PANIC_LINES constant
# ============================================================
# Find the end of PANIC_LINES definition
panic_end = html.find("];\n\nconst CHAOS_RATINGS")
if panic_end == -1:
    raise Exception("Could not find PANIC_LINES end marker")

insert_point = panic_end + 2  # after ];\n

voice_system_code = """
// ==================== REAL VOICE AUDIO SYSTEM ====================
// Pre-generated ElevenLabs v3 voice clips (male + female)
""" + voice_js + """

// Voice clip categories mapped to game events
const VOICE_CATEGORIES = {
  calm: 'calm',         // "Come here! Come back!"
  annoyed: 'annoyed',   // "Bad dog! No no no! Leave it!"
  panic: 'panic',       // "COME BACK!! STOP!!"
  ducks: 'ducks',       // "NOT THE DUCKS!!"
  omg: 'omg',           // "OH JESUS CHRIST!! OH GOD!!"
  parkkeeper: 'parkkeeper', // "Oh no! Park keeper!"
  goodboy: 'goodboy',   // "Good boy/girl!"
  food: 'food',         // "DON'T EAT THAT!"
  poo: 'poo',           // "Oh no! Not here! Not now!"
  fetch: 'fetch',       // "FETCH! Good boy!"
  tree: 'tree',         // "NOT ON THE TREE!"
  squirrels: 'squirrels', // "NOT THE SQUIRRELS!!"
  never: 'never'        // "I am never taking you to the park again"
};

// Pre-loaded Audio objects for instant playback
let voiceAudioCache = { male: {}, female: {} };
let currentVoiceAudio = null;
let lastVoicePlayTime = 0;

function preloadVoiceClips() {
  ['male', 'female'].forEach(function(gender) {
    Object.keys(VOICE_CLIPS[gender]).forEach(function(cat) {
      try {
        var audio = new Audio(VOICE_CLIPS[gender][cat]);
        audio.preload = 'auto';
        audio.volume = 1.0;
        voiceAudioCache[gender][cat] = audio;
      } catch(e) {
        console.log('[VOICE] Failed to preload', gender, cat, e);
      }
    });
  });
  console.log('[VOICE] All clips preloaded');
}

function playVoiceClip(category, volume) {
  var now = Date.now();
  // Don't overlap voice clips - minimum 800ms gap
  if (now - lastVoicePlayTime < 800) return;
  
  var gender = ownerGender || 'male';
  var clip = voiceAudioCache[gender][category];
  
  if (!clip) {
    console.log('[VOICE] No clip for', gender, category);
    return;
  }
  
  try {
    // Stop any currently playing voice
    if (currentVoiceAudio) {
      try { currentVoiceAudio.pause(); currentVoiceAudio.currentTime = 0; } catch(e) {}
    }
    
    // Clone the audio so we can play overlapping if needed
    var playable = clip.cloneNode();
    playable.volume = volume || 1.0;
    playable.play().then(function() {
      console.log('[VOICE] Playing:', category, '(' + gender + ')');
    }).catch(function(e) {
      console.log('[VOICE] Play failed:', e);
    });
    currentVoiceAudio = playable;
    lastVoicePlayTime = now;
  } catch(e) {
    console.log('[VOICE] Error playing clip:', e);
  }
}

// Map panic level to voice category for random shouts
function getShoutCategory() {
  if (panicLevel >= 70) {
    var extreme = ['omg', 'squirrels', 'ducks', 'panic'];
    return extreme[Math.floor(Math.random() * extreme.length)];
  } else if (panicLevel >= 45) {
    var high = ['panic', 'squirrels', 'annoyed', 'ducks'];
    return high[Math.floor(Math.random() * high.length)];
  } else if (panicLevel >= 20) {
    var med = ['annoyed', 'calm', 'panic'];
    return med[Math.floor(Math.random() * med.length)];
  } else {
    var low = ['calm', 'calm', 'goodboy'];
    return low[Math.floor(Math.random() * low.length)];
  }
}

"""

html = html[:insert_point] + voice_system_code + html[insert_point:]

# ============================================================
# 2. Replace the old voice functions (getOwnerVoice through speakLine)
# ============================================================
# Find and remove the old voice system code
old_voice_start = html.find("\nfunction getOwnerVoice()")
old_voice_end = html.find("\nfunction shoutName()")

if old_voice_start == -1 or old_voice_end == -1:
    raise Exception("Could not find old voice system boundaries")

# Remove old getOwnerVoice, cachedVoice, cacheVoice, speakLine
html = html[:old_voice_start] + "\n" + html[old_voice_end:]

# ============================================================
# 3. Replace the shoutName function
# ============================================================
old_shout_start = html.find("\nfunction shoutName()")
old_shout_end = html.find("\n// ==================== RESIZE")

if old_shout_start == -1 or old_shout_end == -1:
    raise Exception("Could not find shoutName boundaries")

new_shout = """
function shoutName() {
  var now = Date.now();
  var cooldown = panicLevel > 70 ? 2000 : panicLevel > 40 ? 2800 : 3500;
  if (now - lastShoutTime < cooldown) return;
  lastShoutTime = now;
  lastVoiceTime = now;

  var category = getShoutCategory();
  playVoiceClip(category, 1.0);

  // Also play a small tone as extra feedback
  if (panicLevel > 50) {
    playTone(600, 0.08, 'square', 0.1, 400);
  }
}

// Legacy speakLine wrapper - now routes to voice clips
function speakLine(text, rate, pitch, priority) {
  // Map text content to voice clip category
  var lower = (text || '').toLowerCase();
  var cat = 'calm'; // default
  
  if (lower.indexOf('park keeper') >= 0) cat = 'parkkeeper';
  else if (lower.indexOf('duck') >= 0) cat = 'ducks';
  else if (lower.indexOf('squirrel') >= 0) cat = 'squirrels';
  else if (lower.indexOf('good') >= 0 && (lower.indexOf('boy') >= 0 || lower.indexOf('girl') >= 0)) cat = 'goodboy';
  else if (lower.indexOf('fetch') >= 0 || lower.indexOf('bring it') >= 0) cat = 'fetch';
  else if (lower.indexOf('eat') >= 0 || lower.indexOf('food') >= 0 || lower.indexOf('leave the') >= 0) cat = 'food';
  else if (lower.indexOf('not here') >= 0 || lower.indexOf('not now') >= 0 || lower.indexOf('poo') >= 0) cat = 'poo';
  else if (lower.indexOf('tree') >= 0) cat = 'tree';
  else if (lower.indexOf('never') >= 0 || lower.indexOf('again') >= 0) cat = 'never';
  else if (lower.indexOf('oh my god') >= 0 || lower.indexOf('oh god') >= 0 || lower.indexOf('jesus') >= 0) cat = 'omg';
  else if (lower.indexOf('stop') >= 0 || lower.indexOf('come back') >= 0 || lower.indexOf('somebody') >= 0) cat = 'panic';
  else if (lower.indexOf('bad') >= 0 || lower.indexOf('no no') >= 0 || lower.indexOf('leave it') >= 0 || lower.indexOf('drop') >= 0) cat = 'annoyed';
  
  playVoiceClip(cat, priority ? 1.0 : 0.85);
}

"""

html = html[:old_shout_start] + new_shout + html[old_shout_end:]

# ============================================================
# 4. Add preloadVoiceClips() call in game init
# ============================================================
# Find where music is loaded or game starts
init_marker = html.find("tryPlayMusic()")
if init_marker == -1:
    init_marker = html.find("resize();")

# Find the next occurrence of a function or event listener after init
# Let's insert it right after the first tryPlayMusic call
insert_after = html.find("tryPlayMusic();")
if insert_after != -1:
    insert_after = html.find("\n", insert_after) + 1
    html = html[:insert_after] + "  preloadVoiceClips();\n" + html[insert_after:]
else:
    # Fallback: add after resize()
    resize_pos = html.find("resize();\n")
    if resize_pos != -1:
        insert_after = html.find("\n", resize_pos) + 1
        html = html[:insert_after] + "\npreloadVoiceClips();\n" + html[insert_after:]

# ============================================================
# 5. Remove speechSynthesis references that might cause errors
# ============================================================
# Remove the onvoiceschanged handler if it still exists
html = html.replace("if (typeof speechSynthesis !== 'undefined') {\n  speechSynthesis.onvoiceschanged = cacheVoice;\n  cacheVoice();\n}\n", "")

# Write the patched file
with open("index.html", "w") as f:
    f.write(html)

print(f"Patched index.html: {len(html)} chars ({len(html)/1024:.1f} KB)")
print("Voice system replaced: speechSynthesis -> real audio clips")
