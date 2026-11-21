# -*- coding: utf-8 -*-
"""
audio_lab.py - 120+ 100% Copyright-Free Procedural BGM & SFX Studio Lab (48kHz Stereo).
Zero copyright claims, zero giant GitHub binary bloat: generates any of 60 BGM tracks
and 60 SFX files on demand (or exports the entire 120+ audio pack to a local folder).

Usage:
  python pipeline/audio_lab.py --list
  python pipeline/audio_lab.py --bgm thriller_pulse_01 --dur 45 --out bgm.wav
  python pipeline/audio_lab.py --sfx boom_sub_01 --out boom.wav
  python pipeline/audio_lab.py --build-pack assets/audio_lab --bgm-dur 20
"""
import argparse
import math
import os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 48000


def _lp(sig, cut, order=3):
    cut = max(40.0, min(cut, SR * 0.45))
    b, a = butter(order, cut / (0.5 * SR), btype="low")
    return lfilter(b, a, sig)


def _bp(sig, lo, hi, order=2):
    lo = max(30.0, min(lo, SR * 0.42))
    hi = max(lo + 40.0, min(hi, SR * 0.46))
    b, a = butter(order, [lo / (0.5 * SR), hi / (0.5 * SR)], btype="band")
    return lfilter(b, a, sig)


# 12 Genres x 5 Variations = 60 Distinct Copyright-Free BGM Presets
_GENRE_BASES = {
    "thriller":    ([73.42, 58.27, 49.00, 55.00], 116, 520, True,  True),
    "horror":      ([65.41, 61.74, 55.00, 69.30], 88,  420, True,  False),
    "scifi":       ([82.41, 73.42, 65.41, 98.00], 120, 680, True,  True),
    "crime_noir":  ([69.30, 65.41, 58.27, 51.91], 96,  460, True,  False),
    "emotional":   ([110.0, 87.31, 130.8, 98.00], 80,  820, False, False),
    "action":      ([82.41, 65.41, 73.42, 61.74], 134, 620, True,  True),
    "mystery":     ([77.78, 69.30, 61.74, 73.42], 104, 540, True,  True),
    "survival":    ([61.74, 55.00, 49.00, 58.27], 112, 480, True,  True),
    "documentary": ([98.00, 110.0, 87.31, 98.00], 100, 740, False, True),
    "anime_epic":  ([87.31, 103.8, 116.5, 98.00], 128, 760, True,  True),
    "suspense":    ([65.41, 69.30, 61.74, 58.27], 108, 440, True,  True),
    "space_void":  ([55.00, 65.41, 73.42, 49.00], 76,  600, False, False),
}

BGM_PRESETS = {}
for g_idx, (genre, (roots, base_bpm, lp_cut, has_pulse, has_tick)) in enumerate(_GENRE_BASES.items()):
    for v in range(1, 6):
        name = f"{genre}_{v:02d}"
        shift = 2.0 ** (((v - 3) * 2) / 12.0)  # transpose semitones per variation
        BGM_PRESETS[name] = {
            "genre": genre,
            "roots": [round(r * shift, 2) for r in roots],
            "bpm": base_bpm + (v - 3) * 4,
            "lp": lp_cut + (v - 3) * 55,
            "pulse": has_pulse or (v >= 4),
            "tick": has_tick or (v % 2 == 0),
            "seed": 1000 + g_idx * 17 + v * 7,
        }

# 6 Categories x 10 Variations = 60 Distinct Copyright-Free SFX Presets
SFX_PRESETS = {}
for i in range(1, 11):
    SFX_PRESETS[f"boom_impact_{i:02d}"]   = {"type": "boom",      "f0": 85 + i * 9,   "f1": 28 + i * 2,  "dur": 0.75 + i * 0.08, "seed": 200 + i}
    SFX_PRESETS[f"whoosh_cut_{i:02d}"]    = {"type": "whoosh",    "lo": 180 + i * 45, "hi": 1600 + i * 220, "dur": 0.28 + i * 0.04, "seed": 300 + i}
    SFX_PRESETS[f"riser_tension_{i:02d}"] = {"type": "riser",     "f0": 80 + i * 14,  "mul": 2.4 + i * 0.25, "dur": 1.4 + i * 0.22, "seed": 400 + i}
    SFX_PRESETS[f"heartbeat_{i:02d}"]     = {"type": "heartbeat", "f0": 42 + i * 3,   "gap": 0.18 + i * 0.02, "dur": 0.65, "seed": 500 + i}
    SFX_PRESETS[f"glitch_hit_{i:02d}"]    = {"type": "glitch",    "lo": 700 + i * 180,"hi": 3200 + i * 400, "dur": 0.12 + i * 0.025, "seed": 600 + i}
    SFX_PRESETS[f"bell_reveal_{i:02d}"]   = {"type": "bell",      "f0": 420 + i * 55, "dur": 1.1 + i * 0.15, "seed": 700 + i}


