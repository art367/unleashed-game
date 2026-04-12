#!/usr/bin/env python3
"""
Patch script: Implement Option B (Funny Word Replacements) for UNLEASHED!
Replaces all expletives with family-friendly alternatives:
  fudge, flipping heck, blooming, crikey, sugar, bloomin' nora, good grief, 
  blimey, for goodness sake, oh crumbs
"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    # ==================== 1. PANIC_LINES (lines 282-287) ====================
    # Replace the entire PANIC_LINES block
    (
        r'const PANIC_LINES = \[.*?\];',
        '''const PANIC_LINES = [
  { threshold:0, lines:["{NAME}! Come here!","{NAME}! Come back!","{NAME}! Good dog, come!","{NAME}! Walkies!","{NAME}! Treat! Want a treat?"], rate:0.9, pitch:1.0 },
  { threshold:20, lines:["{NAME}!","{NAME}! Come here!","{NAME}! Bad dog!","{NAME}! No no no!","{NAME}! Come HERE!","{NAME}! Leave it!","{NAME}! DROP IT!"], rate:1.0, pitch:1.1 },
  { threshold:45, lines:["{NAME}!!","{NAME}!! COME BACK!!","{NAME}!! STOP!!","Somebody grab {NAME}!","Oh FUDGE! {NAME}!!","{NAME}! NOT THE SQUIRRELS!","LEAVE THE DUCKS ALONE {NAME}!!","Oh BLOOMIN NORA {NAME}!"], rate:1.1, pitch:1.25 },
  { threshold:70, lines:["OH CRIKEY {NAME}!!","{NAME}!! OH SUGAR!!","{NAME}!! THE DEEEEER!!","OH FLIPPING HECK!! {NAME}!!","FENTOOOON!! I mean {NAME}!!","{NAME}!! NOT THE DUCKS!!","SOMEBODY STOP THAT DOG!!","BLOOMING HECK {NAME}!!","{NAME} {NAME} {NAME}!!","OH FUDGE OH FUDGE {NAME}!!"], rate:1.3, pitch:1.45 }
];'''
    ),

    # ==================== 2. shoutName() high panic lines (>=80) ====================
    (
        "'For fucks sake ' + dogN + '!!'",
        "'Oh FUDGE ' + dogN + '!!'"
    ),
    (
        "'Bloody dog!!'",
        "'Blooming dog!!'"
    ),
    (
        "'OH MY GOD ' + dogN + '!!'",
        "'OH CRIKEY ' + dogN + '!!'"
    ),
    (
        "'SOMEBODY STOP THAT DOG!!'",
        "'SOMEBODY STOP THAT DOG!!'"  # This one is fine as-is
    ),
    (
        "dogN + '!! I SWEAR TO GOD!!'",
        "dogN + '!! OH BLOOMIN NORA!!'"
    ),
    (
        "'I AM GOING TO KILL THAT DOG!!'",
        "'I AM GOING TO BLOOMING LOSE IT!!'"
    ),

    # ==================== 3. Animal-specific shouts ====================
    # Squirrel
    (
        "'OH GOD ' + dogName + ' NOT THE SQUIRRELS!'",
        "'OH CRIKEY ' + dogName + ' NOT THE SQUIRRELS!'"
    ),
    # Duck  
    (
        "'NOT THE DUCKS ' + dogName + '!! OH GOD!!'",
        "'NOT THE DUCKS ' + dogName + '!! OH SUGAR!!'"
    ),
    # Deer
    (
        "'OH JESUS CHRIST THE DEER!!'",
        "'OH FLIPPING HECK THE DEER!!'"
    ),
    (
        "'OH GOD ' + dogName + '!! LEAVE THE DEER ALONE!!'",
        "'OH CRIKEY ' + dogName + '!! LEAVE THE DEER ALONE!!'"
    ),

    # ==================== 4. Pond shouts ====================
    (
        "'OH GOD ' + dogName + '!! NOW YOU SMELL LIKE POND!!'",
        "'OH SUGAR ' + dogName + '!! NOW YOU SMELL LIKE POND!!'"
    ),

    # ==================== 5. Park keeper caught ====================
    (
        "ownerSpeechBubble.text = 'Oh thank GOD! The keeper got ' + dogName + '!';",
        "ownerSpeechBubble.text = 'Oh THANK GOODNESS! The keeper got ' + dogName + '!';"
    ),

    # ==================== 6. Human help shouts ====================
    (
        "'THANK GOD! GRAB ' + dogName + '!'",
        "'OH THANK GOODNESS! GRAB ' + dogName + '!'"
    ),

    # ==================== 7. Poo dropped ====================
    (
        "ownerSpeechBubble.text = 'OH FOR GODS SAKE ' + dogName + '!!';",
        "ownerSpeechBubble.text = 'OH FOR GOODNESS SAKE ' + dogName + '!!';",
    ),

    # ==================== 8. Wee finished lines ====================
    (
        "'Oh for GODS sake ' + dogName + '!'",
        "'Oh for GOODNESS sake ' + dogName + '!'"
    ),

    # ==================== 9. Tree wee shouts ====================
    (
        "'Oh for GOODNESS sake ' + dogName + '! Not ANOTHER tree!'",
        "'Oh BLOOMIN NORA ' + dogName + '! Not ANOTHER tree!'"
    ),

    # ==================== 10. Park keeper warning ====================
    # This line is fine - no expletives

    # ==================== 11. Game over final line is fine ====================
    # "I am NEVER taking dogName to the park again!" - no expletives
]

count = 0
for old, new in replacements:
    if old == new:
        continue
    # Use re.DOTALL for the PANIC_LINES multiline replacement
    if 'PANIC_LINES' in old:
        new_content = re.sub(old, new, content, count=1, flags=re.DOTALL)
    else:
        new_content = content.replace(old, new, 1)
    
    if new_content != content:
        content = new_content
        count += 1
        # Extract a short preview
        preview = old[:60].replace('\n', ' ')
        print(f"  ✅ Replaced: {preview}...")
    else:
        preview = old[:60].replace('\n', ' ')
        print(f"  ⚠️  Not found: {preview}...")

# Now handle the tree wee shout that has "GOODNESS" from earlier replacement
# The line "Oh for GOODNESS sake" in tree wee section should be "Oh BLOOMIN NORA"
# But we need to be careful - let's do the specific tree wee array replacement
old_tree = "dogName + '! WE DONT WEE ON TREES!!'"
new_tree = "dogName + '! WE DO NOT WEE ON TREES!!'"
# This line is actually fine, no expletives

print(f"\n🎉 Applied {count} replacements!")
print("Option B (Funny Word Replacements) is now active!")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
