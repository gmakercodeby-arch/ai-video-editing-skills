# -*- coding: utf-8 -*-
"""
build_meridian_short.py  (v2 - uses the reusable pipeline; no standalone audio / timestamp shortcuts)

 audio : pipeline/audio_guard.GuardedTTS  (normalizer + Whisper-small gate + retries + fallback flag)
 video : pipeline/shot_guard              (PySceneDetect shots, safe windows, 3-frame probe)
 text  : pipeline/overlay_kit             (Pillow draws ONLY the glass box; Hindi banner text = libass)
 run with the OmniVoice interpreter:  F:\\VoiceStudio_Runtime\\project\\.venv\\Scripts\\python.exe
"""
import json
import os
import re
import subprocess
import sys
import time

PIPE = r"f:\ai video edit\pipeline"
sys.path.insert(0, PIPE)
os.environ["HF_HOME"] = r"F:\OmniVoice_Models\hf_cache"
os.environ["HF_HUB_CACHE"] = r"F:\OmniVoice_Models\hf_cache"
os.environ["HUGGINGFACE_HUB_CACHE"] = r"F:\OmniVoice_Models\hf_cache"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import numpy as np  # noqa: E402
import torch  # noqa: E402
from scipy.io import wavfile  # noqa: E402

from audio_guard import GuardedTTS  # noqa: E402
from music_kit import generate_cinematic_bgm_and_sfx  # noqa: E402
from overlay_kit import build_chunks, make_banner_box_png, write_ass  # noqa: E402
from shot_guard import SPEED, build_shots, probe_window, safe_window  # noqa: E402

WORK = r"f:\ai video edit\meridian_short_v2"
SRC = r"f:\ai video edit\source_movie\meridian.mp4"
SHOTS_JSON = r"f:\ai video edit\source_movie\meridian_shots.json"
REF_WAV = r"f:\ai video edit\voice_clone\profiles\SnakeNarrator_ref.wav"
OUT_VIDEO = os.path.join(WORK, "meridian_viral_short.mp4")
OUT_ASS = os.path.join(WORK, "captions.ass")
BANNER_PNG = os.path.join(WORK, "banner_box.png")
AUDIO_REPORT = os.path.join(WORK, "audio_report.json")
CLIP_MANIFEST = os.path.join(WORK, "clips_manifest.json")

BANNER_TITLE = "MERIDIAN (2016)  •  SCI-FI MYSTERY"
BANNER_HOOK = "गुफा के अंदर मिला भविष्य का पोर्टल!"

LEAD = 0.06          # cut this long BEFORE the cue word is spoken
MIN_CLIP = 1.0
MAX_CLIP = 4.45      # hard cap on any single continuous shot

