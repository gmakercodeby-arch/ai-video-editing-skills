# -*- coding: utf-8 -*-
"""
whisper_worker.py - CPU-safe Whisper guard worker (faster-whisper `small`, int8, CPU).
Runs in the project venv as a long-lived subprocess so the TTS interpreter (which may
not have faster-whisper) can still verify every beat.  Protocol (stdout lines prefixed '@@'):
    -> {"wav": "path.wav"}   <- {"ok":true,"text":"...","words":[{"w","s","e"}]}
NEVER use large-v3 here (far too slow on CPU).
"""
import json
import sys
from math import gcd

import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly

sys.stdout.reconfigure(encoding="utf-8")
from faster_whisper import WhisperModel  # noqa: E402

model = WhisperModel("small", device="cpu", compute_type="int8")
print("@@READY", flush=True)

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        req = json.loads(line)
        sr, data = wavfile.read(req["wav"])
        if data.ndim > 1:
            data = data.mean(axis=1)
        audio = data.astype(np.float32)
        if data.dtype == np.int16:
            audio /= 32768.0
        g = gcd(sr, 16000)
        audio = resample_poly(audio, 16000 // g, sr // g).astype(np.float32)
        segs, _info = model.transcribe(
            audio, language="hi", word_timestamps=True, beam_size=5,
            condition_on_previous_text=False, temperature=0.0,
        )
        words, texts = [], []
        for s in segs:
            texts.append(s.text.strip())
            for w in (s.words or []):
                words.append({"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)})
        out = {"ok": True, "text": " ".join(texts), "words": words}
    except Exception as exc:  # noqa: BLE001
        out = {"ok": False, "err": repr(exc)}
    print("@@" + json.dumps(out, ensure_ascii=False), flush=True)
