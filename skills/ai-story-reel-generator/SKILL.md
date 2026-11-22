---
name: ai-story-reel-generator
description: End-to-end production blueprint for viral 3D AI character story Reels & Shorts (modeled on @thesmartaloo "Sheru & Aloo" multi-part series). Covers consistent character prompt engineering, luxury set design (crystal palaces, Bugatti auctions), Google Flow / Veo scene animation, multi-character Hindi voice dubbing, cliffhanger scripting (Part 1, 2, 3), and official Instagram Reels auto-publishing.
---

# Viral 3D AI Character Story Reel Blueprint (Sheru & Aloo Style)

This blueprint decodes the exact production formula used by viral channels like **@thesmartaloo** (1M+ views per reel) featuring recurring anthropomorphic 3D characters like **"Sheru"** (the billionaire white lion) and **"Aloo"** (the humble, smart potato).

---

## 1. The Core Viral Elements Analyzed
* **Format:** `1080×1920` (9:16 Vertical Reel, 30fps)
* **Average Length:** 60s – 135s (Story episodes split into Parts: Part 1, Part 2, Part 3...)
* **Character Contrast (High Hook Value):**
  * **The Underdog:** Cute 3D cartoon potato in simple Indian kurta-pajama & chappals carrying a burlap sack.
  * **The Mafia Boss / Royalty:** "Sheru" — an anthropomorphic white lion in a bespoke white Italian 3-piece suit, heavy gold lion chain, Rolex watch, and gold formal shoes.
  * **The Arrogant Rival:** "Tiger" in a sparkling gold sequin/glitter tuxedo.
  * **The Host / Auctioneer:** A tuxedo-wearing bear with a microphone.
* **Extravagant Set Pieces:**
  * Crystal diamond chandelier halls surrounded by mountains of gold bars and coins.
  * Luxury opera house auctions with a **Ruby Red Diamond-encrusted Bugatti Chiron** under revolving spotlights.

---

## 2. Character Consistency Prompting (Google Flow / Imagen 3 / Flux)

### A. "The Smart Aloo" (Character Anchor)
```text
A cute expressive 3D Pixar-style anthropomorphic potato character, big warm cartoon eyes, smiling subtly, wearing a traditional dusty beige Indian kurta-pajama and brown leather sandals, carrying a heavy burlap sack slung over his shoulder, standing in a grand luxury hall, soft cinematic studio lighting, Octane Render 3D style, Disney Pixar aesthetic, hyper-detailed texture, 8k resolution --ar 9:16
```

### B. "Sheru" (Billionaire White Lion)
```text
A majestic anthropomorphic white male lion with a full thick snowy white mane, sharp intelligent golden eyes, tall muscular build, dressed in an immaculate bespoke white three-piece tuxedo suit, tailored white vest, thick heavy gold Cuban link chain with a lion-head medallion, gold watch, gold formal dress shoes, standing confidently, opulent crystal chandelier background, ultra-photorealistic fur and cloth physics, 8k --ar 9:16
```

### C. "Tiger" (The Arrogant Rival)
```text
An arrogant anthropomorphic Bengal tiger with sharp orange and black stripes, wearing an extravagant sparkling gold-glitter sequin tuxedo jacket with satin black lapels, gold tie, looking shocked and fainting in disbelief, opera auction stage background with flashbulbs --ar 9:16
```

### D. The Scene (Red Diamond Bugatti Auction)
```text
A dazzling ruby-red diamond-encrusted Bugatti Chiron sports car sparkling on a revolving center stage of a grand royal opera theater, surrounded by flash photography from an audience of suited animal dignitaries, dramatic overhead theater spotlights, cinematic composition, photorealistic 8k --ar 9:16
```

---

## 3. Motion & Animation (Google Flow / Veo 2 MCP)
Using our connected `google-flow` MCP server:
* Generate 4–6 second video clips with slow, deliberate camera movements:
  * *"Slow cinematic push-in on the white lion in a white suit as he raises his hand to place a winning bid, crowd reacts in awe, 4k 30fps."*
  * *"The potato character smiles proudly, nodding while holding his sack of gold."*
  * *"The tiger in the gold suit stumbles backward in dramatic slow-motion shock, jaw dropping."*

---

## 4. Multi-Character Hindi Voice Dubbing
Assign distinct voice personalities:
1. **Aloo:** Higher pitch, innocent, witty, fast colloquial Hindi (`hi-IN-SwaraNeural` or high-pitched OmniVoice).
2. **Sheru:** Deep, commanding, baritone royal gangster voice (`hi-IN-MadhurNeural` pitched down -2 semitones or deep OmniVoice clone).
3. **Tiger:** Sharp, arrogant, squeaky when losing.
4. **Auctioneer:** Fast-paced, dramatic sports/auction cadence.

---

## 5. Story Hook & Cliffhanger Structure
* **0–3s Hook:** Show the unbelievable visual (e.g. *"Sheru ne Red Diamond Bugatti ke liye 500 Crore ki boli lagayi!"*).
* **3–60s Conflict:** Rivalry between Tiger and Sheru bidding back and forth until the rival collapses in shock.
* **60–120s Next Mission:** Sheru and Aloo set off on their next secret test (e.g. *"Ab gaon chalte hain Aloo ki biwi ka test lene!"*).
* **Ending Call-to-Action:** High-retention open loop: *"Kya Aloo test pass kar payega? Part 4 ke liye abhi Follow karein!"*

---

## 6. Official Instagram Auto-Publishing (`pipeline/instagram_upload.py`)
```powershell
python pipeline/instagram_upload.py `
  --url "https://your-public-storage.com/sheru_part3.mp4" `
  --caption "Sheru ki boli se Tiger behosh! 😱💎 Part 3 🔥`n`nRed Diamond Bugatti ki neelami mein Sheru ne lagayi aisi boli! Ab Aloo ka agla test kya hoga? Part 4 ke liye Follow karein! 🚀`n`n#Aloo #Sheru #aivideos #viralreels #foryoupage"
```
Zero shadowban risk, 100% compliant with Meta's Official Content Publishing API.
