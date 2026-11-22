#!/usr/bin/env python3
"""
100% FREE Local HTML/CSS/GSAP Motion Graphics Generator & HyperFrames Bridge
Generates deterministic, frame-accurate studio motion cards (Glassmorphism Hook,
Vox-Style Newspaper Highlight, Animated Stat Counter, Kinetic Chapter Title)
using the open-source HyperFrames HTML contract — zero paywall, zero telemetry.

Works in TWO modes:
  1. HyperFrames Local CLI (`--render --engine hyperframes`) — requires Node 22+
  2. Pure FFmpeg/libass Fast Fallback (`--render --engine ffmpeg`) — works on ANY PC
"""

from __future__ import annotations

import argparse
import html as html_lib
import shutil
import subprocess
import sys
from pathlib import Path


TEMPLATES = ("glass_hook", "vox_newspaper", "stat_counter", "kinetic_title")

GSAP_CDN = "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"


def _aspect_dims(aspect: str) -> tuple[int, int]:
    if aspect == "16:9":
        return 1920, 1080
    if aspect == "1:1":
        return 1080, 1080
    return 1080, 1920


def build_html_composition(
    template: str,
    title: str,
    subtitle: str = "",
    badge: str = "EXPLAINED",
    stat_value: str = "98%",
    accent: str = "#00E5FF",
    bg_color: str = "#090D16",
    duration: float = 4.0,
    fps: int = 30,
    aspect: str = "9:16",
) -> str:
    w, h = _aspect_dims(aspect)
    esc_title = html_lib.escape(title)
    esc_sub = html_lib.escape(subtitle)
    esc_badge = html_lib.escape(badge)
    esc_stat = html_lib.escape(stat_value)

    if template == "vox_newspaper":
        body_markup = f"""
  <div id="stage" class="clip" data-start="0" data-duration="{duration}" data-track-kind="graphics">
    <div class="paper-card">
      <div class="masthead" data-var-text="badge">{esc_badge}</div>
      <div class="rule"></div>
      <h1 class="headline" data-var-text="title">
        <span class="highlight-wrap"><span class="highlight-bar"></span><span class="hl-text">{esc_title}</span></span>
      </h1>
      <p class="deck" data-var-text="subtitle">{esc_sub}</p>
    </div>
  </div>"""
        extra_css = f"""
    body {{ background: #141210; }}
    .paper-card {{
      width: 80%; max-width: 900px; background: #F4EFE6; color: #161412;
      padding: 64px 56px; border-radius: 8px;
      box-shadow: 0 30px 90px rgba(0,0,0,0.65);
      border-top: 10px solid {accent};
    }}
    .masthead {{
      font-size: 26px; font-weight: 800; letter-spacing: 0.22em;
      text-transform: uppercase; color: #5C5549; margin-bottom: 18px;
    }}
    .rule {{ height: 3px; background: #161412; margin-bottom: 34px; transform-origin: left; }}
    .headline {{
      font-size: {62 if w < h else 74}px; line-height: 1.18; font-weight: 900; margin: 0 0 26px 0;
    }}
    .highlight-wrap {{ position: relative; display: inline; padding: 4px 10px; }}
    .highlight-bar {{
      position: absolute; inset: 0; background: {accent}; z-index: 0;
      transform-origin: left center; opacity: 0.85; border-radius: 4px;
    }}
    .hl-text {{ position: relative; z-index: 1; }}
    .deck {{ font-size: 32px; line-height: 1.4; color: #3A352E; margin: 0; font-weight: 500; }}"""
        tl_js = f"""
    tl.from(".paper-card", {{ y: 90, opacity: 0, scale: 0.94, duration: 0.65, ease: "power3.out" }}, 0.1)
      .from(".rule", {{ scaleX: 0, duration: 0.45, ease: "power2.out" }}, 0.45)
      .from(".highlight-bar", {{ scaleX: 0, duration: 0.75, ease: "expo.out" }}, 0.75)
      .from(".deck", {{ y: 24, opacity: 0, duration: 0.5, ease: "power2.out" }}, 1.1)
      .to(".paper-card", {{ scale: 1.03, duration: {max(duration - 1.4, 0.5):.2f}, ease: "none" }}, 1.3);"""

    elif template == "stat_counter":
        body_markup = f"""
  <div id="stage" class="clip" data-start="0" data-duration="{duration}" data-track-kind="graphics">
    <div class="stat-card">
      <div class="pill" data-var-text="badge">{esc_badge}</div>
      <div class="big-num" data-var-text="stat_value">{esc_stat}</div>
      <div class="bar-track"><div class="bar-fill"></div></div>
      <h1 class="stat-title" data-var-text="title">{esc_title}</h1>
      <p class="stat-sub" data-var-text="subtitle">{esc_sub}</p>
    </div>
  </div>"""
        extra_css = f"""
    .stat-card {{
      width: 80%; max-width: 920px; text-align: center;
      background: rgba(18, 25, 42, 0.88); border: 2px solid {accent};
      border-radius: 28px; padding: 68px 52px;
      box-shadow: 0 0 80px {accent}33, 0 30px 70px rgba(0,0,0,0.65);
    }}
    .pill {{
      display: inline-block; padding: 10px 26px; border-radius: 999px;
      background: {accent}22; color: {accent}; font-weight: 800;
      letter-spacing: 0.16em; font-size: 24px; margin-bottom: 24px;
    }}
    .big-num {{
      font-size: {140 if w < h else 164}px; font-weight: 900; color: {accent};
      line-height: 1.0; margin-bottom: 26px; text-shadow: 0 0 40px {accent}66;
    }}
    .bar-track {{
      width: 100%; height: 14px; background: rgba(255,255,255,0.12);
      border-radius: 99px; overflow: hidden; margin-bottom: 32px;
    }}
    .bar-fill {{
      width: 100%; height: 100%; background: linear-gradient(90deg, {accent}, #FFFFFF);
      transform-origin: left center;
    }}
    .stat-title {{ font-size: 52px; font-weight: 800; margin: 0 0 14px 0; }}
    .stat-sub {{ font-size: 30px; color: #B8C4D9; margin: 0; }}"""
        tl_js = f"""
    tl.from(".stat-card", {{ y: 70, opacity: 0, scale: 0.92, duration: 0.55, ease: "back.out(1.4)" }}, 0.1)
      .from(".big-num", {{ scale: 0.5, opacity: 0, duration: 0.65, ease: "expo.out" }}, 0.35)
      .from(".bar-fill", {{ scaleX: 0, duration: 1.1, ease: "power3.inOut" }}, 0.5)
      .from(".stat-title, .stat-sub", {{ y: 26, opacity: 0, stagger: 0.15, duration: 0.45 }}, 0.85);"""

    elif template == "kinetic_title":
        body_markup = f"""
  <div id="stage" class="clip" data-start="0" data-duration="{duration}" data-track-kind="graphics">
    <div class="kinetic-wrap">
      <div class="k-badge" data-var-text="badge">{esc_badge}</div>
      <h1 class="k-title" data-var-text="title">{esc_title}</h1>
      <div class="k-line"></div>
      <p class="k-sub" data-var-text="subtitle">{esc_sub}</p>
    </div>
  </div>"""
        extra_css = f"""
    .kinetic-wrap {{ width: 80%; text-align: center; }}
    .k-badge {{
      font-size: 28px; font-weight: 800; letter-spacing: 0.3em;
      color: {accent}; margin-bottom: 24px; text-transform: uppercase;
    }}
    .k-title {{
      font-size: {84 if w < h else 108}px; font-weight: 900; line-height: 1.12;
      margin: 0 0 28px 0; text-shadow: 0 14px 44px rgba(0,0,0,0.75);
    }}
    .k-line {{
      width: 260px; height: 8px; background: {accent}; margin: 0 auto 28px auto;
      border-radius: 99px; box-shadow: 0 0 30px {accent};
    }}
    .k-sub {{ font-size: 36px; color: #D4DEEE; font-weight: 500; margin: 0; }}"""
        tl_js = f"""
    tl.from(".k-badge", {{ y: -30, opacity: 0, duration: 0.45, ease: "power3.out" }}, 0.1)
      .from(".k-title", {{ y: 60, opacity: 0, scale: 0.9, duration: 0.65, ease: "expo.out" }}, 0.25)
      .from(".k-line", {{ scaleX: 0, duration: 0.55, ease: "power3.out" }}, 0.6)
      .from(".k-sub", {{ y: 24, opacity: 0, duration: 0.5, ease: "power2.out" }}, 0.85)
      .to(".kinetic-wrap", {{ scale: 1.04, duration: {max(duration - 1.1, 0.5):.2f}, ease: "none" }}, 1.0);"""

    else:  # glass_hook (default)
        body_markup = f"""
  <div id="stage" class="clip" data-start="0" data-duration="{duration}" data-track-kind="graphics">
    <div class="glow-orb"></div>
    <div class="glass-card">
      <div class="accent-bar"></div>
      <div class="g-badge" data-var-text="badge">{esc_badge}</div>
      <h1 class="g-title" data-var-text="title">{esc_title}</h1>
      <p class="g-sub" data-var-text="subtitle">{esc_sub}</p>
    </div>
  </div>"""
        extra_css = f"""
    .glow-orb {{
      position: absolute; width: 620px; height: 620px; border-radius: 50%;
      background: radial-gradient(circle, {accent}55 0%, transparent 70%);
    }}
    .glass-card {{
      position: relative; width: 80%; max-width: 920px;
      background: rgba(15, 23, 42, 0.78);
      border: 2px solid rgba(255, 255, 255, 0.16);
      border-radius: 30px; padding: 62px 54px;
      box-shadow: 0 30px 90px rgba(0, 0, 0, 0.7);
      overflow: hidden;
    }}
    .accent-bar {{
      position: absolute; top: 0; left: 0; right: 0; height: 10px;
      background: linear-gradient(90deg, {accent}, #FF4B2B); transform-origin: left;
    }}
    .g-badge {{
      display: inline-block; padding: 10px 22px; border-radius: 10px;
      background: {accent}; color: #050914; font-weight: 900;
      font-size: 24px; letter-spacing: 0.12em; margin-bottom: 26px;
    }}
    .g-title {{
      font-size: {68 if w < h else 78}px; line-height: 1.18; font-weight: 900;
      margin: 0 0 22px 0; color: #FFFFFF;
    }}
    .g-sub {{
      font-size: 34px; line-height: 1.4; color: #CBD5E1; margin: 0; font-weight: 500;
    }}"""
        tl_js = f"""
    tl.from(".glow-orb", {{ scale: 0.4, opacity: 0, duration: 0.8, ease: "power2.out" }}, 0.0)
      .from(".glass-card", {{ y: 80, opacity: 0, scale: 0.94, duration: 0.6, ease: "back.out(1.2)" }}, 0.1)
      .from(".accent-bar", {{ scaleX: 0, duration: 0.6, ease: "expo.out" }}, 0.45)
      .from(".g-badge, .g-title, .g-sub", {{ y: 28, opacity: 0, stagger: 0.16, duration: 0.5, ease: "power3.out" }}, 0.5)
      .to(".glass-card", {{ scale: 1.03, duration: {max(duration - 1.3, 0.5):.2f}, ease: "none" }}, 1.2);"""

    return f"""<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8" />
  <title>{esc_title}</title>
  <script src="{GSAP_CDN}"></script>
  <style>
    * {{ box-sizing: border-box; }}
    html, body {{
      margin: 0; padding: 0; width: {w}px; height: {h}px;
      overflow: hidden; background: {bg_color}; color: #FFFFFF;
      font-family: "Noto Sans Devanagari", "Nirmala UI", "Segoe UI", system-ui, sans-serif;
    }}
    #root {{
      position: relative; width: {w}px; height: {h}px;
      display: flex; align-items: center; justify-content: center;
    }}
    #stage {{
      position: relative; width: 100%; height: 100%;
      display: flex; align-items: center; justify-content: center;
    }}
{extra_css}
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-width="{w}" data-height="{h}" data-fps="{fps}" data-duration="{duration}">
{body_markup}
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
{tl_js}
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
"""


