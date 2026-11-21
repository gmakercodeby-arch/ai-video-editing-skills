---
name: viral-shorts-mastery
description: >-
  End-to-end blueprint for producing high-retention viral YouTube Shorts, Instagram Reels,
  and Hindi Movie Recap Shorts (1080x1920 @ 30fps). Combines best practices from top GitHub
  automation frameworks (Remotion Shorts, NarratoAI, ClipsAI, AI-Movie-Shorts, MoneyPrinterTurbo)
  and top Hindi recap channels (@MUNDAEXPLAIN style): 0-3s hook, 1.4-2.2s dynamic sub-cuts,
  face-centered smart vertical framing, word-synced Devanagari ASS pop captions, cinema BGM + SFX,
  and platform safe-zone enforcement. Activate whenever designing, scripting, editing, or
  upgrading vertical short-form videos or movie recap Shorts.
---

# Viral Shorts & Hindi Movie Recap Mastery

Use this skill when building, editing, scripting, or reviewing vertical short-form videos (`1080x1920`, `30fps`, **sweet-spot target `50–60s`** for tight viral retention; tight `0.10–0.15s` inter-sentence gaps and a crisp **`0.8s` smooth outro fade** — never leave a dragging 2s+ tail).

---

## 1. How Top Viral Movie-Recap Shorts Channels Actually Build Videos
Top channels (e.g., `@MUNDAEXPLAIN` and million-view Hindi recap Shorts) follow a strict retention formula — **every second must earn the next second**:

1. **0–3s Instant Conflict Hook (Zero Intro / Zero Logo)**
   - Drop directly into the peak danger/mystery frame (*"ट्रेन के कांच पर सैकड़ों ज़ोंबी टूट पड़े..."*).
   - Pair frame `0.0s` with a **sub-bass impact hit** and immediate bold visual action.
2. **Hyper-Paced Micro-Cuts (1.4s – 2.2s ideal, HARD CAP `<= 4.5s`)**
   - **Never let any single continuous shot exceed `4.5s`** (if a beat runs longer, ALWAYS split across 2 angles or a `1.12x` dramatic punch-in close-up) with subtle **Ken Burns slow zoom-in** (`1.00x -> 1.065x`) — never circular wobble.
3. **Literal Visual-to-Narration Match (Zero Random B-Roll)**
   - Whatever the narrator mentions (*"पानी की बोतल"*, *"अखबार"*, *"रोती हुई बच्ची"*), the viewer MUST see that exact object/action on screen.
   - Never blindly pick timestamps without inspecting keyframes first; empty ceiling/wall/handle shots kill retention immediately.
4. **Cliffhanger / Open-Loop Ending**
   - Build accelerating tension in the final 25% (riser + heartbeat acceleration) and end on a twist or unanswered question that triggers re-watches & comments.
5. **Transformative Copyright Protection**
   - Mute 100% of original movie audio (narration + custom BGM + SFX only).
   - Fragmented non-consecutive cuts (`<= 4.5s` hard max) + **`hflip` default ON for real movies** (only skip on shots with prominent readable text/signs; ALWAYS strip/crop burned-in movie subtitles first with `15–18%` bottom trim) + `1.03x` temporal speed shift (`setpts=PTS/1.03`) + Cold Teal/Pop cinema color grade + micro-sharpening + subtle grain (`noise=c0s=1.4:c0f=t+u`).

---

## 2. Smart Vertical Framing & Platform Safe Zones (1080×1920)
Inspired by **ClipsAI / NarratoAI** active-subject reframing and **Remotion Shorts** safe-zone checks:

- **Never crop from an edge (`x=8`) & Protect 2-Person Wide Shots!** Always compute **true-center** (`x = cx + (cw - crop_w) // 2`) or **face-tracked center**. For **2-person wide shots**, use wider framing / slightly zoomed-out crop (`16:9` or `4:3` wider window inside the cinema box) or smart dual-subject centering so side characters' faces are NEVER sliced in half!
- **Primary Locked Layout (Black-Bar Cinema + Top Hook Banner + Lower-Border Big Captions):**
  1. **Clean Cinema Window (`1080×1120` at `y=340..1460`) on Pure Pitch-Black (`#000000`)** — zero blurred clutter, aggressive **Cold Teal + Vivid Pop Cinema LUT + Topaz-style Unsharp Mask (`unsharp=5:5:1.15:3:3:0.4`)** for 4K trailer clarity + strong Content-ID transformation.
  2. **Mandatory Top Hook Banner (`y=135..295`):** Sleek dark translucent glass bar + thin gold/red accent stripe + bold white **Movie Title** + warm golden **Hindi Hook Header** (0-second scroll stopper, safely below `y=120` mobile status bar).
  3. **Lower Dark Border Subtitles Zone (`y=1510..1635`, `MarginV=295–315`):** Place big, ultra-clean captions **BELOW the video frame** inside the lower black border — zero overlap with actors' faces and safely above YouTube Shorts bottom UI (`y=1660..1920`).
