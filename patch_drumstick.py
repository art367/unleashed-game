#!/usr/bin/env python3
"""Patch: Fix drumstick scoring (dog points) + add squeaky toy (owner distraction)"""

import re

with open('index.html', 'r') as f:
    html = f.read()

# ============================================================
# 1. Add 'toy' color to COLORS config
# ============================================================
html = html.replace(
    "bone:'#F5F5DC', ball:'#9ACD32', food:'#DAA520',",
    "bone:'#F5F5DC', ball:'#9ACD32', food:'#DAA520', toy:'#FF69B4',"
)

# ============================================================
# 2. Update spawnPickup to include 'toy' type
# ============================================================
html = html.replace(
    "const type = r < 0.4 ? 'bone' : r < 0.7 ? 'ball' : 'food';",
    "const type = r < 0.25 ? 'bone' : r < 0.5 ? 'ball' : r < 0.75 ? 'food' : 'toy';"
)

# ============================================================
# 3. Fix food/drumstick scoring: DOG points, not owner
# ============================================================
old_food_case = """        case 'food':
          ownerScore += 50;
          spawnFloatText(p.x, psy, '👤+50 🍗', '#4A90D9');
          hudOwnerFlash('TREAT!');
          // Eating food triggers an urgent poo! Dog slows down, owner can catch up
          if (!dogPooing) {
            pooTimer = rand(1.5, 3.0); // poo coming VERY soon after eating
            showCombo('🍗 YUMMY! 💩 UH OH...');
            speakLine(dogName + ' NO! DONT EAT THAT! Oh no...', 1.1, 1.2);
            lastVoiceTime = Date.now();
            ownerSpeechBubble.text = dogName + '!! SPIT IT OUT!!';
            ownerSpeechBubble.timer = 2.0;
            ownerSpeechBubble.maxTimer = 2.0;


          }
          break;"""

new_food_case = """        case 'food':
          // Drumstick gives DOG points - naughty chaos!
          score += 70;
          chaosPoints += 15;
          spawnFloatText(p.x, psy, '🐕+70 🍗 NAUGHTY!', '#FF6B6B');
          hudDogFlash('YUM!');
          // Eating food triggers an urgent poo! More chaos!
          if (!dogPooing) {
            pooTimer = rand(1.5, 3.0); // poo coming VERY soon after eating
            showCombo('🍗 NAUGHTY! 💩 UH OH...');
            speakLine('NAUGHTY ' + (dogGender === 'girl' ? 'GIRL' : 'BOY') + '! LEAVE IT ' + dogName + '!', 1.1, 1.2);
            lastVoiceTime = Date.now();
            ownerSpeechBubble.text = 'NAUGHTY ' + (dogGender === 'girl' ? 'GIRL' : 'BOY') + '! LEAVE IT!';
            ownerSpeechBubble.timer = 2.0;
            ownerSpeechBubble.maxTimer = 2.0;
          }
          break;
        case 'toy':
          // Squeaky toy is an owner distraction - dog stops to play
          ownerScore += 70;
          spawnFloatText(p.x, psy, '👤+70 🧸 DISTRACTED!', '#4A90D9');
          hudOwnerFlash('SQUEAKY!');
          showCombo('🧸 SQUEAK SQUEAK!');
          speakLine(dogName + '! Look! Squeaky toy! Good ' + (dogGender === 'girl' ? 'girl' : 'boy') + '!', 1.0, 1.1);
          lastVoiceTime = Date.now();
          ownerSpeechBubble.text = 'SQUEAKY TOY ' + dogName + '! COME!';
          ownerSpeechBubble.timer = 2.0;
          ownerSpeechBubble.maxTimer = 2.0;
          // Dog slows down playing with toy
          dog.speed *= 0.45;
          setTimeout(() => { dog.speed = BREEDS[selectedBreed].speed; }, 1500);
          break;"""

html = html.replace(old_food_case, new_food_case)

# ============================================================
# 4. Add drawing code for squeaky toy
# ============================================================
old_food_draw = """    case 'food':
      // Drumstick
      ctx.fillStyle = COLORS.food;
      ctx.beginPath(); ctx.ellipse(0, 0, 16, 10, 0.3, 0, Math.PI*2); ctx.fill();
      ctx.fillStyle = '#F5F0E0';
      ctx.fillRect(14, -3.5, 14, 7);
      ctx.beginPath(); ctx.arc(28, 0, 6, 0, Math.PI*2); ctx.fill();
      break;"""