# Every clip: src = source second (inside the shot named in the comment), flip = hflip copyright shield,
# why = reason when flip is False, span = (first_shot, last_shot) when a jump-cut mirror sequence is intended,
# fit = "wide" for multi-person wide shots (full 16:9 frame, nobody's face is cropped).
BEATS = [
    {"id": 1, "text": "तीन आदमी अचानक गायब हो गए, और पुलिस को कोई सुराग नहीं मिला!", "pause": 0.12, "sfx": "boom",
     "impact": ["गायब", "सुराग"],
     "clips": [{"src": 49.6, "flip": True},                                   # S012 corkboard: 3 missing men
               {"cue": "पुलिस", "src": 55.6, "flip": True}]},                  # S013 young detective
    {"id": 2, "text": "यह कहानी 1947 के लॉस एंजिल्स की है।", "pause": 0.12, "sfx": None,
     "impact": ["सैंतालीस", "लॉस"],
     "clips": [{"src": 1.3, "flip": False, "why": "on-screen title text 'Los Angeles 1947'"},   # S001
               {"cue": "लॉस", "src": 9.6, "flip": False, "why": "street signage text"}]},     # S003
    {"id": 3, "text": "पुलिस दफ़्तर में एक अनुभवी अफसर, नए जासूस को केस समझा रहा था।", "pause": 0.12, "sfx": None,
     "impact": ["अनुभवी", "जासूस"],
     "clips": [{"src": 60.0, "flip": False, "why": "readable wall clock in frame"},             # S014 veteran
               {"cue": "नए", "src": 73.0, "flip": True}]},                                     # S015 young detective
    {"id": 4, "text": "एक जासूस केस की फाइल लेकर, सुनसान हाईवे पर अकेला निकल पड़ा।", "pause": 0.12, "sfx": "whoosh",
     "impact": ["जासूस", "सुनसान", "अकेला"],
     "clips": [{"src": 192.0, "flip": True},                                  # S035 detective at desk
               {"cue": "सुनसान", "src": 199.0, "flip": True}]},                # S036 lonely highway
    {"id": 5, "text": "तभी उसकी कार के शीशे में, एक अजीब लड़की दिखाई दी!", "pause": 0.12, "sfx": "whoosh",
     "impact": ["शीशे", "अजीब", "लड़की"],
     "clips": [{"src": 249.0, "flip": True},                                  # S046 driver
               {"cue": "शीशे", "src": 260.1, "flip": True, "span": (52, 54)},  # S052-54 girl in mirror
               {"cue": "अजीब", "src": 256.8, "flip": True}]},                  # S051 shocked eyes
    {"id": 6, "text": "आगे समंदर के किनारे, किसी की लावारिस कार खड़ी मिली।", "pause": 0.12, "sfx": None,
     "impact": ["समंदर", "लावारिस"],
     "clips": [{"src": 274.6, "flip": True},                                  # S060 two cars
               {"cue": "लावारिस", "src": 286.0, "flip": True}]},
    {"id": 7, "text": "आसमान में भयानक तूफान उठा, और बिजली कड़कने लगी!", "pause": 0.12, "sfx": "boom",
     "impact": ["भयानक", "तूफान", "बिजली"],
     "clips": [{"src": 365.0, "flip": True},                                  # S066 storm clouds
               {"cue": "बिजली", "src": 351.3, "flip": True}]},                 # S063 lightning cliff
    {"id": 8, "text": "चट्टानों के नीचे, उसे एक रहस्यमयी गुफा दिखाई दी।", "pause": 0.12, "sfx": None,
     "impact": ["चट्टानों", "रहस्यमयी", "गुफा"],
     "clips": [{"src": 396.2, "flip": True},                                  # S068 rock
               {"cue": "रहस्यमयी", "src": 410.1, "flip": True}]},              # S070 cave exterior
    {"id": 9, "text": "वह टॉर्च और बंदूक लेकर, अंधेरी गुफा के अंदर चला गया।", "pause": 0.12, "sfx": "whoosh",
     "impact": ["टॉर्च", "बंदूक", "अंधेरी"],
     "clips": [{"src": 418.0, "flip": True},                                  # S071 walking to cave
               {"cue": "अंधेरी", "src": 472.0, "flip": True}]},                # S074 torch + gun
    {"id": 10, "text": "अंदर एक चमकती खिड़की में, उसने खुद को ही देख लिया!", "pause": 0.12, "sfx": "boom",
     "impact": ["चमकती", "खुद"],
     "clips": [{"src": 498.0, "flip": True},                                  # S075 glowing window
               {"cue": "उसने", "src": 513.2, "flip": True}]},                  # S077 himself on the beach
    {"id": 11, "text": "वहाँ तीन पुतले खड़े थे, जो हूबहू गायब आदमियों जैसे थे।", "pause": 0.12, "sfx": None,
     "impact": ["पुतले", "हूबहू", "गायब"],
     "clips": [{"src": 535.5, "flip": True},                                  # S079 three figures
               {"cue": "हूबहू", "src": 50.0, "flip": True}]},                  # S012 corkboard callback
    {"id": 12, "text": "तभी अंधेरे से एक रहस्यमयी औरत सामने आई, और उसे घूरने लगी।", "pause": 0.15, "sfx": "riser",
     "impact": ["अंधेरे", "रहस्यमयी", "घूरने"],
     "clips": [{"src": 563.8, "flip": True},                                  # S081 pale man
               {"cue": "औरत", "src": 567.5, "flip": True, "fit": "wide"}]},    # S082 woman + hat man (wide)
    {"id": 13, "text": "आखिर वह औरत कौन थी, और ये सब क्या था?", "pause": 0.80, "sfx": "boom",
     "impact": ["औरत", "कौन"],
     "clips": [{"src": 571.2, "flip": True},                                  # S083 woman
               {"cue": "कौन", "src": 574.9, "flip": True}]},
]


