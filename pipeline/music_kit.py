# -*- coding: utf-8 -*-
"""
music_kit.py - 100% Copyright-Free Procedural 48kHz Stereo Cinema BGM & SFX Engine.
Supports 4 BGM moods:
  - 'dark_thriller'   : Hans-Zimmer style dark D-minor pulse + cello drone (default)
  - 'horror_suspense' : Deep sub-octave drone + eerie tritone tension + heartbeat
  - 'emotional_drama' : Warm minor-key orchestral pad swells (sad/twist endings)
  - 'action_hype'     : Fast 132 BPM driving synth-bass pulse for high-energy cuts
Supports 6 Designed SFX:
  - 'boom', 'whoosh', 'riser', 'heartbeat', 'glitch_hit', 'bell_reveal'
"""
import math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter


def _lp(sig, cutoff, sr, order=3):
    b, a = butter(order, cutoff / (0.5 * sr), btype="low")
    return lfilter(b, a, sig)


def _bp(sig, low, high, sr, order=2):
    b, a = butter(order, [low / (0.5 * sr), high / (0.5 * sr)], btype="band")
    return lfilter(b, a, sig)


MOOD_CHORDS = {
    "dark_thriller": (118, [
        [73.42, 110.0, 146.83, 174.61],   # Dm
        [58.27, 116.54, 146.83, 174.61],  # Bb
        [49.00, 98.00, 146.83, 174.61],   # Gm
        [55.00, 110.0, 138.59, 164.81],   # A
    ]),
    "horror_suspense": (92, [
        [65.41, 92.50, 130.81, 155.56],   # Cm(b5) eerie tritone
        [61.74, 92.50, 123.47, 146.83],   # Bdim tension
        [55.00, 82.41, 116.54, 155.56],   # Dark minor cluster
        [65.41, 98.00, 138.59, 155.56],
    ]),
    "emotional_drama": (84, [
        [110.0, 164.81, 220.0, 261.63],   # Am
        [87.31, 130.81, 174.61, 220.0],   # F
        [130.81, 196.0, 261.63, 329.63],  # C
        [98.00, 146.83, 196.0, 246.94],   # G
    ]),
    "action_hype": (132, [
        [82.41, 123.47, 164.81, 196.0],   # Em
        [65.41, 98.00, 130.81, 196.0],    # C
        [73.42, 110.0, 146.83, 220.0],    # D
        [61.74, 92.50, 123.47, 185.0],    # Bm
    ]),
}


