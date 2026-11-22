---
name: hyperframes-motion-bridge
description: Hybrid Studio Motion Graphics workflow combining open-source HTML/CSS/GSAP deterministic MP4 rendering (HyperFrames contract) with our fast Python/FFmpeg pipeline. Use when creating After Effects-grade title intros, glassmorphism hook cards, Vox-style newspaper highlights, animated stat counters, charts, or blank-screen explainer visuals for Shorts (9:16) and Long-Form (16:9) videos — 100% free and local with zero paywall.
---

# HyperFrames Motion Bridge (Hybrid HTML/GSAP + FFmpeg Studio)

Use **HTML + CSS + GSAP** for high-impact motion graphics, intros, explainers, charts, and blank-screen title cards — while keeping our **Python + FFmpeg + Whisper Audio Guard + HarfBuzz** pipeline for fast footage cutting, Hindi captions, and 120+ copyright-free audio!

## When to Use Which Engine
| Task | Best Engine | Why |
| :--- | :--- | :--- |
| Movie recaps, fast footage cuts, 12–22 min videos, Hindi pop captions, voice QA | **Python + FFmpeg (`smart_editor.py`, `overlay_kit.py`, `audio_guard.py`)** | 10× faster on CPU/GPU, native HarfBuzz Devanagari, Whisper QA gate. |
| Pro intro cards, Vox newspaper highlights, animated stat counters, glassmorphism hooks, data charts, kinetic 3D titles | **HTML/CSS/GSAP (`pipeline/html_motion.py` or local free `npx hyperframes render`)** | After Effects-grade easing, clean typography, instant 1-line variable edits. |

## The 10 Hard HTML-to-MP4 Contract Rules (Deterministic Rendering)
Whenever writing or editing an HTML motion scene (`index.html` or `compositions/*.html`), ALWAYS enforce these rules (verified by `pipeline/project_linter.py --html`):
1. **Root duration:** Root `#root` MUST declare `data-composition-id`, `data-width`, `data-height`, `data-fps`, and `data-duration` (in seconds).
2. **Clip timing:** Every timed block uses `class="clip" data-start="<sec>" data-duration="<sec>"` — frame-aligned using `floor(frame / fps)`.
3. **Paused seekable timeline:** Build ONE paused GSAP timeline (`const tl = gsap.timeline({ paused: true })`) and expose `window.__timelines["main"] = tl`.
4. **Zero non-determinism:** NEVER use `Date.now()`, unseeded `Math.random()`, `setTimeout`, network fetches inside frame callbacks, or infinite `repeat: -1`.
5. **No transform fighting:** Never mix CSS `transform` with GSAP transforms on the same element; animate transforms (`x`, `y`, `scale`, `rotate`), not `top`/`left`/`width`/`height`.
6. **Editable variables:** Mark swappable headlines, badges, and media with `data-var-text` / `data-var-src` so future revisions only touch 1 line.
7. **Audio IDs:** Every `<audio>` tag MUST have an explicit `id` attribute (or it will be omitted from the mix).
8. **Relative asset paths:** Always use `assets/...` (never leading `/assets/...`).
9. **Safe Zones:** Keep all visuals inside the **90% action-safe box** and all key text/captions inside the **80% title-safe box** (for 9:16 Shorts, keep bottom 20% clear for UI buttons).
10. **Zero Paywall / Zero Pro Lock:** NEVER trigger paid cloud commands (`billing subscribe`, `reverse start`, `templates pull`). Use local free `pipeline/html_motion.py` + `npx hyperframes render` (local CLI) + `pipeline/style_cloner.py` instead!

## Quick Production Workflow
1. **Generate an editable HTML/GSAP motion card (4 built-in presets):**
   ```powershell
   python pipeline/html_motion.py --template glass_hook --title "असली राज़ अब खुला!" --subtitle "1947 की वो रात..." --badge "MYSTERY" --aspect 9:16 --duration 4 --out-dir build/intro_card --render --engine auto
   ```
   Available presets: `glass_hook`, `vox_newspaper`, `stat_counter`, `kinetic_title`.
2. **Lint BEFORE final assembly:**
   ```powershell
   python pipeline/project_linter.py --html build/intro_card/index.html --json
   ```
3. **Composite seamlessly into your FFmpeg video:**
   Concat or overlay the rendered MP4 card onto your main timeline, mix with `pipeline/audio_lab.py` SFX (`whoosh_cut` / `boom_impact`), and run `ffmpeg-video-qa-engine` post-render QA!
