---
name: ffmpeg-video-qa-engine
description: >-
  Production-grade FFmpeg execution rules and mandatory Post-Render Video QA Self-Critique workflow.
  Combines the Probe-Edit-Check-Look loop from GitHub kajisho5/ffmpeg-skill, zero-error FFmpeg
  recipes from n0an/ffmpeg-skill, and hard production correctness rules from video-use. Use BEFORE
  writing complex FFmpeg commands and ALWAYS AFTER rendering any short or long video to visually
  inspect a 3x3 storyboard, verify EBUR128 loudness, check A/V sync, and catch defects before
  presenting the video to the user.
---

# FFmpeg Engineering & Post-Render Video QA Engine

Never ship a video blindly. Follow the **Probe → Plan → Edit → Check → Look** loop on every render.

---

## 1. Non-Negotiable FFmpeg Production Rules (Zero-Error Recipes)

1. **Always Probe First:** Run `ffprobe` on every input before writing filtergraphs (check `width`, `height`, `r_frame_rate`, `duration`, `codec_name`, `pix_fmt`).
2. **Fast & Accurate Seeking:** Put `-ss` **before** `-i` for fast keyframe seek, and `-t` cleanly on output after normalization. Always normalize frame rate (`fps=30`) and `setsar=1` BEFORE concatenating clips with `-c copy` so timestamps never drift.
3. **Subtitles LAST in Filter Chain:** Apply `ass=` / `subtitles=` **after** all `crop`, `scale`, `overlay`, `drawbox`, and `drawtext` filters so nothing ever covers captions.
4. **Devanagari / Hindi / Indic ASS Shaping Rule:**
   - Always use native `.ass` with explicit `PlayResX` & `PlayResY` matching the video (`1080×1920` or `1920×1080`).
   - **ALWAYS set `Spacing=0`** in the ASS Style line! Any non-zero `Spacing` breaks HarfBuzz complex script shaping and renders broken dotted circles (`◌`) around Hindi matras.
5. **Zoompan Exact-FPS Rule:**
   - `zoompan` with `d=1` outputs 1 frame per input frame at its `fps` parameter. If input is 24fps and `zoompan` has `fps=30`, video speeds up 1.25x!
   - **Fix:** Always insert `fps=30` **BEFORE** `zoompan`, then `zoompan=z='1.0+0.065*min(on/{total_frames},1)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=WxH:fps=30`.
6. **True-Center Crop Rule:**
   - Never hardcode `x=8` or `x=0` when cropping widescreen to vertical! Always compute `crop_x = cx + (clean_cw - crop_w) // 2`.
   - When stripping burned-in movie subtitles from bottom of source clips, anchor crop to top `cy` and trim `15–18%` of height if 2-line English subtitles exist.
7. **Audio Outro Silence Fix (`apad` + `duration=longest`):**
   - Never use `amix=duration=first` when mixing shorter speech with longer outro BGM — it chops off the outro music into dead silence!
   - Always pad speech with `apad=whole_dur={total_dur},atrim=0:{total_dur}`, apply `sidechaincompress` to duck BGM under speech, and mix with `amix=duration=longest:normalize=0` + `alimiter=limit=0.95`.
8. **Web & Mobile Compatibility:** Always output `-pix_fmt yuv420p -movflags +faststart` with H.264 (`libx264`) and AAC (`192k`, `44100 Hz` or `48000 Hz`, stereo).
9. **FFmpeg 9.0 Compatibility:** Avoid deprecated `-vsync vfr` (use `-fps_mode vfr`) and use `-update 1` with `-frames:v 1` when exporting single JPEG/PNG stills.

---

## 2. Mandatory Post-Render Video QA Self-Critique ("Check + Look")

**Every time a video finishes rendering**, run the bundled QA script [qa_inspect_video.py](./scripts/qa_inspect_video.py) and **visually inspect the generated 3×3 storyboard image with `read_file`** before telling the user the video is ready:

```powershell
python C:\Users\shahz\.gemini\config\skills\ffmpeg-video-qa-engine\scripts\qa_inspect_video.py "<path\to\video.mp4>" --ass "<captions.ass>" --audio-report "<audio_report.json>" --clip-manifest "<clips_manifest.json>" --require-banner-ass
```

### V2 Mandatory Extra Checks (added after the Meridian audit)
1. **`qa_banner_zoom.png`** (full-width crop of the top banner, auto-generated for vertical videos): you MUST open it with `read_file` and read every Devanagari matra (`मिला`, `भविष्य` ...). The 360px storyboard tiles are far too small to prove matra correctness. Banner Hindi must come from libass (`BannerTitle`/`BannerHook` ASS styles), never from Pillow (`PILLOW_RAQM=False`).
2. **Whisper similarity report** (`--audio-report`): per-beat `similarity`, `max_gap`, `suffix_unmatched`, retries, engine. ANY beat `< 0.72`, `FAILED_QA`, cut last word or abrupt end = ISSUE; fallback voice = WARNING you must tell the user about.
3. **Clip manifest audit** (`--clip-manifest`): every clip `<= 4.5s`; lists `hflip` ON/OFF with reasons; surfaces shot-guard `BLACK_FRAME` / `POSSIBLE_CUT` probe flags.
4. **ASS audit is per style** (banner events span the whole video; only caption events are overlap-checked); `Spacing=0` on EVERY style.
5. Honest limits: automated checks measure, they cannot listen. State this and never claim "sounds good".

### Visual Self-Critique Checklist (Inspect Every Tile of the 3×3 Storyboard!)
Be brutally honest — look for defects like a critic, not the author:
- [ ] **Framing & Faces:** Are main actors centered? Is any face sliced in half at the edge?
- [ ] **Source Subtitle / Text Collisions:** Are original movie English subtitles peeking at the bottom or colliding with Hindi captions? Are mirrored logos/text (`XTK`) distracting?
- [ ] **Devanagari / Caption Quality:** Are all Hindi matras joined cleanly (no `◌` dotted circles)? Zero black opaque boxes over faces? Readable size & contrast? Zero overlapping captions?
- [ ] **Scene-to-Script Match:** Does every tile show meaningful action/emotion matching the caption — or are there empty ceilings, walls, door handles, or black transition frames?
- [ ] **Header & Safe Zones:** Does the top header stay below `y=120`? Do captions stay above `y=1660` (YouTube Shorts UI safe zone)?
- [ ] **Color & Sharpness:** Are blacks deep & crisp (not washed-out gray/muddy)? Is footage sharp?

### Technical Audio & Sync Pass Criteria
- **A/V Duration Drift:** `abs(video_dur - audio_dur) <= 0.25s`
- **Integrated Loudness (`ebur128`):** `-12.5` to `-15.5 LUFS` (Target: `-14.0 LUFS`)
- **True Peak:** `<= -1.0 dBFS` (no digital clipping)
- **Outro Last-1s Audio:** `mean_volume > -45 dB` (confirms no dead-silence outro bug)
- **ASS Subtitle Overlaps:** `overlaps == 0` and `Spacing=0` confirmed

If any check fails: **fix → re-render → re-inspect** (max 3 passes; if still imperfect, report the exact remaining issues honestly to the user).
