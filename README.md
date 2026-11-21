# AI Video Editing Skills & Viral Hindi Recap Pipeline 🎬🔥

Production-grade **AI Video Editing Skills** + **Reusable Python Pipeline** for:
1. **Viral Hindi Movie Recap Shorts (`1080×1920 @ 30fps`)** — `@CineKahaniHindi75` / `@MUNDAEXPLAIN` style
2. **Long-Form Movie Explained (`1920×1080` Full HD, 12–22 mins)** — Filmy Nest / ZN Explain style
3. **General Conversational Video Editing (`video-use`)**
4. **Mandatory Post-Render Video QA Engine (`ffmpeg-video-qa-engine`)**

---

## ✨ Key Features (V3 Locked Pipeline)
- **Pre-TTS Hindi Normalizer (`pipeline/hindi_normalizer.py`):** Converts English digits, years (`1947` → `उन्नीस सौ सैंतालीस`), decimals, and acronyms (`LAPD` → `एल ए पी डी`) into pure Hindi words before TTS.
- **Zero-Bypass Audio Guard (`pipeline/audio_guard.py`):** Runs `faster-whisper (small, int8, CPU)` on every generated beat (`sim >= 0.72`, `max_gap <= 8`, last-word intact check, `-52dB` trim + `65ms` safety padding, max 3 retries + clean `edge-tts` fallback).
- **Zero Blind Timestamps (`pipeline/shot_guard.py`):** Uses `PySceneDetect` shot boundaries + 3-frame probe (`0s, +1.5s, +3.0s`) + Whisper `word_timestamps` so cuts land `0.06s` before the spoken cue word.
- **HarfBuzz Devanagari Banner & Captions (`pipeline/overlay_kit.py`):** Renders all Hindi banner hooks & pop captions via `libass` (`Spacing=0`) — zero broken matras!
- **Copyright Shield:** Original audio muted, smart `hflip` (skips readable clocks/signs), `<= 4.45s` max cut length, `1.03x` speed shift, Cold Teal LUT, micro-sharpening, and subtle film grain.
- **Post-Render QA (`skills/ffmpeg-video-qa-engine/scripts/qa_inspect_video.py`):** Generates `qa_banner_zoom.png`, 3×3 storyboard, EBUR128 loudness (`-14 LUFS`), and Whisper similarity report.

---

## 🚀 Quick Install (Smart PC Scanner — Skips Already Installed Tools)

```powershell
git clone https://github.com/gmakercodeby-arch/ai-video-editing-skills.git
cd ai-video-editing-skills
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

`install.ps1` automatically scans your PC for `python`, `ffmpeg`, `git`, and NVIDIA GPU:
- Skips anything already installed.
- Creates an isolated `.venv` with all dependencies.
- Installs all 4 skills into `~/.gemini/config/skills/`.
- Optionally installs `OmniVoice` for local zero-shot voice cloning (or uses fast `edge-tts`).

---

## 💻 System Requirements (Minimum vs Recommended)

This pipeline adapts to the user's PC! Even a basic laptop can run the full video editing + `edge-tts` pipeline, while a **6 GB+ CUDA GPU** unlocks **15×–30× faster** local **OmniVoice** voice cloning.

| Component | Minimum (`edge-tts` Cloud Voice Mode) | Recommended (Fast Local `OmniVoice` Cloning) |
|---|---|---|
| **OS** | Windows 10 / 11 (64-bit) | Windows 11 (64-bit) |
| **CPU** | 4-Core Intel i5 / Ryzen 5 | 6-Core+ Intel i5 (11th Gen+) / Ryzen 5 5600+ |
| **RAM** | **8 GB** | **16 GB+** |
| **GPU** | Integrated / Any CPU (no GPU needed) | **NVIDIA GTX 1660 SUPER (6 GB) / RTX 3060 (12 GB)** (`CUDA sm_70+`, **6 GB+ VRAM**) |
| **Disk Space** | **~2 GB free** (+ space for your movies) | **~8–10 GB free** (OmniVoice + Whisper models + cache) |
| **Internet** | Required for `yt-dlp` & `edge-tts` | Optional once models are cached |

> **Note on Older GPUs (e.g., GTX 960M / `sm_50`):** Modern PyTorch (`cu128`) requires CUDA Compute Capability **`7.0+`** (GTX 16-series / RTX 20/30/40-series). On older GPUs, OmniVoice automatically falls back to CPU (slower) — use `edge-tts` mode for fast 1–2 min renders!

---

## 📁 Repository Structure
```text
├── install.ps1                  # Smart PC-scanning installer
├── requirements.txt             # Python dependencies
├── .env.example                 # Optional Telegram delivery config
├── pipeline/                    # Reusable Python modules
│   ├── hindi_normalizer.py
│   ├── audio_guard.py
│   ├── whisper_worker.py
│   ├── shot_guard.py
│   ├── overlay_kit.py
│   ├── music_kit.py
│   ├── send_telegram.py
│   └── example_build_short.py
└── skills/                      # 4 Antigravity Global Skills
    ├── viral-shorts-mastery/
    ├── long-form-movie-recap/
    ├── ffmpeg-video-qa-engine/
    └── video-use/
```
