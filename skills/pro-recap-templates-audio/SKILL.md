---
name: pro-recap-templates-audio
description: >-
  Curated library of ready-made 9:16 & 16:9 cinema overlay templates, 100% copyright-free procedural
  BGM moods & SFX (dark_thriller, horror_suspense, emotional_drama, action_hype), free stock audio
  sources, and distilled open-source GitHub video-editing recipes (NarratoAI, MoneyPrinterTurbo,
  ClipsAI, Remotion Shorts). Activate when choosing a visual template, mood BGM, SFX, or stock audio
  for Hindi Movie Recaps and Shorts.
---

# Pro Recap Templates, Copyright-Free Audio Library & Open-Source Recipes

## 1. Ready-Made Visual Templates (`templates/` + `pipeline/template_kit.py`)
Never design a banner box from scratch when a proven template already exists! All templates are transparent PNGs with **zero Pillow Devanagari text** — Hindi Titles & Hooks are rendered cleanly on top via **`libass` (`overlay_kit.py`)**:

| Template File | Aspect | Best Genre | Style |
|---|---|---|---|
| `templates/template_dark_gold.png` | `1080×1920` (9:16) | Mystery / Sci-Fi / Thriller | Dark-glass card + Gold accent stripe + cinema frame lines |
| `templates/template_crimson_horror.png` | `1080×1920` (9:16) | Horror / Zombie / Monster | Deep crimson dark-glass card + Blood-red neon accent |
| `templates/template_cyan_scifi.png` | `1080×1920` (9:16) | Cyberpunk / Alien / Action | Dark-teal glass card + Corner HUD brackets |
| `templates/template_cinema_16x9.png` | `1920×1080` (16:9) | Long-Form Movie Explained | Filmy Nest matte-black bottom scope bar (covers original subs) + top-left genre badge |

Generate or refresh all 4 templates anytime:
```powershell
python pipeline/template_kit.py templates
```

---

## 2. Built-In 100% Copyright-Free Procedural BGM & SFX (`pipeline/music_kit.py`)
Zero copyright claims — every track is synthesized at 48kHz stereo:
- **4 BGM Moods (`mood=`):**
  1. `dark_thriller` — Hans-Zimmer style 118 BPM D-minor pulse + cello drone
  2. `horror_suspense` — 92 BPM eerie tritone drone + dark tension
  3. `emotional_drama` — 84 BPM warm minor orchestral pad swells (no heavy pulse)
  4. `action_hype` — 132 BPM fast driving synth-bass pulse
- **6 Designed SFX:** `boom`, `whoosh`, `riser`, `heartbeat`, `glitch_hit`, `bell_reveal`

---

## 3. Verified External Copyright-Free Audio & Music Sources
When you want real studio recordings alongside procedural SFX:
1. **YouTube Audio Library** (`studio.youtube.com` → Audio Library) — 100% Monetization-safe, filter by *Dark / Dramatic / Cinematic*.
2. **Pixabay Music & SFX** (`pixabay.com/music` & `pixabay.com/sound-effects`) — Royalty-free, no attribution required.
3. **Mixkit** (`mixkit.co/free-stock-music` & `free-sound-effects`) — Free cinematic impacts, risers, whooshes.
4. **Freesound.org (CC0 filter)** — Filter strictly by `Creative Commons 0 (Public Domain)` for real Foley & ambient beds.
5. **Incompetech (Kevin MacLeod, CC BY 4.0)** — Classic suspense beds (*Darkling*, *Long Note Four*, *Anxiety*) with 1-line description credit.

---

## 4. Distilled Open-Source GitHub Video Editing Best Practices
This repository combines battle-tested patterns from top open-source projects:
- **NarratoAI / AI-Movie-Shorts:** Shot-level scene detection (`PySceneDetect`) before matching narration beats — never blind fixed-interval timestamps.
- **ClipsAI:** Active-subject & multi-person wide-shot protection (`fit="wide"` for 2+ actors so no face is ever sliced).
- **Remotion Shorts:** Strict platform safe-zone enforcement (`y=135..295` header, `MarginV=305` lower-border captions clear of YT Shorts UI).
- **MoneyPrinterTurbo:** Clean modular separation of TTS → Subtitle alignment → FFmpeg composite → Audio mastering (`-14 LUFS`).