- **YouTube Shorts / Reels Safe Zones (`1080×1920`):**
  - `y = 0..120`: Mobile status bar & top Shorts search/camera icons → **Keep clear.**
  - `y = 125..255`: **Sleek Hook Header Zone** (dark translucent glass bar + thin gold/red accent stripe + bold white title + warm gold Hindi hook; never harsh 2010 flat yellow boxes).
  - `y = 265..1545`: **Primary Visual Cinema Canvas** (actors' faces stay in middle `y=450..1350`).
  - `y = 1560..1650`: **Viral Subtitles Safe Zone** (`MarginV=295–315` in PlayRes 1920) → cleanly BELOW actors' faces and ABOVE YouTube Shorts' bottom channel/caption UI (`y=1660..1920`).
  - `x = 920..1080, y = 1000..1660`: Right-side Like/Comment/Share buttons → keep text centered with `MarginL=65, MarginR=65`.

---

## 3. Viral Hindi / Devanagari ASS Subtitle Rules
- Always generate native **`.ass`** with `PlayResX: 1080` and `PlayResY: 1920` (never rely on `.srt` `force_style` virtual 384×288 scaling).
- **CRITICAL DEVANAGARI RULE:** Always set **`Spacing=0`** in the ASS `[V4+ Styles]` line! Any non-zero `Spacing` (e.g., `1.0`) breaks libass/HarfBuzz complex script shaping and inserts broken dotted circles (`◌`) between Hindi matras.
- **Zero Black Box & Bigger Font:** Use `BorderStyle=1` (transparent box) with thick crisp outline (`Outline=7.0`), drop shadow (`Shadow=4.5`), `Bold=-1`, `Fontname=Nirmala UI`, **`Fontsize=92–96`** (~25–30% larger for instant mobile readability).
- **Balanced 1–2 Word Pop Chunks (Zero Trailing Punctuation, Lower Dark Border Placement):** Strip `,`, `।`, `—`, `...` from on-screen pop captions for ultra-clean modern typography. Keep chunks tight (1–2 words) with strict monotonic forward clamping (`min_dur >= 0.28s`, `overlaps == 0`), anchored cleanly in the **lower dark border zone below the video frame** (`MarginV=295–315` at `PlayResY=1920`, safely above YT Shorts bottom UI).
- **Phone-Speaker Vocal Presence:** Apply `highpass=85`, presence EQ (`+3dB @ 3.2kHz`, `+1.8dB @ 180Hz`), and tight vocal compression (`ratio=3.5`) so `LRA` stays punchy (`1.8–4.0 LU`) and every Hindi consonant cuts clearly through mobile speakers at low volume.
- **Word-Level Vocal Sync:** Align chunks to `faster_whisper(..., word_timestamps=True)` on the master speech track, keeping our clean script text (never Whisper misspellings).
- **Visual Pop:** Crisp White (`&H00FFFFFF&`) + Viral Gold/Yellow (`&H0000E5FF&`) on impact words with subtle spring pop (`\fscx88\fscy88\t(0,75,\fscx104\fscy104)\t(75,140,\fscx100\fscy100)`).

---

## 4. Audio & Voiceover Craft
- **Locked Hindi Voice Engines:**
  - **Primary (Real Human Cloned Voice):** **OmniVoice** (`F:\VoiceStudio_Runtime\project\.venv` + `F:\OmniVoice_Models\hf_cache\models--k2-fsa--OmniVoice`) with `num_step >= 18`, Whisper similarity guard (`>= 0.65`, never cache failed gibberish), `-18 dBFS` per-beat RMS normalization, and versioned MD5 cache keys.
  - **Fast Zero-Glitch Alternative:** **`edge-tts`** (`hi-IN-MadhurNeural`, `rate="+16%"`, `pitch="-3Hz"`).
  - **Shared Pro Vocal Chain:** `-45dB` silence trim + `48kHz` resample, presence EQ (`highpass=85`, `+3.2dB @ 3.2kHz`, `+1.8dB @ 180Hz`), tight vocal compression (`ratio=3.5`, `LRA ~1.8–3.5 LU`), tight `0.10–0.15s` inter-sentence pauses, and crisp `0.8s` smooth outro fade.
- **Zero Cache Poisoning:** Track best similarity across retries; NEVER save failed (`< 0.65`) gibberish attempts into persistent `cache/audio/`.
- **Real Cinematic BGM + SFX:** Never use raw pure sine waves (`np.sin(55Hz)`). Use real studio dark-thriller tracks (`assets/bgm/`) or multi-layered filtered rumble + dark minor cello pad + pitch-swept heartbeat + climax riser. Add restrained SFX (Hook impact at `0.0s`, soft whooshes at major cuts >= 1.5s apart, climax boom).
- **Real Sidechain Ducking & Outro Safety:** Pad vocal track with `apad=whole_dur={total_dur}` before `amix=duration=longest` so BGM never cuts to dead silence during the outro fade. Apply `sidechaincompress` triggered by vocals and finish at `-13.5 to -14 LUFS`, True Peak `<= -1.0 dBTP`.

---

## 5. Mandatory Post-Render Self-QA
Before declaring any Short finished, ALWAYS run the `ffmpeg-video-qa-engine` checklist:
1. Build a 3×3 visual contact sheet and inspect EVERY tile for: cut-off faces, colliding burned-in movie subtitles, broken Devanagari matras, empty/off-topic frames, or dark/muddy grading.
2. Verify `ffprobe` A/V duration match (`<= 0.25s` diff), exact `30fps`, `ebur128` loudness (`-13 to -15 LUFS`, Peak `<= -1.0 dBTP`), and non-silent outro audio.
3. Verify `overlaps == 0` in the `.ass` file.


---

## 6. V3 MANDATORY PIPELINE RULES (locked after the Meridian audit - zero bypass)

Reusable code lives in `C:\Users\shahz\.gemini\config\skills\viral-shorts-mastery\scripts\pipeline\`
(canonical working copy: `f:\ai video edit\pipeline\`). Every Short script MUST import it - never call
`model.generate()`, `PIL.ImageDraw.text()` for Hindi, or hand-typed timestamps directly.

1. **Audio = `audio_guard.GuardedTTS` only (no standalone OmniVoice calls).**
   - `hindi_normalizer.normalize_hindi()` runs first: digits/years/decimals/% /ALL-CAPS acronyms -> pure Hindi words
     (`1947` -> `उन्नीस सौ सैंतालीस`, `2016` -> `दो हज़ार सोलह`, `LAPD` -> `एल ए पी डी`).
   - Beats are **max 15 words** (target 9-13). Longer = hard error (long beats make OmniVoice hallucinate).
   - Gate = faster-whisper **`small`, CPU, int8** (never `large-v3`) on the SHIPPED audio: phonetic-normalised
     `SequenceMatcher >= 0.72` AND `max_gap <= 8` chars (longest script span Whisper did not hear) AND
     `suffix_unmatched <= 4` chars (last word not cut) AND no abrupt end. Whisper repetition loops (`ँँँँ`) are collapsed.
   - Fail -> new seed, **max 3 retries**; still failing -> flagged `edge-tts hi-IN-MadhurNeural` fallback; still failing ->
     `FAILED_QA` and the build ABORTS. Gibberish is never silently mixed.
   - Trim = `-52 dB` with **65 ms real/zero padding at both ends** + 4 ms edge fades (no mid-word cuts).
   - Reference clone text MUST be the real Whisper transcript of the reference clip (`<ref>.txt`), never an invented sentence.
   - `audio_report.json` (per-beat similarity, gap, suffix, attempts, engine) is mandatory input for `qa_inspect_video.py`.
   - **Known limit (be honest):** Whisper-small cannot catch a tiny 1-syllable insertion (e.g. `निकला` -> `निकलागा`, gap=1).
     Keep beats short; the agent cannot listen, only measure.
2. **Banner Hindi = libass, never Pillow.** `PILLOW_RAQM=False` on this PC -> Pillow breaks matras (`मिला` -> `मलिा`).
   `overlay_kit.make_banner_box_png()` draws ONLY the dark-glass box + gold stripe. `BannerTitle` / `BannerHook` ASS styles
   (`Spacing=0`, `\an7\pos()`) render the text via libass+HarfBuzz. Order: banner PNG overlay -> `ass=` burned LAST.
3. **Zero blind timestamps (`shot_guard.py`).** PySceneDetect shot list (on a 480p H.264 proxy), contact sheets labelled with
   exact `S### start-end`; a clip window `[t, t+dur*1.03]` must sit inside ONE shot (or an explicitly allowed jump-cut span);
   3-frame probe (`0s, +1.5s, +3.0s`) flags `BLACK_FRAME` / `POSSIBLE_CUT`. Never select from a fixed-interval thumbnail grid alone
   (a doll / pocket-watch / black frame can hide between two thumbnails).
4. **Word-sync clip timing, no 1:1:1 splits.** Whisper `word_timestamps` -> `script_word_times()` (fuzzy monotonic alignment) ->
   every clip carries a `cue` word; the cut lands `0.06s` BEFORE that word is spoken. Captions use the same word times.
   Story must never show an object the script does not mention.
5. **Smart `hflip`:** default ON for real movies; per-clip `flip=False` + `why` only for readable clocks / signs / on-screen text.
   The clip manifest records `flip`, the reason and whether the `hflip` filter was really in the filter chain.
6. **Wide 2+ person shots:** `fit="wide"` (whole 16:9 frame scaled into the cinema window, black pad) so no face is cropped.
7. **Delivery gate:** build -> `qa_inspect_video.py --audio-report --clip-manifest --require-banner-ass` -> the AGENT opens
   `qa_banner_zoom.png` + the 3x3 storyboard and reads every Devanagari matra -> only then `send_telegram.py`.
