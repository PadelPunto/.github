# Draws the banner of the organization's start page (profile/images/banner.png): "Padel Punto" with
# the watch and the tablet, from the same pieces as the app banners. Needs the repos next to this
# one: ../Uhr (logo, fonts, court lines, watch picture) and ../Panel (tablet frame and screenshot).
# Usage: python3 tools/banner.py
import importlib.util
import os
import sys
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
BASE = os.path.normpath(os.path.join(ROOT, '..'))
sys.path.insert(0, os.path.join(BASE, 'Uhr', 'tools'))
from logo import logo  # noqa: E402
from readme_art import font, court, BG, MUTED, BALL, WHITE  # noqa: E402

spec = importlib.util.spec_from_file_location('panel_art', os.path.join(BASE, 'Panel', 'tools', 'readme_art.py'))
panel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(panel)


def banner():
    W, H = 1280, 640
    img = Image.new('RGBA', (W, H), BG + (255,))
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([600, -60, 1340, 640], fill=(32, 78, 140, 150))
    gd.ellipse([-260, 420, 420, 900], fill=(212, 245, 60, 40))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    c = court(W, H)
    img.alpha_composite(c, (560, (H - c.height) // 2 + 10))

    d = ImageDraw.Draw(img)
    x = 84
    img.alpha_composite(logo(120), (x - 10, 44))
    d.text((x, 196), 'Padel Punto', font=font(92), fill=WHITE)
    d.text((x, 322), 'No more “wait,', font=font(42, 'Medium'), fill=BALL)
    d.text((x, 374), 'what’s the score?”', font=font(42, 'Medium'), fill=BALL)
    d.text((x, 452), 'Count on your watch, see it big at the court', font=font(23, 'Regular'), fill=MUTED)
    f = font(19, 'Medium')
    rows = (('One tap per point', 'Live on a tablet'),
            ('No phone needed', 'Free & open source'))
    for row, ts in enumerate(rows):
        px, py = x, 504 + row * 44
        for t in ts:
            tw = d.textlength(t, font=f)
            d.rounded_rectangle([px, py, px + tw + 28, py + 34], radius=17, fill=(35, 39, 44), outline=(52, 57, 63), width=2)
            d.text((px + 14, py + 17), t, font=f, fill=WHITE, anchor='lm')
            px += tw + 40

    panel.place(img, panel.tablet('banner', 560), 690, 96, angle=-4)
    w = Image.open(panel.WATCH).convert('RGBA')
    w = w.resize((round(w.width * 0.47), round(w.height * 0.47)), Image.LANCZOS)
    panel.place(img, w, 640, 336, angle=7)
    panel.signal(img, 862, 368)
    return img.convert('RGB')


if __name__ == '__main__':
    out = os.path.join(ROOT, 'profile', 'images', 'banner.png')
    banner().save(out, optimize=True)
    print(out)
