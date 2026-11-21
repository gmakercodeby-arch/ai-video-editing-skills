# -*- coding: utf-8 -*-
"""music_kit.py - approved dark-thriller BGM + designed SFX (unchanged sound, reusable)."""
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


def generate_cinematic_bgm_and_sfx(total_dur, sfx_events, out_wav, seed=77, bpm=118):
    sr = 48000
    n = int(math.ceil(total_dur * sr))
    t = np.arange(n, dtype=np.float64) / sr
    rng = np.random.default_rng(seed)
    chords = [[73.42, 110.0, 146.83, 174.61], [58.27, 116.54, 146.83, 174.61],
              [49.00, 98.00, 146.83, 174.61], [55.00, 110.0, 138.59, 164.81]]
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
        for fi, f0 in enumerate(chords[si % 4]):
            vib = 1.0 + 0.003 * np.sin(2 * np.pi * (0.35 + fi * 0.1) * ts)
            pl = 2 * np.pi * np.cumsum(f0 * vib) / sr
            pr = 2 * np.pi * np.cumsum(f0 * 1.003 * vib) / sr
            w = 0.28 if fi == 0 else 0.14
            sl += (np.sin(pl) + 0.45 * np.sin(2 * pl) + 0.22 * np.sin(3 * pl)) * w
            sr_ += (np.sin(pr) + 0.45 * np.sin(2 * pr) + 0.22 * np.sin(3 * pr)) * w
        pad_l[s0:s1] += sl * env
        pad_r[s0:s1] += sr_ * env
    pad_l, pad_r = _lp(pad_l, 520, sr), _lp(pad_r, 520, sr)

    pulse = np.zeros(n)
    for idx, pt in enumerate(np.arange(0.0, total_dur, 60.0 / bpm / 2.0)):
        s0, s1 = int(pt * sr), min(n, int(pt * sr) + int(0.19 * sr))
        if s1 <= s0:
            continue
        tp = np.arange(s1 - s0) / sr
        acc = 1.0 if idx % 4 == 0 else (0.65 if idx % 2 == 0 else 0.42)
        inten = 0.55 + 0.45 * (pt / max(total_dur, 1.0))
        fb = 55.0 if (int(pt / 6.0) % 4 != 1) else 58.27
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

    ml = pad_l * 0.42 + pulse * 0.50 + sfx_l * 0.65
    mr = pad_r * 0.42 + pulse * 0.50 + sfx_r * 0.65
    fi_, fo = int(0.20 * sr), int(0.80 * sr)
    ml[:fi_] *= np.linspace(0, 1, fi_); mr[:fi_] *= np.linspace(0, 1, fi_)
    ml[-fo:] *= np.linspace(1, 0.08, fo); mr[-fo:] *= np.linspace(1, 0.08, fo)
    st = np.stack([ml, mr], axis=1)
    st = st / (np.max(np.abs(st)) + 1e-9) * 0.85
    wavfile.write(out_wav, sr, (st * 32767).astype(np.int16))
