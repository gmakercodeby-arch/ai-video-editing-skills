# -*- coding: utf-8 -*-
"""
shot_guard.py - ZERO BLIND TIMESTAMPS.
  * build_shots(): PySceneDetect shot boundaries (run on a small H.264 proxy; timestamps identical)
  * safe_window(): guarantees a source window lies inside ONE shot (no surprise cut / pocket-watch)
  * probe_window(): 3-frame probe (0s, +1.5s, +3.0s of the window) -> luma + frame drift flags
  * shot_sheet(): contact sheets labelled with EXACT shot id + [start-end] for manual picking
"""
import json
import os
import subprocess

import numpy as np

SPEED = 1.03     # every clip is played 1.03x for Content-ID transformation -> source span = out_dur*1.03


def build_shots(proxy, cache_json, threshold=22.0, min_len=8):
    if os.path.exists(cache_json):
        return json.load(open(cache_json))
    from scenedetect import detect, ContentDetector
    sc = detect(proxy, ContentDetector(threshold=threshold, min_scene_len=min_len))
    shots = [[round(a.get_seconds(), 3), round(b.get_seconds(), 3)] for a, b in sc]
    json.dump(shots, open(cache_json, "w"))
    return shots


def shot_index(shots, t):
    for i, (a, b) in enumerate(shots):
        if a <= t < b:
            return i
    return len(shots) - 1


def safe_window(shots, start, out_dur, margin=0.10):
    """Return (start_adj, ok, info). ok=False -> shot too short for this clip (pick another)."""
    need = out_dur * SPEED
    i = shot_index(shots, start + 0.05)
    a, b = shots[i]
    info = {"shot": i, "shot_range": [a, b], "requested_start": round(start, 3), "need_src_s": round(need, 3)}
    if (b - a) - 2 * margin < need:
        info["too_short"] = True
        return start, False, info
    s = min(max(start, a + margin), b - margin - need)
    info["start_adj"] = round(s, 3)
    return s, True, info


def _grab(src, t):
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", src, "-frames:v", "1",
                        "-vf", "scale=64:36", "-pix_fmt", "gray", "-f", "rawvideo", "-"],
                       stdout=subprocess.PIPE)
    return np.frombuffer(p.stdout, dtype=np.uint8).astype(np.float32).reshape(36, 64) if len(p.stdout) == 64 * 36 else None


def probe_window(src, start, src_len):
    ts = [start + 0.05, start + min(1.5, src_len / 2), start + min(3.0, src_len - 0.05)]
    fr = [_grab(src, t) for t in ts]
    lumas = [round(float(f.mean()), 1) if f is not None else None for f in fr]
    diffs = [round(float(np.mean(np.abs(fr[i + 1] - fr[i]))), 1) for i in range(2) if fr[i] is not None and fr[i + 1] is not None]
    flags = []
    if any(l is not None and l < 3.0 for l in lumas):
        flags.append("BLACK_FRAME")
    if any(d > 55 for d in diffs):
        flags.append("POSSIBLE_CUT")
    return {"probe_t": [round(t, 2) for t in ts], "luma": lumas, "drift": diffs, "flags": flags}


def shot_sheets(proxy, shots, out_dir, min_shot=1.2, per_sheet=30):
    """Contact sheets of the MIDDLE frame of every shot >= min_shot, labelled 'S### start-end'."""
    from PIL import Image, ImageDraw, ImageFont
    os.makedirs(out_dir, exist_ok=True)
    font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 16)
    items = [(i, a, b) for i, (a, b) in enumerate(shots) if b - a >= min_shot]
    paths = []
    for si in range(0, len(items), per_sheet):
        chunk = items[si:si + per_sheet]
        cols, rows = 5, 6
        W, H = 320, 180
        canvas = Image.new("RGB", (cols * (W + 4) + 4, rows * (H + 4) + 4), (17, 17, 17))
        d = ImageDraw.Draw(canvas)
        for k, (i, a, b) in enumerate(chunk):
            mid = (a + b) / 2
            p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{mid:.3f}", "-i", proxy, "-frames:v", "1", "-vf", f"scale={W}:{H}",
                                "-f", "image2pipe", "-vcodec", "bmp", "-"], stdout=subprocess.PIPE)
            import io
            im = Image.open(io.BytesIO(p.stdout)).convert("RGB")
            x, y = (k % cols) * (W + 4) + 4, (k // cols) * (H + 4) + 4
            canvas.paste(im, (x, y))
            d.rectangle([x, y, x + 235, y + 22], fill=(0, 0, 0))
            d.text((x + 4, y + 2), f"S{i:03d} {a:6.1f}-{b:6.1f}s", fill=(255, 230, 0), font=font)
        path = os.path.join(out_dir, f"shots_{si // per_sheet + 1:02d}.jpg")
        canvas.save(path, quality=85)
        paths.append(path)
    return paths
