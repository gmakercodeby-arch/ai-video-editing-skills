<div align="center">

<!-- Animated Wave Header Banner -->
<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,45:0f4c5c,100:e36414&height=230&section=header&text=AI%20Video%20Editing%20Skills&fontSize=44&fontColor=ffffff&fontAlignY=38&desc=Viral%20Hindi%20Recap%20%26%20Production%20V3%20Pipeline&descAlignY=62&descSize=18&animation=fadeIn" alt="AI Video Editing Skills Banner" />

<!-- Repo Logo -->
<img src="assets/logo.png" width="140" alt="AI Video Editing Skills Logo" />

<!-- Animated Typing Tagline -->
<a href="https://github.com/gmakercodeby-arch/ai-video-editing-skills">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=19&duration=2800&pause=900&color=00E5FF&center=true&vCenter=true&width=760&lines=Viral+Hindi+Movie+Recap+Shorts+(1080x1920+%40+30fps);Long-Form+Movie+Explained+(1080p+Full+HD+%7C+12-22+mins);Zero-Bypass+Whisper+Audio+Guard+%2B+PySceneDetect+Cuts;HarfBuzz+Devanagari+Captions+%2B+EBUR128+Post-Render+QA" alt="Typing SVG" />
</a>

<br/>

<!-- Tech Stack & Repo Badges -->
<p>
  <img src="https://img.shields.io/badge/Pipeline-V3%20Locked-FF4B2B?style=for-the-badge&logo=firefoxbrowser&logoColor=white" alt="Pipeline V3 Locked" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FFmpeg-libass%20%2F%20HarfBuzz-007808?style=for-the-badge&logo=ffmpeg&logoColor=white" alt="FFmpeg" />
  <img src="https://img.shields.io/badge/Whisper-Faster--Whisper%20int8-10A37F?style=for-the-badge&logo=openai&logoColor=white" alt="Faster Whisper" />
  <img src="https://img.shields.io/badge/CUDA-Optional%20GPU%20Boost-76B900?style=for-the-badge&logo=nvidia&logoColor=white" alt="NVIDIA CUDA" />
  <img src="https://img.shields.io/badge/OS-Windows%2010%20%2F%2011-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows" />
</p>

<p>
  <a href="https://github.com/gmakercodeby-arch/ai-video-editing-skills/stargazers">
    <img src="https://img.shields.io/github/stars/gmakercodeby-arch/ai-video-editing-skills?style=flat-square&color=f59e0b" alt="GitHub Stars" />
  </a>
  <a href="https://github.com/gmakercodeby-arch/ai-video-editing-skills/network/members">
    <img src="https://img.shields.io/github/forks/gmakercodeby-arch/ai-video-editing-skills?style=flat-square&color=06b6d4" alt="GitHub Forks" />
  </a>
  <a href="https://github.com/gmakercodeby-arch/ai-video-editing-skills/issues">
    <img src="https://img.shields.io/github/issues/gmakercodeby-arch/ai-video-editing-skills?style=flat-square&color=ef4444" alt="GitHub Issues" />
  </a>
  <img src="https://img.shields.io/github/repo-size/gmakercodeby-arch/ai-video-editing-skills?style=flat-square&color=8b5cf6" alt="Repo Size" />
</p>

<!-- Quick Jump Navigation -->
<p>
  <a href="#-4-production-ready-modes"><b>Modes</b></a> â€¢
  <a href="#%EF%B8%8F-v3-locked-pipeline-architecture"><b>Architecture</b></a> â€¢
  <a href="#-key-features-v3-locked-pipeline"><b>Features</b></a> â€¢
  <a href="#-quick-install-smart-pc-scanner"><b>Quick Install</b></a> â€¢
  <a href="#-system-requirements"><b>System Specs</b></a> â€¢
  <a href="#-repository-structure"><b>Structure</b></a>
</p>

</div>

---

## ðŸŽ¯ 4 Production-Ready Modes

