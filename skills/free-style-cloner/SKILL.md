---
name: free-style-cloner
description: 100% FREE local Reference Video Style Cloner & Pre-Render Contract Linter. Analyzes any viral reference video's frame-exact cut rhythm, pacing cadence, color grading mood, EBUR128 loudness, and layout storyboard — then transfers that editing grammar to your own original footage/script without any $25/month subscription or copyright theft.
---

# Free Local Style Cloner & Pre-Render Linter

Clone the **pacing, cut cadence, color look, and audio punch** of any top YouTube Short, Reel, or Explainer video **100% locally and free** — zero cloud credits, zero paywalls!

## Ethics & Copyright Rule
- **Transfer the editing grammar ONLY:** shot rhythm, pacing speed, color grade, caption placement, loudness target, and motion energy.
- **NEVER copy** another creator's face, voice, watermark/logo, or raw copyrighted footage.

## Step 1: Analyze Any Reference Video (1 Command)
```powershell
python pipeline/style_cloner.py path/to/reference.mp4 --out build/style_profile.json --sheet build/ref_storyboard.png
```
What `style_cloner.py` extracts automatically:
- **Exact Canvas & Frame Math:** Width × Height, Aspect Ratio (`9:16` / `16:9`), rational FPS (`30/1` or `30000/1001`), exact frame count.
- **Frame-Exact Cut Cadence:** Uses `floor(frame / fps)` math (preventing 1-frame-late drift) to measure total cuts, cuts/min, avg/median shot length, and pacing tier (`hyper_viral_shorts`, `fast_recap_retention`, `explainer_medium`, `cinematic_slow`).
- **Color Palette & FFmpeg Grade Filter:** Samples frames with FFmpeg `signalstats` (`YAVG`, `SATAVG`, `HUEMED`) and outputs a ready-to-paste `recommended_ffmpeg_grade` (`eq=... , colorbalance=... , unsharp=...`).
- **Audio Punch Profile:** EBUR128 Integrated LUFS, True Peak, and LRA target.
- **3×3 Visual Storyboard:** `ref_storyboard.png` so you can visually inspect caption height, hook card framing, and visual rhythm in 1 glance.

## Step 2: Apply the Cloned Style to Your Original Project
1. Match your shot cut window to `pacing.recommended_cut_window_sec` (e.g., `1.4s–2.2s` for viral Shorts).
2. Drop `color.recommended_ffmpeg_grade` straight into your FFmpeg video filter chain.
3. Normalize final master audio to `audio.recommended_target_lufs` (typically `-14.0 LUFS`).
4. For stylized intros, newspaper highlights, or stat cards seen in the storyboard, generate matching HTML/GSAP cards with `pipeline/html_motion.py`.

## Step 3: Mandatory Pre-Render Lint Gate (`project_linter.py`)
ALWAYS run the linter BEFORE invoking a full FFmpeg render so you catch errors in 1 second instead of after a 5-minute render:
```powershell
python pipeline/project_linter.py --manifest build/clips_manifest.json --ass build/captions.ass --video build/video_concat.mp4 --audio build/master_audio.m4a --recap --json
```
Checks enforced:
- Every referenced clip exists on disk
- Frame-aligned cut timestamps (`floor(frame/fps)`) & zero negative/overlapping durations
- Copyright-safe recap max cut cap (`<= 4.45s` when `--recap` is set)
- Devanagari ASS `Spacing=0` enforcement (zero broken Hindi matras)
- 80% title-safe horizontal margins & 9:16 Shorts bottom UI safe zone
- Audio/Video duration sync check (flags drift > `0.35s`)
- HyperFrames HTML contract rules (`--html index.html`)
