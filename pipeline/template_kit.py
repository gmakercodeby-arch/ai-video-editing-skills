# -*- coding: utf-8 -*-
"""
template_kit.py - Ready-made Pro Cinema Frame & Banner Templates (Zero Pillow Devanagari!).
Generates crisp, reusable transparent PNG frames for 9:16 Shorts and 16:9 Long-Form Movie Recaps.
Hindi text is ALWAYS rendered via libass (HarfBuzz) on top of these templates so matras never break.
"""
import os
from PIL import Image, ImageDraw


def generate_all_templates(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    paths = {}

    # 1. Dark Gold Cinema (9:16) - Suspense / Sci-Fi / Mystery
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([60, 135, 1020, 295], radius=22, fill=(14, 18, 24, 232), outline=(255, 200, 40, 200), width=3)
    d.rounded_rectangle([74, 153, 84, 277], radius=5, fill=(255, 195, 20, 255))
    # Subtle cinema border around 1080x1120 window (y=340..1460)
    d.line([(0, 340), (1080, 340)], fill=(255, 200, 40, 110), width=2)
    d.line([(0, 1460), (1080, 1460)], fill=(255, 200, 40, 110), width=2)
    p1 = os.path.join(out_dir, "template_dark_gold.png")
    im.save(p1, optimize=True)
    paths["dark_gold"] = p1

    # 2. Crimson Horror / Zombie / Monster (9:16)
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([60, 135, 1020, 295], radius=22, fill=(22, 8, 10, 235), outline=(255, 45, 65, 220), width=3)
    d.rounded_rectangle([74, 153, 84, 277], radius=5, fill=(255, 35, 55, 255))
    d.line([(0, 340), (1080, 340)], fill=(255, 45, 65, 140), width=3)
    d.line([(0, 1460), (1080, 1460)], fill=(255, 45, 65, 140), width=3)
    p2 = os.path.join(out_dir, "template_crimson_horror.png")
    im.save(p2, optimize=True)
    paths["crimson_horror"] = p2

    # 3. Cyan Sci-Fi / Cyberpunk HUD (9:16)
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([60, 135, 1020, 295], radius=18, fill=(8, 20, 28, 232), outline=(0, 229, 255, 210), width=3)
    d.rounded_rectangle([74, 153, 84, 277], radius=4, fill=(0, 229, 255, 255))
    # Corner HUD brackets around cinema box
    c = (0, 229, 255, 180)
    for (x, y, dx, dy) in [(24, 348, 45, 45), (1056, 348, -45, 45), (24, 1452, 45, -45), (1056, 1452, -45, -45)]:
        d.line([(x, y), (x + dx, y)], fill=c, width=4)
        d.line([(x, y), (x, y + dy)], fill=c, width=4)
    p3 = os.path.join(out_dir, "template_cyan_scifi.png")
    im.save(p3, optimize=True)
    paths["cyan_scifi"] = p3

    # 4. Long-Form 16:9 Cinema Matte Bar (1920x1080) - Filmy Nest / ZN Explain Style
    im = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # Matte black bottom scope bar (h=102px) cleanly covers original burned-in movie subtitles
    d.rectangle([0, 978, 1920, 1080], fill=(8, 10, 14, 248))
    d.line([(0, 978), (1920, 978)], fill=(255, 200, 40, 160), width=2)
    # Subtle top-left genre pill frame (text added via libass)
    d.rounded_rectangle([40, 36, 340, 92], radius=12, fill=(10, 14, 20, 190), outline=(255, 200, 40, 150), width=2)
    p4 = os.path.join(out_dir, "template_cinema_16x9.png")
    im.save(p4, optimize=True)
    paths["cinema_16x9"] = p4

    return paths


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "templates")
    res = generate_all_templates(os.path.abspath(out))
    for k, v in res.items():
        print(f"GENERATED {k}: {v}")