def cue_index(words, cue):
    clean = lambda w: re.sub(r"[।,!\?\.\-—]", "", w)
    for i, w in enumerate(words):
        if clean(w) == cue:
            return i
    raise ValueError(f"cue '{cue}' not found in {words}")


def render_clip(n, src_start, out_dur, flip, fit, is_last, out_mp4):
    total_frames = max(1, int(round(out_dur * 30)))
    fade = f",fade=t=out:st={max(0.0, out_dur - 0.80):.2f}:d=0.80" if is_last else ""
    grade = ("colorbalance=rs=-0.10:gs=0.04:bs=0.14:rm=-0.06:gm=0.03:bm=0.09:rh=0.03:gh=0.02:bh=0.05,"
             "eq=contrast=1.18:brightness=-0.02:saturation=1.22,unsharp=5:5:1.15:3:3:0.4,noise=c0s=1.4:c0f=t+u")
    hf = "hflip," if flip else ""
    if fit == "wide":     # whole 16:9 frame inside the cinema window -> no face is ever cropped
        geo = (f"{hf}scale=1080:608:flags=lanczos,fps=30,"
               f"zoompan=z='1.0+0.040*min(on/{total_frames},1)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x608:fps=30,"
               f"{grade},pad=1080:1120:0:256:color=black")
    else:
        crop_w = 1040
        cx = (1920 - crop_w) // 2
        geo = (f"{hf}crop={crop_w}:1080:{cx}:0,scale=1080:1120:flags=lanczos,fps=30,"
               f"zoompan=z='1.0+0.060*min(on/{total_frames},1)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1120:fps=30,{grade}")
    vf = f"setpts=PTS/{SPEED},{geo},pad=1080:1920:0:340:color=black{fade},setsar=1,format=yuv420p"
    cmd = ["ffmpeg", "-y", "-ss", f"{src_start:.3f}", "-i", SRC, "-t", f"{out_dur:.3f}", "-an", "-vf", vf,
           "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-r", "30", out_mp4]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"clip {n} failed:\n{r.stderr[-700:]}")
    return vf


