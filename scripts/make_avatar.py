#!/usr/bin/env python3
# make_avatar.py (v0.5.0 draft) - draws one bot badge avatar (512x512 round PNG).
# Why: every bot gets its avatar at creation, so the whole team looks consistent with no hand work (MANIFEST step 7).
# Nothing company-specific lives here: the logo file and colors come from the COMPANY_MARKS line in the LOCAL START HERE.
# Usage: python3 make_avatar.py [--logo <logo.png>] --bg R,G,B --ring R,G,B --badge TEXT [--leader] --out <file.png>
#   No --logo: a plain disc in the company colors (NAMING.txt N8; flag it to the Controller).
#   --badge: 1-4 characters from bootstrap/NAMING.txt (N6). --leader adds the gold star in a dark disc.
# Needs Pillow (pip install pillow). Prints the output path on success.
import argparse, math, sys
from PIL import Image, ImageDraw, ImageFont
S = 512  # final size in pixels

def rgb(text):
    parts = [int(p) for p in text.split(",")]
    if len(parts) != 3 or not all(0 <= p <= 255 for p in parts):
        raise argparse.ArgumentTypeError("color must be R,G,B with each 0-255")
    return tuple(parts)

def font(size):
    # Why a fallback chain: bots run on different machines; any bold sans works.
    for path in ("DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "arialbd.ttf", "C:/Windows/Fonts/arialbd.ttf", "/Library/Fonts/Arial Bold.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()

def star(cx, cy, outer, inner):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = outer if i % 2 == 0 else inner
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

def draw(logo_path, bg, ring, badge, leader, out):
    if not 1 <= len(badge) <= 4:
        sys.exit("badge must be 1-4 characters (NAMING.txt N6)")
    im = Image.new("RGBA", (S, S), ring + (255,))
    d = ImageDraw.Draw(im)
    d.ellipse([22, 22, S - 22, S - 22], fill=bg + (255,))           # ring = company color, disc = logo background
    # Why optional: a new company may have no logo yet (N8); the disc and badge still identify the bot.
    logo = Image.open(logo_path).convert("RGBA") if logo_path else Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    bbox = logo.getbbox()
    if bbox:
        logo = logo.crop(bbox)                                        # trim empty margins so every logo sits the same
    if leader:
        logo.thumbnail((230, 175)); im.paste(logo, (70, 120), logo)  # shifted left to make room for the star
        rin, rd = S / 2 - 22, 78
        cx = S / 2 + (rin - rd) * math.cos(math.radians(-45)); cy = S / 2 + (rin - rd) * math.sin(math.radians(-45))
        d.ellipse([cx - rd, cy - rd, cx + rd, cy + rd], fill=(20, 20, 28, 255), outline=(255, 200, 40, 255), width=5)
        d.polygon(star(cx, cy, rd * 0.78, rd * 0.32), fill=(255, 196, 30, 255))
    else:
        logo.thumbnail((300, 230)); im.paste(logo, ((S - logo.width) // 2, 70), logo)
    bw, bh = 240, 96
    x0, y0 = (S - bw) // 2, S - bh - 58
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=48, fill=ring + (255,), outline=(255, 255, 255, 255), width=6)
    size = 70
    while True:                                                      # shrink until the badge text fits the pill
        f = font(size)
        if d.textlength(badge, font=f) < bw - 40 or size < 30:
            break
        size -= 4
    d.text((x0 + bw / 2, y0 + bh / 2), badge, font=f, fill=(255, 255, 255, 255), anchor="mm")
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, S - 1, S - 1], fill=255)
    im.putalpha(mask)
    im.save(out)
    print(out)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Draw one bot badge avatar.")
    p.add_argument("--logo", default=None); p.add_argument("--bg", type=rgb, required=True)
    p.add_argument("--ring", type=rgb, required=True); p.add_argument("--badge", required=True)
    p.add_argument("--leader", action="store_true"); p.add_argument("--out", required=True)
    a = p.parse_args()
    draw(a.logo, a.bg, a.ring, a.badge.upper(), a.leader, a.out)