def render_bgm(name, dur, out_wav):
    cfg = BGM_PRESETS[name]
    n = int(math.ceil(dur * SR))
    t = np.arange(n, dtype=np.float64) / SR
    rng = np.random.default_rng(cfg["seed"])

    pad_l, pad_r = np.zeros(n), np.zeros(n)
    seg_len = 6.0
    for si in range(int(math.ceil(dur / seg_len))):
        s0, s1 = int(si * seg_len * SR), min(n, int((si + 1) * seg_len * SR))
        if s1 <= s0:
            break
        ts = t[s0:s1]
        env = np.ones(s1 - s0)
        fd = min(int(0.7 * SR), (s1 - s0) // 3)
        env[:fd] = np.linspace(0, 1, fd)
        env[-fd:] = np.linspace(1, 0, fd)
        root = cfg["roots"][si % len(cfg["roots"])]
        chord = [root, root * 1.189, root * 1.498, root * 2.0]  # minor triad + octave
        sl, sr_ = np.zeros(s1 - s0), np.zeros(s1 - s0)
        for fi, f0 in enumerate(chord):
            vib = 1.0 + 0.003 * np.sin(2 * np.pi * (0.3 + fi * 0.11) * ts)
            pl = 2 * np.pi * np.cumsum(f0 * vib) / SR
            pr = 2 * np.pi * np.cumsum(f0 * 1.003 * vib) / SR
            w = 0.30 if fi == 0 else 0.14
            sl += (np.sin(pl) + 0.42 * np.sin(2 * pl) + 0.2 * np.sin(3 * pl)) * w
            sr_ += (np.sin(pr) + 0.42 * np.sin(2 * pr) + 0.2 * np.sin(3 * pr)) * w
        pad_l[s0:s1] += sl * env
        pad_r[s0:s1] += sr_ * env
    pad_l, pad_r = _lp(pad_l, cfg["lp"]), _lp(pad_r, cfg["lp"])

    pulse = np.zeros(n)
    if cfg["pulse"]:
        step = 60.0 / cfg["bpm"] / 2.0
        for idx, pt in enumerate(np.arange(0.0, dur, step)):
            s0, s1 = int(pt * SR), min(n, int(pt * SR) + int(0.18 * SR))
            if s1 <= s0: continue
            tp = np.arange(s1 - s0) / SR
            acc = 1.0 if idx % 4 == 0 else (0.65 if idx % 2 == 0 else 0.4)
            fb = cfg["roots"][int(pt / 6.0) % len(cfg["roots"])] * 0.75
            pulse[s0:s1] += (np.sin(2 * np.pi * fb * tp) + 0.45 * np.sin(2 * np.pi * fb * 2 * tp)) * np.exp(-tp * 14.0) * acc * 0.55
        pulse = _lp(pulse, 260, 2)

    tick = np.zeros(n)
    if cfg["tick"]:
        for tt in np.arange(0.0, dur, 60.0 / cfg["bpm"]):
            s0, s1 = int(tt * SR), min(n, int(tt * SR) + int(0.03 * SR))
            if s1 <= s0: continue
            tp = np.arange(s1 - s0) / SR
            tick[s0:s1] += _bp(rng.standard_normal(s1 - s0), 1800, 4400) * np.exp(-tp * 90.0) * 0.20

    ml = pad_l * 0.48 + pulse * 0.48 + tick
    mr = pad_r * 0.48 + pulse * 0.48 + tick
    fi_, fo = min(int(0.25 * SR), n // 4), min(int(0.80 * SR), n // 4)
    ml[:fi_] *= np.linspace(0, 1, fi_); mr[:fi_] *= np.linspace(0, 1, fi_)
    ml[-fo:] *= np.linspace(1, 0.05, fo); mr[-fo:] *= np.linspace(1, 0.05, fo)
    st = np.stack([ml, mr], axis=1)
    st = st / (np.max(np.abs(st)) + 1e-9) * 0.85
    wavfile.write(out_wav, SR, (st * 32767).astype(np.int16))


def render_sfx(name, out_wav):
    c = SFX_PRESETS[name]
    n = int(math.ceil(c["dur"] * SR))
    t = np.arange(n, dtype=np.float64) / SR
    rng = np.random.default_rng(c["seed"])
    kind = c["type"]
    if kind == "boom":
        ph = 2 * np.pi * np.cumsum(c["f0"] * np.exp(-t * 5.2) + c["f1"]) / SR
        sig = np.sin(ph) * np.exp(-t * 2.8) * 0.85 + _lp(rng.standard_normal(n), 460, 2) * np.exp(-t * 16.0) * 0.45
    elif kind == "whoosh":
        sig = _bp(rng.standard_normal(n), c["lo"], c["hi"]) * (np.sin(np.pi * t / c["dur"]) ** 1.6)
    elif kind == "riser":
        pr = t / c["dur"]
        ph = 2 * np.pi * np.cumsum(c["f0"] * (c["mul"] ** pr)) / SR
        sig = np.sin(ph) * (pr ** 2.1) * 0.55 + _bp(rng.standard_normal(n), 380, 3600) * (pr ** 2.0) * 0.45
    elif kind == "heartbeat":
        sig = np.zeros(n)
        for dt in (0.0, c["gap"]):
            s0, s1 = int(dt * SR), min(n, int((dt + 0.18) * SR))
            if s1 > s0:
                tb = np.arange(s1 - s0) / SR
                sig[s0:s1] += np.sin(2 * np.pi * c["f0"] * tb) * np.exp(-tb * 22.0)
    elif kind == "glitch":
        sig = _bp(rng.standard_normal(n), c["lo"], c["hi"]) * np.exp(-t * 22.0)
    else:  # bell
        sig = (np.sin(2 * np.pi * c["f0"] * t) + 0.4 * np.sin(2 * np.pi * c["f0"] * 2 * t)) * np.exp(-t * 2.4)
    sig = sig / (np.max(np.abs(sig)) + 1e-9) * 0.88
    st = np.stack([sig, sig], axis=1)
    wavfile.write(out_wav, SR, (st * 32767).astype(np.int16))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="120+ Copyright-Free Procedural Audio Lab")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--bgm", default=None)
    ap.add_argument("--sfx", default=None)
    ap.add_argument("--dur", type=float, default=30.0)
    ap.add_argument("--out", default="output.wav")
    ap.add_argument("--build-pack", default=None, help="Export all 120 WAV files into a directory")
    ap.add_argument("--bgm-dur", type=float, default=15.0)
    args = ap.parse_args()

    if args.list:
        print(f"TOTAL PRESETS: {len(BGM_PRESETS) + len(SFX_PRESETS)} ({len(BGM_PRESETS)} BGM + {len(SFX_PRESETS)} SFX)")
        print("BGM GENRES:", sorted(_GENRE_BASES.keys()))
        print("SFX CATEGORIES: boom_impact_01..10, whoosh_cut_01..10, riser_tension_01..10, heartbeat_01..10, glitch_hit_01..10, bell_reveal_01..10")
    elif args.bgm:
        render_bgm(args.bgm, args.dur, args.out)
        print("SAVED_BGM:", args.out)
    elif args.sfx:
        render_sfx(args.sfx, args.out)
        print("SAVED_SFX:", args.out)
    elif args.build_pack:
        bdir = os.path.join(args.build_pack, "bgm")
        sdir = os.path.join(args.build_pack, "sfx")
        os.makedirs(bdir, exist_ok=True); os.makedirs(sdir, exist_ok=True)
        for name in BGM_PRESETS:
            render_bgm(name, args.bgm_dur, os.path.join(bdir, f"{name}.wav"))
        for name in SFX_PRESETS:
            render_sfx(name, os.path.join(sdir, f"{name}.wav"))
        print(f"PACK_BUILT: {len(BGM_PRESETS)} BGM + {len(SFX_PRESETS)} SFX in {args.build_pack}")
