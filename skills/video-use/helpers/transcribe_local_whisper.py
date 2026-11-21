"""Transcribe a video with local faster-whisper without needing ElevenLabs API key.

Outputs JSON matching the schema expected by pack_transcripts.py and render.py:
{
    "words": [
        {"text": "Hello", "start": 0.12, "end": 0.45, "type": "word"},
        ...
    ]
}
"""

import argparse
import json
import os
import sys
from pathlib import Path
from faster_whisper import WhisperModel

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video_path", type=str, help="Path to video/audio")
    parser.add_argument("--edit-dir", type=str, default="", help="Edit dir containing transcripts/")
    parser.add_argument("--model", type=str, default="base", help="Model size: tiny, base, small, medium, large-v3")
    args = parser.parse_args()

    vpath = Path(args.video_path).resolve()
    if not vpath.exists():
        sys.exit(f"File not found: {vpath}")

    if args.edit_dir:
        out_dir = Path(args.edit_dir) / "transcripts"
    else:
        out_dir = vpath.parent / "edit" / "transcripts"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_file = out_dir / f"{vpath.stem}.json"
    if out_file.exists():
        print(f"Transcript already cached at: {out_file}")
        return

    print(f"Loading faster-whisper model ({args.model})...")
    # Using cpu with int8 quantization for ultra-fast, robust transcription
    model = WhisperModel(args.model, device="cpu", compute_type="int8")

    print(f"Transcribing {vpath} with word-level timestamps...")
    segments, info = model.transcribe(str(vpath), word_timestamps=True)

    words_list = []
    full_text = []

    for seg in segments:
        full_text.append(seg.text)
        if seg.words:
            for w in seg.words:
                words_list.append({
                    "text": w.word.strip(),
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                    "type": "word"
                })

    data = {
        "text": " ".join(full_text),
        "language": info.language,
        "duration": info.duration,
        "words": words_list
    }

    out_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Saved {len(words_list)} words transcript to: {out_file}")

if __name__ == "__main__":
    main()
