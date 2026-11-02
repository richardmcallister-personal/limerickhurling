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
    box = Image.new('RGBA', (size, size), bg or (0, 0, 0, 0)); x = c.copy(); inner = size - 2 * pad; x.thumbnail((inner, inner), Image.LANCZOS)
    box.alpha_composite(x, ((size - x.width) // 2, (size - x.height) // 2)); return box
fit(88, 0).save('site/assets/crest-88.png')
fit(32, 0).save('site/assets/favicon-32.png')
W = (255, 255, 255, 255)
fit(180, 14, W).convert('RGB').save('site/assets/apple-touch-icon.png')
fit(192, 14, W).save('site/assets/icon-192.png')
fit(512, 40, W).save('site/assets/icon-512.png')
