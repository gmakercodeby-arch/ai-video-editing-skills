#!/usr/bin/env python3
"""
100% FREE Local Reference Video Style Cloner (Zero Paywall)
Analyzes any reference video's structural editing grammar:
  - Exact dimensions, aspect ratio, rational FPS, frame count
  - Frame-exact shot cuts (floor(frame / fps)) & pacing rhythm (cuts/min, avg shot length)
  - Visual color temperature, brightness, saturation & ready-to-use FFmpeg grade filter
  - Audio loudness profile (Integrated LUFS, True Peak, LRA)
  - Optional 3x3 visual storyboard sheet for AI/human layout inspection

Outputs a plug-and-play `style_profile.json` so you can apply the same pacing,
look, and energy to your own original content without stealing footage or paying $25/mo.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any


def run_cmd(cmd: list[str], timeout: int = 180) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def parse_rational(val: str) -> tuple[int, int, float]:
    if not val or val == "0/0":
        return 30, 1, 30.0
    if "/" in val:
        n, d = val.split("/", 1)
        ni, di = int(n), max(int(d), 1)
        return ni, di, ni / di
    f = float(val)
    return int(round(f)), 1, f


def probe_video_details(video_path: Path) -> dict[str, Any]:
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,avg_frame_rate,nb_frames,codec_name:format=duration,bit_rate",
        "-of", "json", str(video_path),
    ]
    rc, out, err = run_cmd(cmd, timeout=30)
    if rc != 0:
        raise RuntimeError(f"ffprobe failed: {err.strip()}")
    data = json.loads(out)
    stream = (data.get("streams") or [{}])[0]
    fmt = data.get("format") or {}

    w = int(stream.get("width", 1080))
    h = int(stream.get("height", 1920))
    fps_str = stream.get("r_frame_rate") or stream.get("avg_frame_rate") or "30/1"
    num, den, fps = parse_rational(fps_str)
    duration = float(fmt.get("duration") or 0.0)
    nb_frames = int(stream.get("nb_frames") or round(duration * fps))
    exact_duration = nb_frames / fps if fps > 0 and nb_frames > 0 else duration

    ratio = w / max(h, 1)
    if abs(ratio - 9 / 16) < 0.08:
        aspect = "9:16"
    elif abs(ratio - 16 / 9) < 0.08:
        aspect = "16:9"
    elif abs(ratio - 1.0) < 0.08:
        aspect = "1:1"
    else:
        aspect = f"{w}:{h}"

    return {
        "width": w,
        "height": h,
        "aspect_ratio": aspect,
        "fps_rational": f"{num}/{den}",
        "fps": round(fps, 4),
        "total_frames": nb_frames,
        "duration_sec": round(exact_duration, 6),
        "codec": stream.get("codec_name", "unknown"),
    }


def detect_frame_exact_cuts(video_path: Path, fps: float, duration: float, threshold: float = 0.28) -> dict[str, Any]:
    """Detect scene cuts using FFmpeg select=gt(scene,threshold) with frame-exact floor timing."""
    cmd = [
        "ffmpeg", "-hide_banner", "-i", str(video_path),
        "-vf", f"select='gt(scene,{threshold})',showinfo",
        "-f", "null", "-",
    ]
    _, _, stderr = run_cmd(cmd, timeout=240)

    cuts: list[dict[str, Any]] = [{"frame": 0, "time_sec": 0.0}]
    for m in re.finditer(r"pts_time:([0-9.]+)", stderr):
        t = float(m.group(1))
        frame = int(math.floor(t * fps + 1e-6))
        floored_t = round(math.floor(frame) / fps, 6) if fps > 0 else round(t, 6)
        # Merge micro-detections closer than 0.25s
        if floored_t - cuts[-1]["time_sec"] >= 0.25:
            cuts.append({"frame": frame, "time_sec": floored_t})

    shot_lengths: list[float] = []
    for i in range(len(cuts)):
        t0 = cuts[i]["time_sec"]
        t1 = cuts[i + 1]["time_sec"] if i + 1 < len(cuts) else duration
        length = max(0.0, round(t1 - t0, 3))
        if length > 0.05:
            shot_lengths.append(length)

    avg_shot = round(statistics.mean(shot_lengths), 2) if shot_lengths else round(duration, 2)
    med_shot = round(statistics.median(shot_lengths), 2) if shot_lengths else round(duration, 2)
    cuts_per_min = round((len(cuts) / max(duration, 0.1)) * 60.0, 1)

    if avg_shot <= 2.3:
        pacing_style = "hyper_viral_shorts"
        recommended_range = [1.4, 2.2]
    elif avg_shot <= 4.2:
        pacing_style = "fast_recap_retention"
        recommended_range = [2.0, 3.8]
    elif avg_shot <= 7.5:
        pacing_style = "explainer_medium"
        recommended_range = [3.5, 6.5]
    else:
        pacing_style = "cinematic_slow"
        recommended_range = [6.0, 10.0]

    return {
        "cut_count": len(cuts),
        "cuts_per_minute": cuts_per_min,
        "avg_shot_sec": avg_shot,
        "median_shot_sec": med_shot,
        "min_shot_sec": round(min(shot_lengths), 2) if shot_lengths else 0.0,
        "max_shot_sec": round(max(shot_lengths), 2) if shot_lengths else 0.0,
        "pacing_style": pacing_style,
        "recommended_cut_window_sec": recommended_range,
        "cuts": cuts[:120],  # cap JSON size on very long movies
    }


def analyze_color_profile(video_path: Path, duration: float) -> dict[str, Any]:
    """Sample up to 12 evenly spaced frames via FFmpeg signalstats for brightness/saturation/mood."""
    sample_fps = max(0.05, min(1.0, 12.0 / max(duration, 1.0)))
    cmd = [
        "ffmpeg", "-hide_banner", "-i", str(video_path),
        "-vf", f"fps={sample_fps:.4f},scale=320:-2,signalstats,metadata=print:file=-",
        "-f", "null", "-",
    ]
    _, stdout, _ = run_cmd(cmd, timeout=120)

    yavgs = [float(x) for x in re.findall(r"lavfi\.signalstats\.YAVG=([0-9.]+)", stdout)]
    satavgs = [float(x) for x in re.findall(r"lavfi\.signalstats\.SATAVG=([0-9.]+)", stdout)]
    huemeds = [float(x) for x in re.findall(r"lavfi\.signalstats\.HUEMED=([0-9.]+)", stdout)]

    avg_luma = round(statistics.mean(yavgs), 1) if yavgs else 110.0
    avg_sat = round(statistics.mean(satavgs), 1) if satavgs else 45.0
    med_hue = round(statistics.median(huemeds), 1) if huemeds else 180.0

    # Derive visual mood & matching FFmpeg grade filter
    if avg_luma < 85:
        exposure_mood = "dark_moody"
        eq_brightness = -0.04
        eq_contrast = 1.12
    elif avg_luma > 155:
        exposure_mood = "bright_clean"
        eq_brightness = 0.03
        eq_contrast = 1.05
    else:
        exposure_mood = "balanced_cinema"
        eq_brightness = -0.01
        eq_contrast = 1.08

    if avg_sat > 65:
        sat_mood = "vibrant_punchy"
        eq_sat = 1.18
    elif avg_sat < 30:
        sat_mood = "desaturated_noir"
        eq_sat = 0.85
    else:
        sat_mood = "natural_filmic"
        eq_sat = 1.06

    # Hue rough temperature (BT.709 signalstats hue angle)
    if 150 <= med_hue <= 260:
        temp_mood = "cool_teal_cinema"
        cb = "colorbalance=rs=-0.03:gs=0.01:bs=0.05:rm=-0.02:bm=0.03"
    elif med_hue < 80 or med_hue > 310:
        temp_mood = "warm_golden_drama"
        cb = "colorbalance=rs=0.04:gs=0.01:bs=-0.03:rm=0.03:bm=-0.02"
    else:
        temp_mood = "neutral_balanced"
        cb = "colorbalance=rs=0.0:gs=0.0:bs=0.0"

    ffmpeg_grade = f"eq=contrast={eq_contrast}:brightness={eq_brightness}:saturation={eq_sat},{cb},unsharp=5:5:0.45:5:5:0.0"

    return {
        "avg_luma_0_255": avg_luma,
        "avg_saturation": avg_sat,
        "median_hue_deg": med_hue,
        "mood_tags": [exposure_mood, sat_mood, temp_mood],
        "recommended_ffmpeg_grade": ffmpeg_grade,
    }


def analyze_audio_loudness(video_path: Path) -> dict[str, Any]:
    cmd = [
        "ffmpeg", "-hide_banner", "-i", str(video_path),
        "-af", "ebur128=peak=true", "-f", "null", "-",
    ]
    _, _, stderr = run_cmd(cmd, timeout=180)
    i_match = re.findall(r"I:\s*(-?[0-9.]+)\s*LUFS", stderr)
    lra_match = re.findall(r"LRA:\s*([0-9.]+)\s*LU", stderr)
    tp_match = re.findall(r"Peak:\s*(-?[0-9.]+)\s*dBFS", stderr)

    lufs = float(i_match[-1]) if i_match else -14.0
    lra = float(lra_match[-1]) if lra_match else 6.0
    tp = float(tp_match[-1]) if tp_match else -1.0

    return {
        "integrated_lufs": lufs,
        "loudness_range_lu": lra,
        "true_peak_dbfs": tp,
        "recommended_target_lufs": round(max(-16.0, min(-12.5, lufs)), 1),
    }


def export_storyboard(video_path: Path, out_png: Path, duration: float) -> bool:
    step = max(duration / 9.5, 0.2)
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-i", str(video_path),
        "-vf", f"fps=1/{step:.3f},scale=360:-2,tile=3x3:padding=6:margin=6",
        "-frames:v", "1", str(out_png),
    ]
    rc, _, _ = run_cmd(cmd, timeout=60)
    return rc == 0 and out_png.exists()


def main() -> int:
    parser = argparse.ArgumentParser(description="100% FREE Local Reference Video Style Cloner")
    parser.add_argument("video", type=Path, help="Reference video file (.mp4/.mkv/.mov)")
    parser.add_argument("--out", type=Path, default=Path("style_profile.json"), help="Output style JSON path")
    parser.add_argument("--sheet", type=Path, help="Optional 3x3 storyboard PNG path for visual inspection")
    parser.add_argument("--threshold", type=float, default=0.28, help="Scene cut sensitivity (default: 0.28)")
    args = parser.parse_args()

    if not args.video.exists():
        print(f"[ERROR] Reference video not found: {args.video}", file=sys.stderr)
        return 1

    print(f"[1/4] Probing video format: {args.video.name}...")
    vid = probe_video_details(args.video)

    print(f"[2/4] Detecting frame-exact cuts ({vid['fps']}fps, threshold={args.threshold})...")
    rhythm = detect_frame_exact_cuts(args.video, vid["fps"], vid["duration_sec"], args.threshold)

    print("[3/4] Sampling color palette & grading profile...")
    color = analyze_color_profile(args.video, vid["duration_sec"])

    print("[4/4] Measuring EBUR128 audio loudness profile...")
    audio = analyze_audio_loudness(args.video)

    sheet_saved = None
    if args.sheet:
        args.sheet.parent.mkdir(parents=True, exist_ok=True)
        if export_storyboard(args.video, args.sheet, vid["duration_sec"]):
            sheet_saved = str(args.sheet.resolve())

    profile = {
        "source_file": args.video.name,
        "video": vid,
        "pacing": rhythm,
        "color": color,
        "audio": audio,
        "safe_zone": {
            "action_safe_pct": 90,
            "title_safe_pct": 80,
            "shorts_bottom_clear_pct": 20 if vid["aspect_ratio"] == "9:16" else 8,
        },
        "storyboard_png": sheet_saved,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n[OK] Style profile saved -> {args.out}")
    print(f"     Canvas : {vid['width']}x{vid['height']} ({vid['aspect_ratio']}) @ {vid['fps']}fps ({vid['duration_sec']}s)")
    print(f"     Pacing : {rhythm['pacing_style']} | {rhythm['cut_count']} cuts ({rhythm['cuts_per_minute']}/min, avg {rhythm['avg_shot_sec']}s)")
    print(f"     Look   : {', '.join(color['mood_tags'])}")
    print(f"     Audio  : {audio['integrated_lufs']} LUFS (target: {audio['recommended_target_lufs']} LUFS)")
    if sheet_saved:
        print(f"     Sheet  : {sheet_saved}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