def main():
    os.makedirs(os.path.join(WORK, "clips"), exist_ok=True)
    os.makedirs(os.path.join(WORK, "beats"), exist_ok=True)
    shots = build_shots(SRC, SHOTS_JSON)

    print("1) OmniVoice + guarded narration (normalizer + Whisper-small gate)...", flush=True)
    from omnivoice.models.omnivoice import OmniVoice
    model = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cpu", dtype=torch.float32, local_files_only=True)
    model.eval()
    state = {}

    def gen(text, seed):
        wl = model.generate(text=text, language="hi", voice_clone_prompt=state["prompt"], speed=1.10, num_step=18, seed=seed)
        w = wl[0].detach().cpu().float().squeeze()
        if w.ndim > 1:
            w = w.mean(dim=0)
        return w.numpy()

    g = GuardedTTS(gen, os.path.join(WORK, "beats"), sr_in=24000, tag="omnivoice-snake-v2", base_seed=100)
    ref_txt = REF_WAV[:-4] + ".txt"            # REAL transcript of the reference clip (never an invented one)
    if os.path.exists(ref_txt):
        ref_text = open(ref_txt, encoding="utf-8").read().strip()
    else:
        ref_text = g.client.transcribe(REF_WAV)["text"].strip()
        open(ref_txt, "w", encoding="utf-8").write(ref_text)
    print("   REF TRANSCRIPT:", ref_text, flush=True)
    state["prompt"] = model.create_voice_clone_prompt(ref_audio=REF_WAV, ref_text=ref_text)

    results = [g.synth_beat(b["id"], b["text"]) for b in BEATS]
    rep = g.write_report(AUDIO_REPORT)
    g.close()
    print(f"   AUDIO GUARD: min similarity={rep['min_similarity']}, failed={rep['n_failed']}, fallback={rep['n_fallback']}", flush=True)
    if rep["n_failed"]:
        print("ABORT: beats failed audio QA after retries + fallback; nothing is rendered or sent.", flush=True)
        sys.exit(2)

    print("2) Timeline (word-sync cues from Whisper word timestamps)...", flush=True)
    SR = 48000
    voice = [np.zeros(int(0.10 * SR), dtype=np.int16)]
    captions, sfx_events, plan = [], [], []
    cur = 0.10
    for beat, res in zip(BEATS, results):
        _, samples = wavfile.read(res["wav"])
        bdur = len(samples) / SR
        total = bdur + beat["pause"]
        words, wt = res["script_words"], res["word_times"]
        if beat["sfx"]:
            sfx_events.append((cur, beat["sfx"]))
        offs = [0.0] + [max(0.0, wt[cue_index(words, c["cue"])] - LEAD) for c in beat["clips"][1:]]
        n = len(offs)
        for i in range(1, n):
            offs[i] = max(offs[i], offs[i - 1] + MIN_CLIP)
        for i in range(n - 1, 0, -1):
            offs[i] = min(offs[i], total - MIN_CLIP * (n - i))
        for i, c in enumerate(beat["clips"]):
            d = (offs[i + 1] if i + 1 < n else total) - offs[i]
            if d > MAX_CLIP:
                raise ValueError(f"beat {beat['id']} clip {i} is {d:.2f}s > {MAX_CLIP}s - add another clip")
            plan.append({"beat": beat["id"], "out_start": round(cur + offs[i], 3), "out_dur": round(d, 3), **c})
        chunks = build_chunks(words, beat["impact"])
        for k, ch in enumerate(chunks):
            s = cur + (max(0.0, wt[ch["idx"]] - 0.02) if k else 0.0)
            e = (cur + wt[chunks[k + 1]["idx"]] - 0.01) if k + 1 < len(chunks) else cur + bdur
            captions.append({"text": ch["text"], "start": s, "end": e, "impact": ch["impact"]})
        voice += [samples, np.zeros(int(beat["pause"] * SR), dtype=np.int16)]
        cur += total
        print(f"   Beat {beat['id']:02d}: {bdur:.2f}s voice, clips {[round(p['out_dur'],2) for p in plan if p['beat']==beat['id']]}", flush=True)
    total_dur = cur
    wavfile.write(os.path.join(WORK, "master_voice_raw.wav"), SR, np.concatenate(voice))
    print(f"   TOTAL {total_dur:.2f}s, {len(plan)} clips, {len(sfx_events)} SFX", flush=True)

    print("3) Shot-guard + render clips...", flush=True)
    manifest, concat = [], []
    for n_, p in enumerate(plan, 1):
        span = p.get("span")
        if span:
            a, b = shots[span[0]][0], shots[span[1]][1]
            need = p["out_dur"] * SPEED
            ok = (a + 0.1) <= p["src"] and p["src"] + need <= (b - 0.1)
            s_adj, info = p["src"], {"span": list(span), "span_range": [a, b], "need_src_s": round(need, 3)}
        else:
            s_adj, ok, info = safe_window(shots, p["src"], p["out_dur"])
        if not ok:
            raise ValueError(f"clip {n_} (beat {p['beat']}): window {p['src']}+{p['out_dur']}s does not fit inside its shot {info}")
        probe = probe_window(SRC, s_adj, p["out_dur"] * SPEED)
        is_last = n_ == len(plan)
        path = os.path.join(WORK, "clips", f"clip_{n_:02d}.mp4")
        vf = render_clip(n_, s_adj, p["out_dur"], p["flip"], p.get("fit", "fill"), is_last, path)
        manifest.append({"n": n_, "beat": p["beat"], "src_start": round(s_adj, 3), "out_dur": p["out_dur"],
                         "flip": p["flip"], "flip_reason": p.get("why"), "fit": p.get("fit", "fill"),
                         "shot": info, "probe": probe, "has_hflip_filter": "hflip" in vf})
        concat.append(f"file '{path.replace(os.sep, '/')}'\n")
        flag = f"  !! {probe['flags']}" if probe["flags"] else ""
        print(f"   clip {n_:02d} beat {p['beat']:02d} src {s_adj:7.2f}s dur {p['out_dur']:.2f}s flip={p['flip']} luma={probe['luma']}{flag}", flush=True)
    json.dump({"clips": manifest}, open(CLIP_MANIFEST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(WORK, "concat.txt"), "w", encoding="utf-8").writelines(concat)
    vc = os.path.join(WORK, "video_concat.mp4")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(WORK, "concat.txt"), "-c", "copy", vc],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    vdur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", vc],
                                stdout=subprocess.PIPE, text=True, check=True).stdout.strip())

    print(f"4) Banner (libass) + captions + BGM/SFX + master ({vdur:.2f}s)...", flush=True)
    make_banner_box_png(BANNER_PNG)
    write_ass(captions, OUT_ASS, vdur, BANNER_TITLE, BANNER_HOOK)
    bgm = os.path.join(WORK, "master_bgm_sfx.wav")
    generate_cinematic_bgm_and_sfx(vdur, sfx_events, bgm)
    master = os.path.join(WORK, "master_audio.m4a")
    af = (f"[0:a]highpass=f=85,equalizer=f=3200:t=q:w=1.2:g=3.2,equalizer=f=180:t=q:w=1.0:g=1.8,"
          f"acompressor=threshold=-18dB:ratio=3.5:attack=5:release=65:makeup=4dB,"
          f"apad=whole_dur={vdur:.3f},atrim=0:{vdur:.3f},aformat=channel_layouts=stereo,asplit=2[vm][vs];"
          f"[1:a]volume=0.34,atrim=0:{vdur:.3f},aformat=channel_layouts=stereo[bi];"
          f"[bi][vs]sidechaincompress=threshold=0.025:ratio=5.5:attack=15:release=220:makeup=1[bd];"
          f"[vm][bd]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.92,loudnorm=I=-14.0:TP=-1.2:LRA=7[aout]")
    subprocess.run(["ffmpeg", "-y", "-i", os.path.join(WORK, "master_voice_raw.wav"), "-i", bgm, "-filter_complex", af,
                    "-map", "[aout]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", master],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("5) Final composite: banner box PNG, then libass (banner text + captions) LAST...", flush=True)
    ass_esc = OUT_ASS.replace("\\", "/").replace(":", "\\:")
    subprocess.run(["ffmpeg", "-y", "-i", vc, "-i", BANNER_PNG, "-i", master,
                    "-filter_complex", f"[0:v][1:v]overlay=0:0[wb];[wb]ass='{ass_esc}'[vout]",
                    "-map", "[vout]", "-map", "2:a:0", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "copy", "-shortest", OUT_VIDEO],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("6) Mandatory QA v2...", flush=True)
    qa = subprocess.run([r"f:\ai video edit\.venv\Scripts\python.exe",
                         r"C:\Users\shahz\.gemini\config\skills\ffmpeg-video-qa-engine\scripts\qa_inspect_video.py",
                         OUT_VIDEO, "--ass", OUT_ASS, "--audio-report", AUDIO_REPORT, "--clip-manifest", CLIP_MANIFEST,
                         "--require-banner-ass"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    open(os.path.join(WORK, "qa_report.json"), "w", encoding="utf-8").write(qa.stdout)
    print(qa.stdout, flush=True)
    print("BUILD_DONE (not sent: agent must visually verify banner zoom + storyboard first)", flush=True)


if __name__ == "__main__":
    main()
