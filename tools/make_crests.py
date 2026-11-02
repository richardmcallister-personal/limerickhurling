#!/usr/bin/env python3
"""Crests and icons from Richard's gaa_assets folder. Usage: make_crests.py <folder>. Writes site/assets/crests/*.webp and the icon sizes."""
import glob, os, sys
from PIL import Image
src = sys.argv[1]; out = 'site/assets/crests/'; os.makedirs(out, exist_ok=True)
files = glob.glob(src + '/county-crests/*.png') + [src + '/overseas-crests/london.png']
for f in files:
    if not os.path.exists(f): continue
    im = Image.open(f).convert('RGBA'); bb = im.getbbox()
    if bb: im = im.crop(bb)
    im.thumbnail((96, 96), Image.LANCZOS)
    im.save(out + os.path.basename(f)[:-4] + '.webp', quality=88, method=6)
c = Image.open(src + '/county-crests/limerick.png').convert('RGBA'); c = c.crop(c.getbbox())
def fit(size, pad, bg=None):
    box = Image.new('RGBA', (size, size), bg or (0, 0, 0, 0)); inner = size - 2 * pad; k = inner / max(c.size); x = c.resize((round(c.width * k), round(c.height * k)), Image.LANCZOS)
    box.alpha_composite(x, ((size - x.width) // 2, (size - x.height) // 2)); return box
fit(132, 0).save('site/assets/crest-88.png')
fit(32, 0).save('site/assets/favicon-32.png')
fit(48, 0).save('site/favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
G = (0, 105, 62, 255)   # Limerick green, the site's band colour
def outlined(size, pad, width):   # crest filling the tile, with a thin white edge so it lifts off the green
    x = fit(size, pad); a = x.getchannel('A'); from PIL import ImageFilter
    edge = a.filter(ImageFilter.MaxFilter(2 * width + 1)); box = Image.new('RGBA', (size, size), G)
    box.paste((255, 255, 255, 255), (0, 0), edge); box.alpha_composite(x); return box
outlined(180, 10, 2).convert('RGB').save('site/assets/apple-touch-icon.png')
outlined(192, 11, 2).save('site/assets/icon-192.png')
outlined(512, 28, 5).save('site/assets/icon-512.png')
outlined(512, 70, 5).save('site/assets/icon-512-maskable.png')
og = Image.new('RGBA', (1200, 630), (0, 105, 62, 255)); s = fit(460, 0); og.alpha_composite(s, (370, 85)); og.convert('RGB').save('site/assets/og.png', optimize=True)