def render_ffmpeg_fallback(
    out_mp4: Path,
    title: str,
    subtitle: str,
    badge: str,
    accent: str,
    bg_color: str,
    duration: float,
    fps: int,
    aspect: str,
) -> int:
    """Zero-Node fast FFmpeg + libass (HarfBuzz Devanagari safe) fallback card."""
    w, h = _aspect_dims(aspect)
    ass_path = out_mp4.with_suffix(".ass")
    bg_hex = bg_color.lstrip("#")
    acc_hex = accent.lstrip("#")
    # Convert RGB hex to ASS BGR hex (&H00BBGGRR)
    ass_acc = f"&H00{acc_hex[4:6]}{acc_hex[2:4]}{acc_hex[0:2]}" if len(acc_hex) == 6 else "&H00FFE500"

    ass_content = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Badge,Nirmala UI,34,{ass_acc},&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,0,5,{int(w*0.1)},{int(w*0.1)},40,1
Style: Title,Nirmala UI,{72 if w < h else 84},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,5,{int(w*0.1)},{int(w*0.1)},40,1
Style: Sub,Nirmala UI,40,&H00E2E8F0,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,1,5,{int(w*0.1)},{int(w*0.1)},40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.10,0:00:{duration:05.2f},Badge,,0,0,0,,{{\\an5\\pos({w//2},{int(h*0.36)})\\fad(250,200)}}{badge}
Dialogue: 1,0:00:00.25,0:00:{duration:05.2f},Title,,0,0,0,,{{\\an5\\pos({w//2},{int(h*0.48)})\\fad(300,250)}}{title}
Dialogue: 1,0:00:00.55,0:00:{duration:05.2f},Sub,,0,0,0,,{{\\an5\\pos({w//2},{int(h*0.60)})\\fad(300,250)}}{subtitle}
"""
    ass_path.write_text(ass_content, encoding="utf-8")
    # Escape path for FFmpeg libass filter on Windows
    esc_ass = str(ass_path.resolve()).replace("\\", "/").replace(":", "\\:")

    cmd = [
        "ffmpeg", "-y", "-hide_banner",
        "-f", "lavfi", "-i", f"color=c=0x{bg_hex}:s={w}x{h}:r={fps}:d={duration}",
        "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo",
        "-vf", f"drawbox=x={int(w*0.1)}:y={int(h*0.28)}:w={int(w*0.8)}:h={int(h*0.44)}:color=0x111827@0.85:t=fill,drawbox=x={int(w*0.1)}:y={int(h*0.28)}:w={int(w*0.8)}:h=10:color=0x{acc_hex}:t=fill,ass='{esc_ass}'",
        "-t", str(duration),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k", "-shortest",
        str(out_mp4),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stderr, file=sys.stderr)
    return res.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Free HTML/CSS/GSAP Motion Graphics Generator + HyperFrames Bridge")
    parser.add_argument("--template", choices=TEMPLATES, default="glass_hook", help="Motion template preset")
    parser.add_argument("--title", required=True, help="Main headline (Hindi or English)")
    parser.add_argument("--subtitle", default="", help="Secondary line / hook")
    parser.add_argument("--badge", default="TRUTH REVEALED", help="Top label / masthead")
    parser.add_argument("--stat", default="98%", help="Big stat value (for stat_counter)")
    parser.add_argument("--accent", default="#00E5FF", help="Accent hex color")
    parser.add_argument("--bg", default="#090D16", help="Background hex color")
    parser.add_argument("--duration", type=float, default=4.0, help="Duration in seconds")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second")
    parser.add_argument("--aspect", choices=("9:16", "16:9", "1:1"), default="9:16", help="Aspect ratio")
    parser.add_argument("--out-dir", type=Path, default=Path("motion_card"), help="Output project directory")
    parser.add_argument("--render", action="store_true", help="Also render MP4 immediately")
    parser.add_argument("--engine", choices=("auto", "hyperframes", "ffmpeg"), default="auto", help="Render engine")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    html_file = args.out_dir / "index.html"
    html_text = build_html_composition(
        template=args.template,
        title=args.title,
        subtitle=args.subtitle,
        badge=args.badge,
        stat_value=args.stat,
        accent=args.accent,
        bg_color=args.bg,
        duration=args.duration,
        fps=args.fps,
        aspect=args.aspect,
    )
    html_file.write_text(html_text, encoding="utf-8")
    print(f"[OK] Generated editable HTML/GSAP composition -> {html_file}")

    if not args.render:
        print("     Tip: Open index.html in browser, or run with --render to export MP4.")
        return 0

    out_mp4 = args.out_dir / f"{args.template}.mp4"
    engine = args.engine
    if engine == "auto":
        engine = "hyperframes" if shutil.which("npx") else "ffmpeg"

    if engine == "hyperframes":
        print("[INFO] Rendering via local open-source HyperFrames CLI (free, no login)...")
        cmd = ["npx", "--yes", "hyperframes", "render", "-o", str(out_mp4.name)]
        res = subprocess.run(cmd, cwd=str(args.out_dir))
        if res.returncode == 0 and out_mp4.exists():
            print(f"[OK] HyperFrames MP4 rendered -> {out_mp4}")
            return 0
        print("[WARN] HyperFrames CLI unavailable or failed; falling back to fast FFmpeg/libass engine...")

    rc = render_ffmpeg_fallback(
        out_mp4=out_mp4,
        title=args.title,
        subtitle=args.subtitle,
        badge=args.badge,
        accent=args.accent,
        bg_color=args.bg,
        duration=args.duration,
        fps=args.fps,
        aspect=args.aspect,
    )
    if rc == 0:
        print(f"[OK] FFmpeg/libass MP4 rendered -> {out_mp4}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
