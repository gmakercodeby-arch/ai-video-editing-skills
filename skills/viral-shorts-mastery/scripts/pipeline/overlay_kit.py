# -*- coding: utf-8 -*-
"""
overlay_kit.py - Top hook banner + captions, with ZERO Pillow Devanagari.
  * Pillow draws ONLY the dark-glass rounded box + gold stripe (no text, ever: PILLOW_RAQM is False
    on this PC, so Pillow breaks matras: 'मिला' -> 'मलिा').
  * Banner title + Hindi hook are ASS events (BannerTitle / BannerHook styles, Spacing=0) rendered by
    libass + HarfBuzz, the same engine that shapes the captions correctly.
  * Subtitles/ASS are burned LAST in the filter chain (after the PNG overlay).
"""
import re

from PIL import Image, ImageDraw

BANNER_BOX = (60, 135, 1020, 295)


def make_banner_box_png(out_png, box=BANNER_BOX):
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=22, fill=(14, 18, 24, 228), outline=(255, 200, 40, 180), width=3)
    d.rounded_rectangle([x0 + 14, y0 + 18, x0 + 24, y1 - 18], radius=5, fill=(255, 195, 20, 255))
    img.save(out_png)          # NO TEXT drawn by Pillow


def build_chunks(words, impact_words):
    """1-2 word pop chunks over a list of script words -> [{text, idx, impact}] (idx = first word index)."""
    chunks, i = [], 0
    clean = lambda w: re.sub(r"[।,!\?\.\-—]", "", w)
    while i < len(words):
        w1 = words[i]
        c1 = clean(w1)
        if i + 1 < len(words):
            w2 = words[i + 1]
            c2 = clean(w2)
            if re.search(r"[।,!\?\.\—]$", w1) or len(c1) >= 7 or len(c1) + len(c2) > 12:
                chunks.append((w1, i, 1)); i += 1
            else:
                chunks.append((f"{w1} {w2}", i, 2)); i += 2
        else:
            chunks.append((w1, i, 1)); i += 1
    return [{"text": t, "idx": ix, "impact": any(im in t for im in impact_words)} for t, ix, _ in chunks]


def _t(sec):
    h, m, s = int(sec // 3600), int((sec % 3600) // 60), sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def write_ass(captions, out_path, total_dur, banner_title, banner_hook):
    """captions: [{text, start, end, impact}] on the OUTPUT timeline."""
    for k in range(len(captions)):
        if k and captions[k]["start"] < captions[k - 1]["end"] + 0.01:
            captions[k]["start"] = captions[k - 1]["end"] + 0.01
        if captions[k]["end"] <= captions[k]["start"] + 0.12:
            captions[k]["end"] = captions[k]["start"] + 0.12
        if k + 1 < len(captions) and captions[k]["end"] > captions[k + 1]["start"] - 0.01:
            captions[k]["end"] = max(captions[k]["start"] + 0.12, captions[k + 1]["start"] - 0.01)

    head = """[Script Info]
Title: Viral Hindi Short (V2 locked layout)
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Nirmala UI,92,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,7.0,4.5,2,65,65,305,1
Style: BannerTitle,Arial,36,&H00FAF2EB,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: BannerHook,Nirmala UI,50,&H0032D4FF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [head,
             f"Dialogue: 1,{_t(0)},{_t(total_dur)},BannerTitle,,0,0,0,,{{\\an7\\pos(104,152)}}{banner_title}\n",
             f"Dialogue: 1,{_t(0)},{_t(total_dur)},BannerHook,,0,0,0,,{{\\an7\\pos(104,204)}}{banner_hook}\n"]
    pop = r"{\fscx86\fscy86\t(0,65,\fscx106\fscy106)\t(65,130,\fscx100\fscy100)}"
    for c in captions:
        txt = re.sub(r"[,।!—\.\-]+$", "", c["text"].replace("\n", " ").strip())
        txt = txt.replace("—", "").replace(",", "").replace("...", "").replace("!", "").replace("?", "")
        styled = f"{pop}{{\\c&H0000E5FF&}}{txt}" if c["impact"] else f"{pop}{txt}"
        lines.append(f"Dialogue: 0,{_t(c['start'])},{_t(c['end'])},Default,,0,0,0,,{styled}\n")
    with open(out_path, "w", encoding="utf-8-sig") as f:
        f.writelines(lines)
