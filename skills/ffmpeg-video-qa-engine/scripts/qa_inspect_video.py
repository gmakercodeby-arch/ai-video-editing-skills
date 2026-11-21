"""
Post-Render Video QA Inspector v2
(Probe + EBUR128 + Outro Check + ASS Audit + 3x3 Storyboard
 + FULL-RES BANNER ZOOM + WHISPER SIMILARITY REPORT + CLIP/SHOT MANIFEST AUDIT)
Part of the ffmpeg-video-qa-engine global Antigravity skill.

Mandatory v2 checks (added after the Meridian audit):
  (a) qa_banner_zoom.png  - 1080px-wide crop of the top banner; the AGENT must open it and verify that
      every Devanagari matra is intact (Pillow without raqm silently breaks them).
  (b) --audio-report audio_report.json (written by pipeline/audio_guard.py) - per-beat Whisper
      similarity; ANY beat < 0.72, failed beat, or abrupt end is an ISSUE; fallback beats are WARNINGS.
  (c) --clip-manifest clips_manifest.json - hflip usage + shot-guard probe flags per clip.
"""
import os
import re
import sys
import json
import argparse
import subprocess

SIM_MIN = 0.72


def run_cmd(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")


def probe_video(video_path):
    res = run_cmd(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", video_path])
    if res.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {res.stderr}")
    return json.loads(res.stdout)


def check_ebur128(video_path):
    txt = run_cmd(["ffmpeg", "-i", video_path, "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
    i_match = re.findall(r"I:\s+([-\d.]+)\s+LUFS", txt)
    lra_match = re.findall(r"LRA:\s+([-\d.]+)\s+LU", txt)
    peak_match = re.findall(r"Peak:\s+([-\d.]+)\s+dBFS", txt)
    return {
        "integrated_lufs": float(i_match[-1]) if i_match else None,
        "lra_lu": float(lra_match[-1]) if lra_match else None,
        "true_peak_dbfs": float(peak_match[-1]) if peak_match else None,
    }


def check_outro_audio(video_path, duration):
    st = max(0.0, duration - 1.0)
    res = run_cmd(["ffmpeg", "-ss", f"{st:.2f}", "-i", video_path, "-t", "1.0", "-af", "volumedetect", "-f", "null", "-"])
    m_mean = re.search(r"mean_volume:\s+([-\d.]+)\s+dB", res.stderr)
    m_max = re.search(r"max_volume:\s+([-\d.]+)\s+dB", res.stderr)
    return {
        "outro_mean_db": float(m_mean.group(1)) if m_mean else None,
        "outro_max_db": float(m_max.group(1)) if m_max else None,
    }


def check_ass_file(ass_path):
    """Spacing must be 0 on EVERY style; overlaps are audited per style (banner events span the whole video)."""
    if not ass_path or not os.path.exists(ass_path):
        return None
    overlaps, bad_spacing, events = 0, False, 0
    prev_end = {}
    styles = []

    def parse_t(s):
        h, m, sec = s.strip().split(":")
        return int(h) * 3600 + int(m) * 60 + float(sec)

    with open(ass_path, "r", encoding="utf-8-sig") as f:
        for line in f:
            if line.startswith("Style:"):
                cols = line.split(",")
                styles.append(cols[0].split(":", 1)[1].strip())
                if len(cols) > 13:
                    try:
                        if float(cols[13]) != 0.0:
                            bad_spacing = True
                    except ValueError:
                        pass
            elif line.startswith("Dialogue:"):
                events += 1
                parts = line.split(",", 9)
                st, en, style = parse_t(parts[1]), parse_t(parts[2]), parts[3].strip()
                pe = prev_end.get(style, -1.0)
                if st < pe - 0.002 or en <= st:
                    overlaps += 1
                prev_end[style] = en
    return {"events": events, "overlaps": overlaps, "nonzero_spacing_bug": bad_spacing,
            "styles": styles, "has_banner_styles": ("BannerTitle" in styles and "BannerHook" in styles)}


def build_storyboard(video_path, duration, out_jpg, is_vertical=True):
    tw, th = (360, 640) if is_vertical else (640, 360)
    fps_expr = f"9/{max(duration, 1.0):.3f}"
    res = run_cmd(["ffmpeg", "-y", "-i", video_path, "-vf",
                   f"fps={fps_expr},scale={tw}:{th},tile=3x3:padding=8:margin=8:color=0x111111",
                   "-frames:v", "1", "-update", "1", "-q:v", "3", out_jpg])
    return out_jpg if (res.returncode == 0 and os.path.exists(out_jpg)) else None


def build_banner_zoom(video_path, duration, out_png, y0=105, y1=325):
    """Full-resolution (video width) crop of the top banner - agent MUST open this and read the Hindi."""
    t = min(2.0, max(0.2, duration / 2))
    res = run_cmd(["ffmpeg", "-y", "-ss", f"{t:.2f}", "-i", video_path, "-frames:v", "1", "-update", "1",
                   "-vf", f"crop=iw:{y1 - y0}:0:{y0}", out_png])
    return out_png if (res.returncode == 0 and os.path.exists(out_png)) else None


def audit_audio_report(path):
    rep = json.load(open(path, encoding="utf-8"))
    issues, warns, rows = [], [], []
    for b in rep["beats"]:
        rows.append({"id": b["id"], "similarity": b["similarity"], "engine": b["engine"], "status": b["status"],
                     "tail_ok": b["tail_ok"], "abrupt_end": b["abrupt_end"], "attempts": len(b["attempts"])})
        if b["similarity"] < SIM_MIN:
            issues.append(f"Beat {b['id']} Whisper similarity {b['similarity']} < {SIM_MIN}")
        if b["status"] == "FAILED_QA":
            issues.append(f"Beat {b['id']} FAILED audio QA but was shipped")
        if not b["tail_ok"]:
            issues.append(f"Beat {b['id']} last word not intact (mid-word cut)")
        if b["abrupt_end"]:
            issues.append(f"Beat {b['id']} ends abruptly")
        if b["engine"] != rep.get("primary_engine", b["engine"]) or "fallback" in b["engine"]:
            warns.append(f"Beat {b['id']} used fallback voice ({b['engine']})")
    return {"min_similarity": rep.get("min_similarity"), "threshold": rep.get("threshold"), "beats": rows}, issues, warns


def audit_clip_manifest(path):
    man = json.load(open(path, encoding="utf-8"))
    clips = man["clips"]
    flipped = sum(1 for c in clips if c.get("flip"))
    issues, warns = [], []
    for c in clips:
        if c.get("out_dur", 0) > 4.5:
            issues.append(f"Clip {c['n']} is {c['out_dur']}s (> 4.5s cap)")
        for fl in c.get("probe", {}).get("flags", []):
            warns.append(f"Clip {c['n']} probe flag {fl} @ src {c['src_start']}s")
    return {"clips": len(clips), "hflip_on": flipped, "hflip_off": len(clips) - flipped,
            "hflip_off_reasons": {c["n"]: c.get("flip_reason") for c in clips if not c.get("flip")}}, issues, warns


def main():
    parser = argparse.ArgumentParser(description="Post-Render Video QA Inspector v2")
    parser.add_argument("video", help="Path to rendered MP4 file")
    parser.add_argument("--ass", default=None, help="Optional path to .ass subtitle file")
    parser.add_argument("--out-img", default=None, help="Output path for 3x3 QA storyboard JPEG")
    parser.add_argument("--banner-out", default=None, help="Output path for banner zoom PNG (default: <dir>/qa_banner_zoom.png)")
    parser.add_argument("--audio-report", default=None, help="audio_report.json from pipeline/audio_guard.py")
    parser.add_argument("--clip-manifest", default=None, help="clips_manifest.json from the build script")
    parser.add_argument("--require-banner-ass", action="store_true", help="Fail if BannerTitle/BannerHook ASS styles are missing")
    args = parser.parse_args()

    if not os.path.exists(args.video):
        print(f"ERROR: Video not found: {args.video}")
        sys.exit(1)

    meta = probe_video(args.video)
    v_stream = next((s for s in meta["streams"] if s["codec_type"] == "video"), None)
    a_stream = next((s for s in meta["streams"] if s["codec_type"] == "audio"), None)
    v_dur = float(v_stream.get("duration") or meta["format"].get("duration") or 0.0) if v_stream else 0.0
    a_dur = float(a_stream.get("duration") or 0.0) if a_stream else 0.0
    w = int(v_stream.get("width", 0)) if v_stream else 0
    h = int(v_stream.get("height", 0)) if v_stream else 0
    fps = v_stream.get("avg_frame_rate", "0/0") if v_stream else "0/0"

    loud = check_ebur128(args.video)
    outro = check_outro_audio(args.video, v_dur)
    ass_info = check_ass_file(args.ass)

    out_img = args.out_img or os.path.splitext(args.video)[0] + "_qa_3x3.jpg"
    sb = build_storyboard(args.video, v_dur, out_img, is_vertical=(h > w))
    banner_png = None
    if h > w:
        banner_png = build_banner_zoom(args.video, v_dur, args.banner_out or os.path.join(os.path.dirname(os.path.abspath(args.video)), "qa_banner_zoom.png"))

    issues, warns = [], []
    if abs(v_dur - a_dur) > 0.25:
        issues.append(f"A/V duration mismatch: video={v_dur:.2f}s vs audio={a_dur:.2f}s")
    if loud["integrated_lufs"] is not None and not (-16.0 <= loud["integrated_lufs"] <= -11.5):
        issues.append(f"Loudness outside target (-14 LUFS): {loud['integrated_lufs']} LUFS")
    if loud["true_peak_dbfs"] is not None and loud["true_peak_dbfs"] > -0.8:
        issues.append(f"True peak near clipping: {loud['true_peak_dbfs']} dBFS")
    if outro["outro_mean_db"] is not None and outro["outro_mean_db"] < -50.0:
        issues.append(f"Outro last 1s is nearly silent ({outro['outro_mean_db']} dB)")
    if ass_info:
        if ass_info["overlaps"] > 0:
            issues.append(f"ASS has {ass_info['overlaps']} overlapping caption events")
        if ass_info["nonzero_spacing_bug"]:
            issues.append("ASS Style has Spacing != 0 (breaks Devanagari/Hindi matra shaping!)")
        if args.require_banner_ass and not ass_info["has_banner_styles"]:
            issues.append("ASS lacks BannerTitle/BannerHook styles (banner text must be libass, never Pillow)")

    audio_audit = clip_audit = None
    if args.audio_report:
        audio_audit, i2, w2 = audit_audio_report(args.audio_report)
        issues += i2
        warns += w2
    else:
        warns.append("No --audio-report supplied: narration Whisper-similarity NOT verified")
    if args.clip_manifest:
        clip_audit, i3, w3 = audit_clip_manifest(args.clip_manifest)
        issues += i3
        warns += w3

    if banner_png:
        warns.append(f"MANUAL STEP: open {banner_png} and verify every Devanagari matra (e.g. 'मिला', 'भविष्य') is intact")

    report = {
        "video": args.video, "resolution": f"{w}x{h}", "fps": fps,
        "video_dur_sec": round(v_dur, 3), "audio_dur_sec": round(a_dur, 3), "av_diff_sec": round(abs(v_dur - a_dur), 3),
        "loudness": loud, "outro_audio": outro, "ass_audit": ass_info,
        "whisper_similarity_report": audio_audit, "clip_audit": clip_audit,
        "storyboard_3x3": sb, "banner_zoom_png": banner_png,
        "issues": issues, "warnings": warns,
        "status": "PASS" if not issues else "ISSUES_FOUND",
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