def generate_cinematic_bgm_and_sfx(total_dur, sfx_events, out_wav, seed=77, bpm=None, mood="dark_thriller"):
    sr = 48000
    n = int(math.ceil(total_dur * sr))
    t = np.arange(n, dtype=np.float64) / sr
    rng = np.random.default_rng(seed)

    default_bpm, chords = MOOD_CHORDS.get(mood, MOOD_CHORDS["dark_thriller"])
    bpm = bpm or default_bpm

    pad_l, pad_r = np.zeros(n), np.zeros(n)
    seg_len = 6.0
    for si in range(int(math.ceil(total_dur / seg_len))):
        s0, s1 = int(si * seg_len * sr), min(n, int((si + 1) * seg_len * sr))
        if s1 <= s0:
            break
        ts = t[s0:s1]
        env = np.ones(s1 - s0)
        fade = min(int(0.8 * sr), (s1 - s0) // 3)
        env[:fade] = np.linspace(0, 1, fade)
        env[-fade:] = np.linspace(1, 0, fade)
        sl, sr_ = np.zeros(s1 - s0), np.zeros(s1 - s0)
        for fi, f0 in enumerate(chords[si % len(chords)]):
            vib = 1.0 + 0.003 * np.sin(2 * np.pi * (0.35 + fi * 0.1) * ts)
            pl = 2 * np.pi * np.cumsum(f0 * vib) / sr
            pr = 2 * np.pi * np.cumsum(f0 * 1.003 * vib) / sr
            w = 0.28 if fi == 0 else 0.14
            sl += (np.sin(pl) + 0.45 * np.sin(2 * pl) + 0.22 * np.sin(3 * pl)) * w
            sr_ += (np.sin(pr) + 0.45 * np.sin(2 * pr) + 0.22 * np.sin(3 * pr)) * w
        pad_l[s0:s1] += sl * env
        pad_r[s0:s1] += sr_ * env
    lp_cut = 780 if mood == "emotional_drama" else 520
    pad_l, pad_r = _lp(pad_l, lp_cut, sr), _lp(pad_r, lp_cut, sr)

    pulse = np.zeros(n)
    if mood != "emotional_drama":
        for idx, pt in enumerate(np.arange(0.0, total_dur, 60.0 / bpm / 2.0)):
            s0, s1 = int(pt * sr), min(n, int(pt * sr) + int(0.19 * sr))
            if s1 <= s0:
                continue
            tp = np.arange(s1 - s0) / sr
            acc = 1.0 if idx % 4 == 0 else (0.65 if idx % 2 == 0 else 0.42)
            inten = 0.55 + 0.45 * (pt / max(total_dur, 1.0))
            fb = chords[int(pt / 6.0) % len(chords)][0] * 0.75
            pulse[s0:s1] += (np.sin(2 * np.pi * fb * tp) + 0.5 * np.sin(2 * np.pi * fb * 2 * tp)) * np.exp(-tp * 14.0) * acc * inten * 0.55
        pulse = _lp(pulse, 260, sr, 2)

    sfx_l, sfx_r = np.zeros(n), np.zeros(n)
    for ev_t, kind in sfx_events:
        if kind == "boom":
            s0 = max(0, int(ev_t * sr)); s1 = min(n, s0 + int(1.0 * sr))
            if s1 <= s0: continue
            tb = np.arange(s1 - s0) / sr
            ph = 2 * np.pi * np.cumsum(115.0 * np.exp(-tb * 5.5) + 34.0) / sr
            boom = np.sin(ph) * np.exp(-tb * 2.8) * 0.85 + _lp(rng.standard_normal(s1 - s0), 450, sr, 2) * np.exp(-tb * 18.0) * 0.4
            sfx_l[s0:s1] += boom; sfx_r[s0:s1] += boom
        elif kind == "whoosh":
            s0 = max(0, int((ev_t - 0.16) * sr)); wl = int(0.42 * sr); s1 = min(n, s0 + wl)
            if s1 <= s0: continue
            tw = np.arange(s1 - s0) / sr
            wn = _bp(rng.standard_normal(s1 - s0), 300, 2200, sr) * np.sin(np.pi * tw / (wl / sr)) ** 1.6 * 0.35
            sfx_l[s0:s1] += wn * 0.9; sfx_r[s0:s1] += wn * 1.1
        elif kind == "riser":
            s0 = max(0, int((ev_t - 2.0) * sr)); rl = int(2.2 * sr); s1 = min(n, s0 + rl)
            if s1 <= s0: continue
            pr_ = (np.arange(s1 - s0) / sr) / (rl / sr)
            ph = 2 * np.pi * np.cumsum(120.0 * (3.2 ** pr_)) / sr
            rise = np.sin(ph) * (pr_ ** 2.2) * 0.35 + _bp(rng.standard_normal(s1 - s0), 400, 3500, sr) * (pr_ ** 2.0) * 0.35
            sfx_l[s0:s1] += rise; sfx_r[s0:s1] += rise
        elif kind == "heartbeat":
            for dt in (0.0, 0.24):
                s0 = max(0, int((ev_t + dt) * sr)); s1 = min(n, s0 + int(0.18 * sr))
                if s1 <= s0: continue
                tb = np.arange(s1 - s0) / sr
                hb = np.sin(2 * np.pi * 52.0 * tb) * np.exp(-tb * 22.0) * 0.75
                sfx_l[s0:s1] += hb; sfx_r[s0:s1] += hb
        elif kind == "glitch_hit":
            s0 = max(0, int(ev_t * sr)); s1 = min(n, s0 + int(0.18 * sr))
            if s1 <= s0: continue
            tb = np.arange(s1 - s0) / sr
            gl = _bp(rng.standard_normal(s1 - s0), 1200, 5500, sr) * np.exp(-tb * 24.0) * 0.6
            sfx_l[s0:s1] += gl; sfx_r[s0:s1] += gl
        elif kind == "bell_reveal":
            s0 = max(0, int(ev_t * sr)); s1 = min(n, s0 + int(1.6 * sr))
            if s1 <= s0: continue
            tb = np.arange(s1 - s0) / sr
            bell = (np.sin(2 * np.pi * 587.33 * tb) + 0.4 * np.sin(2 * np.pi * 1174.66 * tb)) * np.exp(-tb * 2.5) * 0.45
            sfx_l[s0:s1] += bell; sfx_r[s0:s1] += bell

    ml = pad_l * 0.42 + pulse * 0.50 + sfx_l * 0.65
    mr = pad_r * 0.42 + pulse * 0.50 + sfx_r * 0.65
    fi_, fo = int(0.20 * sr), int(0.80 * sr)
    ml[:fi_] *= np.linspace(0, 1, fi_); mr[:fi_] *= np.linspace(0, 1, fi_)
    ml[-fo:] *= np.linspace(1, 0.08, fo); mr[-fo:] *= np.linspace(1, 0.08, fo)
    st = np.stack([ml, mr], axis=1)
    st = st / (np.max(np.abs(st)) + 1e-9) * 0.85
    wavfile.write(out_wav, sr, (st * 32767).astype(np.int16))