<table>
  <tr>
    <td width="50%" valign="top">
      <h3>ðŸ“± 1. Viral Hindi Movie Recap Shorts</h3>
      <code>1080Ã—1920 @ 30fps</code> â€¢ Vertical Retention Engine<br/><br/>
      Built for high-retention recap channels in <b>@CineKahaniHindi75</b> / <b>@MUNDAEXPLAIN</b> style with snappy word-synced cuts and Devanagari hook banners.
    </td>
    <td width="50%" valign="top">
      <h3>ðŸŽ¬ 2. Long-Form Movie Explained</h3>
      <code>1920Ã—1080 Full HD</code> â€¢ 12â€“22 Mins<br/><br/>
      Structured storytelling pipeline inspired by <b>Filmy Nest</b> / <b>ZN Explain</b> style with consistent pacing, copyright protection, and clean audio mastering.
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>ðŸ—£ï¸ 3. Conversational Video Editing</h3>
      <code>video-use</code> â€¢ General Purpose Skill<br/><br/>
      Flexible AI-assisted video editing workflow for trimming, assembling, styling, and automating everyday video tasks via natural instructions.
    </td>
    <td width="50%" valign="top">
      <h3>ðŸ” 4. Mandatory Post-Render QA Engine</h3>
      <code>ffmpeg-video-qa-engine</code> â€¢ Automated Verification<br/><br/>
      Every export is audited with banner zoom crops, 3Ã—3 visual storyboards, <code>-14 LUFS</code> EBUR128 loudness checks, and Whisper transcript similarity.
    </td>
  </tr>
</table>

---

## âš™ï¸ V3 Locked Pipeline Architecture

```mermaid
flowchart LR
    A["ðŸ“ Raw Hindi Script"] --> B["ðŸ”¤ Hindi Normalizer<br/>hindi_normalizer.py"]
    B --> C["ðŸŽ™ï¸ TTS / OmniVoice<br/>+ edge-tts fallback"]
    C --> D["ðŸ›¡ï¸ Audio Guard<br/>faster-whisper int8<br/>sim â‰¥ 0.72"]
    D --> E["âœ‚ï¸ Shot Guard<br/>PySceneDetect + 3-Frame Probe<br/>0.06s cue lead"]
    E --> F["ðŸŽ¨ Overlay Kit & Shield<br/>libass HarfBuzz + Cold Teal LUT<br/>â‰¤ 4.45s cuts | 1.03x"]
    F --> G["âœ… Post-Render QA<br/>-14 LUFS + 3Ã—3 Storyboard<br/>qa_banner_zoom.png"]

    style A fill:#1e293b,stroke:#38bdf8,color:#fff
    style B fill:#0f4c5c,stroke:#22d3ee,color:#fff
    style C fill:#1d3557,stroke:#60a5fa,color:#fff
    style D fill:#3b0764,stroke:#c084fc,color:#fff
    style E fill:#7c2d12,stroke:#fb923c,color:#fff
    style F fill:#064e3b,stroke:#34d399,color:#fff
    style G fill:#14532d,stroke:#4ade80,color:#fff
```

---

## âœ¨ Key Features (V3 Locked Pipeline)

| Module | File Path | Core Capability |
| :--- | :--- | :--- |
| ðŸ”¤ **Pre-TTS Hindi Normalizer** | `pipeline/hindi_normalizer.py` | Converts English digits, years (`1947` â†’ `à¤‰à¤¨à¥à¤¨à¥€à¤¸ à¤¸à¥Œ à¤¸à¥ˆà¤‚à¤¤à¤¾à¤²à¥€à¤¸`), decimals, and acronyms (`LAPD` â†’ `à¤à¤² à¤ à¤ªà¥€ à¤¡à¥€`) into pure spoken Hindi before TTS. |
| ðŸ›¡ï¸ **Zero-Bypass Audio Guard** | `pipeline/audio_guard.py` | Audits every beat with `faster-whisper (small, int8, CPU)` â€” enforces `sim >= 0.72`, `max_gap <= 8`, last-word intact check, `-52dB` trim + `65ms` safety padding, max 3 retries + clean `edge-tts` fallback. |
| âœ‚ï¸ **Zero Blind Timestamps** | `pipeline/shot_guard.py` | Combines `PySceneDetect` shot boundaries + 3-frame probe (`0s, +1.5s, +3.0s`) + Whisper `word_timestamps` so cuts land exactly `0.06s` before the spoken cue word. |
| âœï¸ **HarfBuzz Devanagari Overlays** | `pipeline/overlay_kit.py` | Renders all Hindi banner hooks & pop captions via `libass` (`Spacing=0`) â€” **zero broken matras!** |
| ðŸ”’ **Copyright Shield** | Integrated in Render Pipeline | Mutes original audio, smart `hflip` (skips readable clocks/signs), `<= 4.45s` max cut length, `1.03x` speed shift, Cold Teal LUT, micro-sharpening, and subtle film grain. |
| ðŸ“Š **Post-Render Video QA** | `skills/ffmpeg-video-qa-engine/scripts/qa_inspect_video.py` | Auto-generates `qa_banner_zoom.png`, 3Ã—3 storyboard grid, EBUR128 loudness (`-14 LUFS`), and Whisper similarity report. |

---

## ðŸš€ Quick Install (Smart PC Scanner)

> Skips tools that are already installed on your machine â€” zero bloat, clean isolated setup.

