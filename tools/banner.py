# Draws the pictures of the organization's start page: the banner (profile/images/banner.png,
# "Padel Punto" with the watch and the tablet) and the "how it works" strip (profile/images/flow.png),
# from the same pieces as the app banners. Needs the repos next to this
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

# The tablet app is not released yet: the pictures say "coming soon". Set to False with Padel Punto 2.0.
SOON = True


def pill(img, cx, cy, text, size=19, angle=0):
    """A lime label with dark text, centred on (cx, cy)."""
    f = font(size)
    S = 3
    tw = ImageDraw.Draw(img).textlength(text, font=f)
    w, h = round(tw + size * 1.6), round(size * 1.9)
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * S - 1, h * S - 1], radius=h * S // 2, fill=BALL + (255,))
    d.text((w * S // 2, h * S // 2), text, font=font(size * S), fill=BG, anchor='mm')
    im = im.resize((w, h), Image.LANCZOS)
    if angle:
        im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    sh = Image.new('RGBA', (im.width + 40, im.height + 40), (0, 0, 0, 0))
    sh.paste((0, 0, 0, 150), (20, 26), im.split()[3])
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (cx - sh.width // 2, cy - sh.height // 2))
    img.alpha_composite(im, (cx - im.width // 2, cy - im.height // 2))


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
    rows = (('One tap per point', 'Tablet: coming soon' if SOON else 'Live on a tablet'),
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
    if SOON:
        pill(img, 1120, 112, 'COMING SOON', 22, angle=-4)
    return img.convert('RGB')


def flow():
    """How it works, in one strip: the watch counts, Bluetooth carries the score, the tablet shows it."""
    W, H = 1280, 400
    img = Image.new('RGBA', (W, H), BG + (255,))
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([760, -160, 1400, 420], fill=(32, 78, 140, 120))
    gd.ellipse([-200, 180, 360, 620], fill=(212, 245, 60, 30))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(110)))

    w = Image.open(panel.WATCH).convert('RGBA')
    k = 250 / w.height
    w = w.resize((round(w.width * k), 250), Image.LANCZOS)
    wx, top = 150, 28
    panel.place(img, w, wx, top)
    t = panel.tablet('banner', 420)
    tx = W - 150 - t.width
    panel.place(img, t, tx, top + (250 - t.height) // 2)

    # dots from the watch to the tablet, growing brighter, with an arrow head
    d = ImageDraw.Draw(img)
    y = top + 125
    x0, x1 = wx + w.width + 36, tx - 44
    n = 13
    for i in range(n):
        x = x0 + (x1 - x0) * i / (n - 1)
        a = round(70 + 185 * i / (n - 1))
        r = 5
        d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(round(BG[c] + (BALL[c] - BG[c]) * a / 255) for c in range(3)))
    d.polygon([(x1 + 12, y - 13), (x1 + 34, y), (x1 + 12, y + 13)], fill=BALL)
    mid = (x0 + x1) // 2
    d.text((mid, y - 40), 'Bluetooth', font=font(22), fill=WHITE, anchor='mm')
    d.text((mid, y + 40), 'no phone, no internet', font=font(18, 'Regular'), fill=MUTED, anchor='mm')

    base = top + 250 + 44
    for cx, head, sub in ((wx + w.width // 2, 'The watch counts', 'one tap per point, score called out loud'),
                          (tx + t.width // 2, 'The tablet shows', 'big at the court, for everyone')):
        d.text((cx, base), head, font=font(26), fill=WHITE, anchor='mm')
        d.text((cx, base + 34), sub, font=font(18, 'Regular'), fill=MUTED, anchor='mm')
    if SOON:
        pill(img, tx + t.width - 40, top + (250 - t.height) // 2 + 6, 'COMING SOON', 17, angle=-4)
    return img.convert('RGB')


if __name__ == '__main__':
    for name, draw in (('banner', banner), ('flow', flow)):
        out = os.path.join(ROOT, 'profile', 'images', name + '.png')
        draw().save(out, optimize=True)
        print(out)
