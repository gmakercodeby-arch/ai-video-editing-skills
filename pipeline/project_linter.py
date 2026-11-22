#!/usr/bin/env python3
"""
Pre-Render Project Linter (Inspired by HyperFrames `check --json`)
Audits video projects BEFORE rendering to catch missing assets, timing overlaps,
frame-inexact cuts, Devanagari ASS Spacing bugs, 80% title-safe zone violations,
audio/video duration drift, and HTML motion contract violations.

Every error includes an actionable `Fix:` line.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


def floor_frame_time(seconds: float, fps: float) -> float:
    """Round down to exact frame boundary: floor(sec * fps) / fps."""
    if fps <= 0:
        return round(seconds, 6)
    return math.floor(seconds * fps + 1e-9) / fps


def probe_media(path: Path) -> dict[str, Any] | None:
    """Return basic ffprobe stream/format info or None if ffprobe fails."""
    if not path.exists():
        return None
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate",
        "-of", "json", str(path),
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=15)
        return json.loads(out)
    except Exception:
        return None


def parse_fps(rate_str: str) -> float:
    if not rate_str:
        return 30.0
    if "/" in rate_str:
        num, den = rate_str.split("/", 1)
        return float(num) / max(float(den), 1.0)
    return float(rate_str)


class ProjectLinter:
    def __init__(self, fps: float = 30.0, max_recap_cut: float = 4.45):
        self.fps = fps
        self.max_recap_cut = max_recap_cut
        self.errors: list[dict[str, str]] = []
        self.warnings: list[dict[str, str]] = []

    def add_error(self, rule: str, target: str, message: str, fix: str) -> None:
        self.errors.append({"rule": rule, "target": target, "message": message, "fix": fix})

    def add_warning(self, rule: str, target: str, message: str, fix: str) -> None:
        self.warnings.append({"rule": rule, "target": target, "message": message, "fix": fix})

    def lint_manifest(self, manifest_path: Path, recap_mode: bool = False) -> None:
        if not manifest_path.exists():
            self.add_error(
                "manifest.missing", str(manifest_path),
                "Clips manifest file not found.",
                f"Create {manifest_path} or pass the correct --manifest path."
            )
            return

        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            self.add_error(
                "manifest.invalid_json", str(manifest_path),
                f"Manifest is not valid JSON: {exc}",
                "Fix JSON syntax errors in the manifest file."
            )
            return

        clips = data if isinstance(data, list) else data.get("clips") or data.get("beats") or []
        if not clips:
            self.add_warning(
                "manifest.empty", str(manifest_path),
                "Manifest contains zero clips/beats.",
                "Populate the manifest with clip entries before rendering."
            )
            return

        base_dir = manifest_path.parent
        prev_end = -1.0
        for idx, clip in enumerate(clips):
            if not isinstance(clip, dict):
                continue
            label = f"clip[{idx}]"
            src = clip.get("file") or clip.get("path") or clip.get("clip") or clip.get("src")
            if src:
                src_path = Path(src)
                if not src_path.is_absolute():
                    src_path = (base_dir / src_path).resolve()
                if not src_path.exists():
                    self.add_error(
                        "media.missing", label,
                        f"Referenced media file does not exist: {src}",
                        f"Verify file path or regenerate clip before rendering: {src_path}"
                    )

            start = clip.get("start")
            end = clip.get("end")
            dur = clip.get("duration")

            if dur is None and start is not None and end is not None:
                dur = float(end) - float(start)

            if dur is not None:
                dur_f = float(dur)
                if dur_f <= 0:
                    self.add_error(
                        "timing.non_positive_duration", label,
                        f"Clip duration is {dur_f:.3f}s (must be > 0).",
                        "Set a positive duration or verify start < end timestamps."
                    )
                elif recap_mode and dur_f > self.max_recap_cut:
                    self.add_warning(
                        "copyright.cut_too_long", label,
                        f"Clip duration {dur_f:.2f}s exceeds copyright-safe cap ({self.max_recap_cut}s).",
                        f"Split {label} into sub-cuts <= {self.max_recap_cut}s (ideal: 1.4s-2.2s for Shorts)."
                    )

            if start is not None:
                start_f = float(start)
                snapped = floor_frame_time(start_f, self.fps)
                if abs(start_f - snapped) > (0.55 / self.fps):
                    self.add_warning(
                        "timing.subframe_drift", label,
                        f"Start time {start_f:.4f}s is not frame-aligned at {self.fps}fps.",
                        f"Floor timestamp to frame boundary: {snapped:.6f}s to prevent 1-frame flash."
                    )
                if prev_end > 0 and start_f < prev_end - (1.0 / self.fps):
                    self.add_warning(
                        "timing.overlap", label,
                        f"Timeline start {start_f:.3f}s overlaps previous clip end {prev_end:.3f}s.",
                        "Adjust start timestamp or place overlapping graphics on separate overlay track."
                    )
                if dur is not None:
                    prev_end = start_f + float(dur)

    def lint_ass(self, ass_path: Path) -> None:
        if not ass_path.exists():
            self.add_error(
                "ass.missing", str(ass_path),
                "ASS subtitle file does not exist.",
                "Generate captions with pipeline/overlay_kit.py before rendering."
            )
            return

        text = ass_path.read_text(encoding="utf-8", errors="replace")
        play_x, play_y = 1080, 1920
        m_x = re.search(r"^PlayResX:\s*(\d+)", text, re.MULTILINE)
        m_y = re.search(r"^PlayResY:\s*(\d+)", text, re.MULTILINE)
        if m_x:
            play_x = int(m_x.group(1))
        if m_y:
            play_y = int(m_y.group(1))

        has_devanagari = bool(re.search(r"[\u0900-\u097F]", text))
        format_cols: list[str] = []

        for line_no, line in enumerate(text.splitlines(), 1):
            if line.startswith("Format:") and "Spacing" in line:
                format_cols = [c.strip() for c in line.split(":", 1)[1].split(",")]
            elif line.startswith("Style:") and format_cols:
                vals = [v.strip() for v in line.split(":", 1)[1].split(",")]
                row = dict(zip(format_cols, vals))
                style_name = row.get("Name", f"line-{line_no}")

                # Critical Devanagari HarfBuzz check: Spacing MUST be 0
                if has_devanagari and "Spacing" in row:
                    try:
                        spacing = float(row["Spacing"])
                        if abs(spacing) > 1e-6:
                            self.add_error(
                                "ass.devanagari_spacing", f"{ass_path.name}:{style_name}",
                                f"Devanagari text detected with Spacing={spacing} (breaks Hindi matras!).",
                                f"Set Spacing=0 in Style '{style_name}' so libass/HarfBuzz shapes matras cleanly."
                            )
                    except ValueError:
                        pass

                # 80% title-safe horizontal margin check (10% left & right)
                min_side_margin = int(play_x * 0.06)
                for side in ("MarginL", "MarginR"):
                    if side in row:
                        try:
                            mval = int(float(row[side]))
                            if mval < min_side_margin:
                                self.add_warning(
                                    "safezone.horizontal_margin", f"{ass_path.name}:{style_name}",
                                    f"{side}={mval}px is tighter than recommended safe margin ({min_side_margin}px for {play_x}px width).",
                                    f"Increase {side} to at least {min_side_margin}px (ideal 10% = {int(play_x*0.10)}px) to stay inside title-safe area."
                                )
                        except ValueError:
                            pass

                # Vertical Shorts UI bottom safe-zone check
                if play_y > play_x and "MarginV" in row and "Alignment" in row:
                    try:
                        align = int(row["Alignment"])
                        margin_v = int(float(row["MarginV"]))
                        if align in (1, 2, 3) and margin_v < int(play_y * 0.16):
                            self.add_warning(
                                "safezone.shorts_bottom_ui", f"{ass_path.name}:{style_name}",
                                f"Bottom-aligned Shorts caption MarginV={margin_v}px may collide with YouTube/Reels UI (bottom ~20%).",
                                f"Raise MarginV to >= {int(play_y * 0.18)}px (e.g. 360-480px on 1080x1920)."
                            )
                    except ValueError:
                        pass

    def lint_av_sync(self, video_path: Path | None, audio_path: Path | None) -> None:
        if not video_path or not audio_path:
            return
        v_info = probe_media(video_path)
        a_info = probe_media(audio_path)
        if not v_info:
            self.add_error("media.probe_failed", str(video_path), "Could not probe video file.", "Ensure video exists and is valid.")
            return
        if not a_info:
            self.add_error("media.probe_failed", str(audio_path), "Could not probe audio file.", "Ensure audio exists and is valid.")
            return
        v_dur = float(v_info.get("format", {}).get("duration", 0) or 0)
        a_dur = float(a_info.get("format", {}).get("duration", 0) or 0)
        drift = abs(v_dur - a_dur)
        if drift > 0.35:
            self.add_warning(
                "sync.duration_drift", f"{video_path.name} vs {audio_path.name}",
                f"Video ({v_dur:.2f}s) and Audio ({a_dur:.2f}s) differ by {drift:.2f}s.",
                "Trim or pad video tail to match master audio duration (or use -shortest with intentional pad)."
            )

    def lint_html_motion(self, html_path: Path) -> None:
        """Validate HyperFrames-compatible HTML motion composition contract."""
        if not html_path.exists():
            self.add_error("html.missing", str(html_path), "HTML composition file not found.", "Generate via pipeline/html_motion.py.")
            return

        html = html_path.read_text(encoding="utf-8", errors="replace")
        target = html_path.name

        if "data-duration" not in html:
            self.add_error(
                "html.missing_root_duration", target,
                "Missing root `data-duration` attribute (video length is undefined).",
                'Add `data-duration="5"` (in seconds) to the root composition element.'
            )

        if "window.__timelines" not in html:
            self.add_warning(
                "html.no_seekable_timeline", target,
                "No `window.__timelines` registration found — animations may not be deterministic frame-by-frame.",
                'Create a paused GSAP timeline (`gsap.timeline({ paused: true })`) and assign `window.__timelines["main"] = tl`.'
            )

        for forbidden, reason in [
            (r"\bDate\.now\s*\(", "Non-deterministic `Date.now()` breaks identical frame-by-frame rendering."),
            (r"\bMath\.random\s*\(", "Unseeded `Math.random()` causes flicker between frames."),
            (r"repeat\s*:\s*-1", "Infinite `repeat: -1` breaks deterministic seekable timelines."),
            (r"src\s*=\s*['\"]/assets/", "Leading `/assets/` breaks relative sub-composition resolution."),
        ]:
            if re.search(forbidden, html):
                self.add_error(
                    "html.contract_violation", target,
                    reason,
                    "Replace with deterministic timeline-driven values or relative `assets/...` paths."
                )

        # Every <audio> must have an id
        for idx, m in enumerate(re.finditer(r"<audio\b[^>]*>", html, re.IGNORECASE)):
            tag = m.group(0)
            if not re.search(r"\bid\s*=", tag, re.IGNORECASE):
                self.add_error(
                    "html.audio_missing_id", f"{target}:audio[{idx}]",
                    "<audio> tag missing `id` attribute (will be excluded from rendered audio mix).",
                    'Add a unique `id="bgm"` or `id="sfx-1"` attribute to every <audio> tag.'
                )

        # Every class="clip" needs data-start and data-duration
        for idx, m in enumerate(re.finditer(r"<[a-zA-Z0-9]+\b[^>]*class\s*=\s*['\"][^'\"]*\bclip\b[^'\"]*['\"][^>]*>", html)):
            tag = m.group(0)
            if "data-start" not in tag or "data-duration" not in tag:
                self.add_error(
                    "html.clip_missing_timing", f"{target}:clip[{idx}]",
                    'Element with class="clip" is missing `data-start` or `data-duration`.',
                    'Add `data-start="0" data-duration="3"` (seconds) to every `.clip` element.'
                )

    def report(self) -> dict[str, Any]:
        return {
            "status": "PASS" if not self.errors else "FAIL",
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-Render Video Project Contract Linter")
    parser.add_argument("--manifest", type=Path, help="Path to clips_manifest.json")
    parser.add_argument("--ass", type=Path, help="Path to captions.ass")
    parser.add_argument("--video", type=Path, help="Path to assembled video track")
    parser.add_argument("--audio", type=Path, help="Path to master audio track")
    parser.add_argument("--html", type=Path, help="Path to HTML motion composition (index.html)")
    parser.add_argument("--fps", type=float, default=30.0, help="Project FPS (default: 30)")
    parser.add_argument("--recap", action="store_true", help="Enforce copyright-safe recap cut limits (<= 4.45s)")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output JSON report")
    args = parser.parse_args()

    linter = ProjectLinter(fps=args.fps)
    if args.manifest:
        linter.lint_manifest(args.manifest, recap_mode=args.recap)
    if args.ass:
        linter.lint_ass(args.ass)
    if args.video or args.audio:
        linter.lint_av_sync(args.video, args.audio)
    if args.html:
        linter.lint_html_motion(args.html)

    rep = linter.report()
    if args.as_json:
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        print(f"=== Project Linter: {rep['status']} ({rep['error_count']} errors, {rep['warning_count']} warnings) ===")
        for e in rep["errors"]:
            print(f"  [ERROR] ({e['rule']}) {e['target']}: {e['message']}")
            print(f"          Fix: {e['fix']}")
        for w in rep["warnings"]:
            print(f"  [WARN]  ({w['rule']}) {w['target']}: {w['message']}")
            print(f"          Fix: {w['fix']}")

    return 0 if rep["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