```powershell
git clone https://github.com/gmakercodeby-arch/ai-video-editing-skills.git
cd ai-video-editing-skills
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

### What `install.ps1` Does Automatically
- ðŸ”Ž **Scans your PC** for `python`, `ffmpeg`, `git`, and NVIDIA GPU hardware.
- â­ï¸ **Skips existing tools** already present in PATH.
- ðŸ“¦ **Builds an isolated `.venv`** with all required Python dependencies.
- ðŸ§© **Installs all 4 skills** directly into `~/.gemini/config/skills/`.
- ðŸŽ™ï¸ **Voice engine choice:** Optionally sets up local zero-shot **OmniVoice** cloning, or defaults to fast cloud **`edge-tts`**.

---

## ðŸ’» System Requirements

This pipeline adapts automatically to your hardware. Even a standard laptop runs the complete editing + `edge-tts` pipeline smoothly, while a **6 GB+ CUDA GPU** unlocks **15Ã—â€“30Ã— faster** local **OmniVoice** voice cloning.

| Component | â˜ï¸ Minimum (`edge-tts` Cloud Voice Mode) | âš¡ Recommended (Fast Local `OmniVoice` Cloning) |
| :--- | :--- | :--- |
| **OS** | Windows 10 / 11 (64-bit) | Windows 11 (64-bit) |
| **CPU** | 4-Core Intel i5 / Ryzen 5 | 6-Core+ Intel i5 (11th Gen+) / Ryzen 5 5600+ |
| **RAM** | **8 GB** | **16 GB+** |
| **GPU** | Integrated / Any CPU (no GPU needed) | **NVIDIA GTX 1660 SUPER (6 GB) / RTX 3060 (12 GB)** (`CUDA sm_70+`, **6 GB+ VRAM**) |
| **Disk Space** | **~2 GB free** (+ space for movies) | **~8â€“10 GB free** (OmniVoice + Whisper models + cache) |
| **Internet** | Required for `yt-dlp` & `edge-tts` | Optional once models are cached |

> [!NOTE]
> **Older GPUs (e.g., GTX 960M / `sm_50`):** Modern PyTorch (`cu128`) requires CUDA Compute Capability **`7.0+`** (GTX 16-series / RTX 20/30/40-series). On older GPUs, OmniVoice automatically falls back to CPU (slower) â€” switch to **`edge-tts` mode** for fast 1â€“2 min renders!

---

## ðŸ“ Repository Structure

```text
ai-video-editing-skills/
â”œâ”€â”€ ðŸ“œ install.ps1                        # Smart PC-scanning installer
â”œâ”€â”€ ðŸ“¦ requirements.txt                   # Python dependencies
â”œâ”€â”€ ðŸ” .env.example                       # Optional Telegram delivery config
â”‚
â”œâ”€â”€ ðŸ pipeline/                          # Reusable Python modules (V3 Locked)
â”‚   â”œâ”€â”€ hindi_normalizer.py               # Pre-TTS Devanagari number/acronym normalizer
â”‚   â”œâ”€â”€ audio_guard.py                    # Whisper verification + retry + edge-tts fallback
â”‚   â”œâ”€â”€ whisper_worker.py                 # faster-whisper int8 transcription worker
â”‚   â”œâ”€â”€ shot_guard.py                     # PySceneDetect + 3-frame probe + word cue cuts
â”‚   â”œâ”€â”€ overlay_kit.py                    # libass / HarfBuzz Devanagari banners & captions
â”‚   â”œâ”€â”€ music_kit.py                      # Background music mixing & ducking
â”‚   â”œâ”€â”€ send_telegram.py                  # Automated Telegram delivery
â”‚   â””â”€â”€ example_build_short.py            # End-to-end sample short builder
â”‚
â””â”€â”€ ðŸ§  skills/                            # 4 Antigravity Global Skills
    â”œâ”€â”€ viral-shorts-mastery/             # 1080Ã—1920 Viral Hindi Recap Shorts
    â”œâ”€â”€ long-form-movie-recap/            # 1920Ã—1080 Long-Form Movie Explained
    â”œâ”€â”€ ffmpeg-video-qa-engine/           # Post-Render QA & EBUR128 Inspector
    â””â”€â”€ video-use/                        # General Conversational Video Editing
```

---

<div align="center">

### â­ If this pipeline saves you editing hours, drop a star on the repo!

<a href="https://github.com/gmakercodeby-arch/ai-video-editing-skills/stargazers">
  <img src="https://img.shields.io/badge/Star%20This%20Repo-FF4B2B?style=for-the-badge&logo=github&logoColor=white" alt="Star Repo" />
</a>

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:e36414,55:0f4c5c,100:0d1117&height=115&section=footer" alt="Footer Wave" />

</div>
