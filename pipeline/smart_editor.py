# -*- coding: utf-8 -*-
"""
smart_editor.py - Pro Auto-Editor for ANY Normal User Video (Vlogs, Talking-Head, Tutorials, Reels).
Features:
  1. Auto Dead-Air / Silence Removal (30ms crossfades at every cut - zero audio pops!)
  2. Pro Color Grading presets ('warm_cinematic', 'neutral_punch', 'cold_teal', 'none')
  3. Optional Motion Graphics Lower-Third overlay (via pipeline/motion_gfx.py)
  4. Optional Auto Word-Synced Subtitles (faster-whisper small -> libass burned LAST!)
  5. Optional Copyright-Free BGM from pipeline/audio_lab.py (sidechain-ducked under speech!)
  6. Broadcast Mastering (-14 LUFS, yuv420p, +faststart)

Usage:
  python pipeline/smart_editor.py input.mp4 -o edited.mp4 --grade neutral_punch --trim-silence --subs --lower-third "Shahzad|Tech Creator" --bgm documentary_01
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audio_lab import render_bgm  # noqa: E402
from motion_gfx import make_lower_third  # noqa: E402

GRADES = {
    "none": "",
    "neutral_punch": "eq=contrast=1.10:saturation=1.08,unsharp=3:3:0.6:3:3:0.3",
    "warm_cinematic": "colorbalance=rs=0.05:gs=0.01:bs=-0.06:rh=0.04:bh=-0.04,eq=contrast=1.12:saturation=0.95,unsharp=3:3:0.7:3:3:0.3",
    "cold_teal": "colorbalance=rs=-0.08:gs=0.03:bs=0.11,eq=contrast=1.16:saturation=1.18,unsharp=5:5:1.0:3:3:0.4",
}


def probe(path):
    p = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", path],
                       stdout=subprocess.PIPE, text=True, check=True)
    meta = json.loads(p.stdout)
    vs = next(s for s in meta["streams"] if s["codec_type"] == "video")
    return int(vs["width"]), int(vs["height"]), float(meta["format"]["duration"])


def detect_keep_ranges(video_path, dur, min_silence=0.55, noise_db="-36dB", pad=0.06):
    res = subprocess.run(["ffmpeg", "-i", video_path, "-af", f"silencedetect=noise={noise_db}:d={min_silence}", "-f", "null", "-"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    starts = [float(x) for x in re.findall(r"silence_start:\s*([\d\.]+)", res.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([\d\.]+)", res.stderr)]
    silences = list(zip(starts, ends + [dur]))
    keeps, cur = [], 0.0
    for s0, s1 in silences:
        e = min(dur, s0 + pad)
        if e - cur >= 0.25:
            keeps.append((cur, e))
        cur = max(0.0, s1 - pad)
    if dur - cur >= 0.25:
        keeps.append((cur, dur))
    return keeps or [(0.0, dur)]


def build_auto_subs(video_path, ass_path, width, height):
    """Run faster-whisper small and build crisp libass captions (Spacing=0)."""
    wav = ass_path + ".wav"
    subprocess.run(["ffmpeg", "-y", "-i", video_path, "-vn", "-ac", "1", "-ar", "16000", wav],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import numpy as np
    from scipy.io import wavfile
    from faster_whisper import WhisperModel
    sr, data = wavfile.read(wav)
    audio = data.astype(np.float32) / 32768.0
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(audio, word_timestamps=True)
    words = [w for s in segs for w in (s.words or [])]

    def ft(sec):
        return f"{int(sec//3600)}:{int((sec%3600)//60):02d}:{sec%60:05.2f}"

    fs = 68 if height > width else 52
    mv = 280 if height > width else 65
    lines = [
        f"[Script Info]\nScriptType: v4.00+\nPlayResX: {width}\nPlayResY: {height}\n\n"
        "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,Nirmala UI,{fs},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,3,2,60,60,{mv},1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    ]
    for i in range(0, len(words), 3):
        chunk = words[i:i + 3]
        txt = " ".join(w.word.strip() for w in chunk).strip()
        if txt:
            lines.append(f"Dialogue: 0,{ft(chunk[0].start)},{ft(chunk[-1].end)},Default,,0,0,0,,{txt}\n")
    open(ass_path, "w", encoding="utf-8-sig").writelines(lines)


def main():
    ap = argparse.ArgumentParser(description="Pro Auto-Editor for Any User Video")
    ap.add_argument("input", help="Source MP4/MOV video")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--grade", default="neutral_punch", choices=list(GRADES.keys()))
    ap.add_argument("--trim-silence", action="store_true")
    ap.add_argument("--subs", action="store_true")
    ap.add_argument("--lower-third", default=None, help="Format: 'Name|Role'")
    ap.add_argument("--bgm", default=None, help="Audio Lab preset name (e.g. documentary_01)")
    a = ap.parse_args()

    w, h, dur = probe(a.input)
    with tempfile.TemporaryDirectory() as td:
        # 1. Cut dead air (with 30ms audio fades at every boundary - Hard Rule #3!)
        ranges = detect_keep_ranges(a.input, dur) if a.trim_silence else [(0.0, dur)]
        print(f"1) Segments kept: {len(ranges)} (from {dur:.1f}s)")
        seg_files = []
        grade_f = GRADES[a.grade]
        for idx, (s0, s1) in enumerate(ranges):
            sdur = max(0.1, s1 - s0)
            seg_out = os.path.join(td, f"seg_{idx:03d}.mp4")
            vf = (grade_f + "," if grade_f else "") + "fps=30,setsar=1,format=yuv420p"
            af = f"afade=t=in:st=0:d=0.03,afade=t=out:st={max(0.0, sdur - 0.03):.3f}:d=0.03"
            subprocess.run([
                "ffmpeg", "-y", "-ss", f"{s0:.3f}", "-i", a.input, "-t", f"{sdur:.3f}",
                "-vf", vf, "-af", af,
                "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", seg_out
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            seg_files.append(f"file '{seg_out.replace(os.sep, '/')}'\n")

        clist = os.path.join(td, "concat.txt")
        open(clist, "w").writelines(seg_files)
        base_mp4 = os.path.join(td, "base.mp4")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", clist, "-c", "copy", base_mp4],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        _, _, new_dur = probe(base_mp4)
        print(f"2) Base edited duration: {new_dur:.2f}s")

        # 2. Optional Motion Graphics Lower-Third (PTS-shifted overlay)
        inputs = ["-i", base_mp4]
        v_chain = "[0:v]"
        if a.lower_third:
            parts = a.lower_third.split("|", 1)
            lt_mov = os.path.join(td, "lt.mov")
            make_lower_third(parts[0].strip(), parts[1].strip() if len(parts) > 1 else "", min(4.2, new_dur), lt_mov, w, h)
            inputs += ["-i", lt_mov]
            v_chain = "[1:v]setpts=PTS-STARTPTS+0.5/TB[lt];[0:v][lt]overlay=0:0:eof_action=pass[v_ov]"
            v_out = "[v_ov]"
        else:
            v_out = "[0:v]"

        # 3. Optional Auto Subtitles (APPLIED LAST - Hard Rule #1!)
        if a.subs:
            ass_path = os.path.join(td, "subs.ass")
            build_auto_subs(base_mp4, ass_path, w, h)
            ass_esc = ass_path.replace("\\", "/").replace(":", "\\:")
            if v_chain == "[0:v]":
                v_chain = f"[0:v]ass='{ass_esc}'[v_sub]"
            else:
                v_chain += f";{v_out}ass='{ass_esc}'[v_sub]"
            v_out = "[v_sub]"

        # 4. Optional Copyright-Free BGM with sidechain ducking + -14 LUFS master
        if a.bgm:
            bgm_wav = os.path.join(td, "bgm.wav")
            render_bgm(a.bgm, new_dur, bgm_wav)
            bgm_idx = len(inputs) // 2
            inputs += ["-i", bgm_wav]
            a_chain = (
                f"[0:a]aformat=channel_layouts=stereo,asplit=2[vm][vs];"
                f"[{bgm_idx}:a]volume=0.22,atrim=0:{new_dur:.3f},aformat=channel_layouts=stereo[bi];"
                f"[bi][vs]sidechaincompress=threshold=0.025:ratio=5:attack=15:release=220[bd];"
                f"[vm][bd]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14.0:TP=-1.2:LRA=7[aout]"
            )
        else:
            a_chain = "[0:a]loudnorm=I=-14.0:TP=-1.2:LRA=7[aout]"

        fc = (v_chain + ";" if v_chain != "[0:v]" else "") + a_chain
        cmd = ["ffmpeg", "-y"] + inputs + [
            "-filter_complex", fc,
            "-map", v_out, "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", a.output
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("EDIT_COMPLETE:", a.output)


if __name__ == "__main__":
    main()
