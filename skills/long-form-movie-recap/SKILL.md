---
name: long-form-movie-recap
description: >-
  Complete production blueprint for 12-to-22 minute 16:9 Full HD Hindi Movie Explanation / Recap
  YouTube videos modeled on top Indian channels (Filmy Nest, ZN Explain, Story Unlocked, Holly Films,
  Anokhi Films) and GitHub editing workflows (joshcirre/editing-videos, AI-Movie-Shorts, NarratoAI).
  Covers copyright-safe Tier-3 movie selection, 4-Act retention scripting, visual-to-narration scene
  matching, clean 16:9 framing, conversational narration pacing, and audio mastering. Activate when
  planning, scripting, or editing long-form YouTube movie recaps or narrative explainers.
---

# Long-Form Movie Recap & Narrative Editing Engine (16:9 Full HD)

Use this skill when building 10–22 minute YouTube movie explanation / story recap videos (`1920×1080`).

---

## 1. Competitor DNA: How Top Hindi Long-Form Channels Win (Filmy Nest, ZN Explain, Holly Films, Story Unlocked)
Analysis of top-performing 15–22 minute Hindi movie recaps reveals clear, repeatable patterns:

1. **Movie Selection (Copyright Survival First)**
   - **Sweet Spot (Tier-3 Safe):** Chinese web-monster/disaster films (*Snake 3, Big Octopus, Giant Crocodile*), Korean/Japanese/European indie survival & psychological thrillers (*Watcher, Peninsula-style indies, survival desert/island films*).
   - **Avoid Tier-1 Enterprise Content-ID Bots:** Disney/Marvel, Warner Bros, Sony, Paramount, Universal, T-Series, YRF — automated global blocks/strikes are high risk.
2. **High-CTR Hinglish Titles & Emotional Premise**
   - Pattern: `[Shocking Survival/Mystery Premise in Hinglish] | [Movie Name / Genre] Explained in Hindi`
   - Examples: *"4 Saal Tak Is Plane Ke Upar Zinda Kaise Rahi?"*, *"Is Shehar Ke Beech Chhupa Hai Ek Rehsamayi Raaz"*, *"Puri Family Fans Gyi Es Desert Me Jaha Se Koi Nahi Bachega"*.
3. **Clean Cinema Presentation (Filmy Nest Style)**
   - Full `1920×1080` crisp 16:9 visual — **NO cluttered overlays, NO garish yellow boxes!**
   - Clean matte-black bottom scope bar (`h=90–110px`) displaying minimal uppercase white movie title (`DINOSAUR VS PYTHON`), optionally hiding original movie subtitles cleanly!
   - Subtle diagonal low-opacity (`20–25%`) channel brand watermark in lower-left for ownership identity.
4. **Natural Conversational Storytelling (Not Rushed Shorts Speed)**
   - Pace: **165–185 WPM** (TTS speed `~1.05–1.10x`, NOT frantic `1.25x`), natural `0.15–0.25s` breath pauses between story beats, dramatic `0.4s` pauses before plot twists.
   - Conversational Hindi hooks: *"कहानी की शुरुआत में हम देखते हैं..."*, *"लेकिन इन्हें बिल्कुल अंदाज़ा नहीं था कि..."*, *"तभी कुछ ऐसा होता है जिसने सबके होश उड़ा दिए..."*.

---

## 2. 4-Act Retention Script Architecture (Target: 15–20 Minutes / 2,000–2,600 Words)
Never ship a 60-second 16-sentence video and call it a "long recap". A true monetizable long recap requires **120–200 narration beats** across 4 structured acts with **micro-cliffhangers every 90–120 seconds**:

1. **Act 1 — Cold Open Hook & World Setup (`00:00 – 02:30`)**
   - Start with a 20-second flash-forward of the film's scariest/wildest moment (the "open loop"), then cut back: *"लेकिन ये लोग यहाँ तक पहुँचे कैसे? आइए कहानी की शुरुआत से देखते हैं..."*
   - Introduce protagonist, goal, and the fatal mistake that triggers the plot.
2. **Act 2 — Catalyst & Escalating Threat (`02:30 – 07:30`)**
   - First incident / monster reveal / trap closing.
   - Escape routes destroyed; first casualties raise stakes.
   - Drop micro-cliffhangers every 2 minutes so Average View Duration (AVD) stays > 50%.
3. **Act 3 — Survival Struggle, Betrayal & Midpoint Twist (`07:30 – 13:30`)**
   - Temporary shelter or counter-plan forms, then fails dramatically.
   - Internal conflict, betrayal, or shocking reveal about the villain/monster's weakness.
4. **Act 4 — Final Showdown, Sacrifice & Ending Explanation (`13:30 – 18:00`)**
   - Climax battle / escape with faster `2.5–3.5s` cut rhythm.
   - Explain the ending twist clearly + ask a single engaging moral/survival question to drive comments.

---

## 3. Professional 6-Step Sequential Editing Order (from `joshcirre/editing-videos`)
Follow this strict order — never polish before structure is locked:
1. **Verify Narration & Clean Slips:** Synthesize act-by-act with resumable checkpoints. Whisper guard MUST use **`sim >= 0.60 and len(transcribed) >= 5`** (never `or`!) and NEVER cache failed gibberish.
2. **Tighten Rhythm:** Strip dead air (`-40dB` with 50ms padding), normalize RMS across all beats (`-18 dBFS`), preserve intentional dramatic pauses.
3. **Shape Macro Arc:** Verify total audio length matches target runtime and chapter timestamps are logged for YouTube description SEO.
4. **Visual-to-Narration Scene Matching (Critical!):**
   - **NEVER use blind evenly-spaced timestamps (`idx * step`)** — that disconnects visuals from narration!
   - Use **PySceneDetect** + source subtitle/scene-summary indexing (like `AI-Movie-Shorts` / `NarratoAI`) to map each narration beat to the chronological scene in the movie where that action actually happens.
   - Keep every individual clip `2.5s – 4.5s` max (Content ID protection + viewer engagement), muted original audio, subtle `1.03x` temporal shift, clean cinema color grade + sharpening, and smooth `30ms` audio crossfades at boundaries.
5. **Minimal Graphics & Chapters:** Clean lower matte title bar (`DINOSAUR VS PYTHON` style), subtle watermark, chapter card fades only at Act transitions.
6. **Final Audio Mastering:** Ambient suspense/cinematic bed ducked `-14 to -18 dB` under narration via `sidechaincompress`, `apad=whole_dur={total_dur}` so outro music fades smoothly, final loudness `-14 LUFS`, True Peak `<= -1.0 dBTP`.

---

## 4. Mandatory Pre-Delivery Verification
Run the `ffmpeg-video-qa-engine` workflow on the finished long video:
- Inspect a 3×3 storyboard sampled across all 4 Acts (verify crisp 16:9 visuals, clean matte bottom bar covering any original movie subs, no black transition frames, no cropped heads).
- Check `ffprobe` A/V sync (`diff <= 0.3s`), `ebur128` loudness (`-14 LUFS ± 1 LU`), and verify Telegram file-size handling (`> 49 MB` sends summary + local path instead of failing upload).
