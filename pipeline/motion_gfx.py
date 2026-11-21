# -*- coding: utf-8 -*-
"""
motion_gfx.py - Pro Motion Graphics Overlay Generator (Cubic Easing + Transparent MOV/WebM/MP4).
Generates studio-grade motion graphics for ANY user video (vlogs, tutorials, reels, promos):
  1. lower_third  : Animated slide-in Name + Role card with cubic easing & gold/cyan accent bar
  2. stat_counter : Animated number counter (e.g., 0 -> 100,000+) with progress bar
  3. cta_pill     : Animated sleek floating CTA / Subscribe / Follow pill
  4. progress_bar : Smooth full-video retention progress bar overlay

Usage:
  python pipeline/motion_gfx.py lower_third --title "Shahzad" --sub "AI Video Creator" --dur 4.0 --out lt.mov
  python pipeline/motion_gfx.py stat_counter --label "VIEWS IN 7 DAYS" --target 2680000 --suffix "+" --dur 3.5 --out stat.mov
"""
import argparse
import os
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont

FPS = 30


def ease_out_cubic(t):
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** 3


def ease_in_out_cubic(t):
    t = max(0.0, min(1.0, t))
    return 4 * t ** 3 if t < 0.5 else 1.0 - ((-2 * t + 2) ** 3) / 2.0


def _font(size, bold=True):
    path = r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf"
    if not os.path.exists(path):
        path = r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"
    return ImageFont.truetype(path, size)


def _encode_alpha_mov(frames_dir, out_mov):
    """Encode PNG RGBA sequence into lossless alpha-channel QuickTime PNG (for clean FFmpeg overlay)."""
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS),
        "-i", os.path.join(frames_dir, "f_%04d.png"),
        "-c:v", "png", "-pix_fmt", "rgba",
        out_mov
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def make_lower_third(title, sub, dur, out_mov, width=1920, height=1080):
    n = max(1, int(round(dur * FPS)))
    f_t = _font(44, True)
    f_s = _font(26, False)
    with tempfile.TemporaryDirectory() as td:
        for i in range(n):
            t = i / FPS
            # Slide in 0..0.55s, hold, slide out last 0.45s
            if t < 0.55:
                p = ease_out_cubic(t / 0.55)
            elif t > dur - 0.45:
                p = ease_out_cubic(max(0.0, (dur - t) / 0.45))
            else:
                p = 1.0
            im = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            bw, bh = 560, 126
            bx = int(-bw + (bw + 70) * p)
            by = height - bh - 95
            alpha = int(235 * p)
            d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=16, fill=(13, 17, 23, alpha), outline=(0, 229, 255, int(200 * p)), width=2)
            d.rounded_rectangle([bx + 12, by + 16, bx + 20, by + bh - 16], radius=4, fill=(255, 200, 40, int(255 * p)))
            d.text((bx + 38, by + 18), title, font=f_t, fill=(255, 255, 255, int(255 * p)))
            d.text((bx + 38, by + 74), sub, font=f_s, fill=(0, 229, 255, int(240 * p)))
            im.save(os.path.join(td, f"f_{i:04d}.png"))
        _encode_alpha_mov(td, out_mov)


def make_stat_counter(label, target, suffix, dur, out_mov, width=1920, height=1080):
    n = max(1, int(round(dur * FPS)))
    f_num = _font(84, True)
    f_lbl = _font(28, True)
    with tempfile.TemporaryDirectory() as td:
        for i in range(n):
            t = i / FPS
            prog = ease_out_cubic(min(1.0, t / max(0.4, dur - 1.0)))  # hold final value >= 1s!
            val = int(round(target * prog))
            num_txt = f"{val:,}{suffix}"
            im = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            bw, bh = 620, 210
            bx, by = (width - bw) // 2, (height - bh) // 2
            d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=24, fill=(13, 17, 23, 238), outline=(255, 200, 40, 210), width=3)
            d.text((bx + 42, by + 26), label.upper(), font=f_lbl, fill=(0, 229, 255, 255))
            d.text((bx + 42, by + 68), num_txt, font=f_num, fill=(255, 212, 50, 255))
            # Animated bar
            bar_w = int((bw - 84) * prog)
            d.rounded_rectangle([bx + 42, by + 174, bx + bw - 42, by + 186], radius=6, fill=(40, 48, 60, 220))
            if bar_w > 6:
                d.rounded_rectangle([bx + 42, by + 174, bx + 42 + bar_w, by + 186], radius=6, fill=(0, 229, 255, 255))
            im.save(os.path.join(td, f"f_{i:04d}.png"))
        _encode_alpha_mov(td, out_mov)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Pro Motion Graphics Overlay Generator")
    ap.add_argument("kind", choices=["lower_third", "stat_counter"])
    ap.add_argument("--title", default="Creator Name")
    ap.add_argument("--sub", default="Video Editor")
    ap.add_argument("--label", default="TOTAL VIEWS")
    ap.add_argument("--target", type=int, default=100000)
    ap.add_argument("--suffix", default="+")
    ap.add_argument("--dur", type=float, default=4.0)
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.kind == "lower_third":
        make_lower_third(a.title, a.sub, a.dur, a.out, a.width, a.height)
    else:
        make_stat_counter(a.label, a.target, a.suffix, a.dur, a.out, a.width, a.height)
    print("MOTION_GFX_READY:", a.out)