new_food_draw = """    case 'food':
      // Drumstick
      ctx.fillStyle = COLORS.food;
      ctx.beginPath(); ctx.ellipse(0, 0, 16, 10, 0.3, 0, Math.PI*2); ctx.fill();
      ctx.fillStyle = '#F5F0E0';
      ctx.fillRect(14, -3.5, 14, 7);
      ctx.beginPath(); ctx.arc(28, 0, 6, 0, Math.PI*2); ctx.fill();
      break;
    case 'toy':
      // Squeaky toy - cute rubber bone shape in pink
      ctx.fillStyle = COLORS.toy;
      // Body
      ctx.beginPath(); ctx.ellipse(0, 0, 12, 8, 0, 0, Math.PI*2); ctx.fill();
      // Left bulb
      ctx.beginPath(); ctx.arc(-14, 0, 8, 0, Math.PI*2); ctx.fill();
      // Right bulb
      ctx.beginPath(); ctx.arc(14, 0, 8, 0, Math.PI*2); ctx.fill();
      // Shine
      ctx.fillStyle = 'rgba(255,255,255,0.5)';
      ctx.beginPath(); ctx.arc(-14, -3, 3, 0, Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.arc(14, -3, 3, 0, Math.PI*2); ctx.fill();
      // Squeak lines
      ctx.strokeStyle = 'rgba(255,105,180,0.6)';
      ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.moveTo(-5, -12); ctx.lineTo(-3, -17); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(0, -11); ctx.lineTo(0, -17); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(5, -12); ctx.lineTo(3, -17); ctx.stroke();
      break;"""

html = html.replace(old_food_draw, new_food_draw)

# ============================================================
# 5. Update tutorial / How To Play screen
# ============================================================
# Move drumstick from owner section to dog section
html = html.replace(
    '<div>🍗 Dog eats treat: <b>+60</b> (at least it stopped running)</div>',
    '<div>🧸 Dog gets squeaky toy: <b>+70</b> (squeak squeak! distracted!)</div>'
)

# Add drumstick to dog scoring section
html = html.replace(
    '<div>🌳 Wee on trees: Priceless (marking territory is an art form)</div>',
    '<div>🌳 Wee on trees: Priceless (marking territory is an art form)</div>\n<div>🍗 Eat a drumstick: <b>+70</b> (naughty! leave it! 💩 incoming...)</div>'
)

# ============================================================
# 6. Add hudDogFlash function if it doesn't exist
# ============================================================
if 'function hudDogFlash' not in html:
    # Add it right after hudOwnerFlash
    html = html.replace(
        'function hudOwnerFlash(txt) {',
        """function hudDogFlash(txt) {
  const el = document.getElementById('hudDogFlash');
  if (el) { el.textContent = txt; el.style.opacity = '1'; setTimeout(() => el.style.opacity = '0', 800); }
}
function hudOwnerFlash(txt) {"""
    )

# ============================================================
# 7. Add sfx for squeaky toy (higher pitch squeak)
# ============================================================
if 'sfx_squeak' not in html:
    html = html.replace(
        'function sfx_pickup() {',
        """function sfx_squeak() { playTone(1200, 0.08, 'sine', 0.4); setTimeout(() => playTone(1500, 0.1, 'sine', 0.45), 60); setTimeout(() => playTone(1200, 0.08, 'sine', 0.35), 140); }
function sfx_pickup() {"""
    )
    # Use squeak sfx for toy pickup
    html = html.replace(
        "hudOwnerFlash('SQUEAKY!');",
        "hudOwnerFlash('SQUEAKY!');\n          sfx_squeak();"
    )

with open('index.html', 'w') as f:
    f.write(html)

print("✅ Patch applied successfully!")
print("Changes:")
print("  1. Drumstick now gives DOG +70 points (was owner +50)")
print("  2. Voice: 'NAUGHTY BOY/GIRL! LEAVE IT!'")
print("  3. New pickup: Squeaky Toy (pink rubber bone) - owner distraction +70")
print("  4. Tutorial updated with new scoring")
print("  5. Squeaky toy SFX added")
