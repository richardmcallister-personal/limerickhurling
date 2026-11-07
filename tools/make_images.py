#!/usr/bin/env python3
"""Shirt, cup and ground images from Richard's gaa_assets folder, plus credits. Usage: make_images.py <folder>. Run from the repo root.
Writes site/assets/{shirts,cups,grounds}/*.webp and tools/data/image_sources.json, which build_archive.py reads."""
import csv, json, os, re, sys
from PIL import Image
from urllib.parse import urlparse
src = sys.argv[1]
SHIRTS = []   # retired 7 Nov 2026: shirts now come from tools/data/shirt_archive.json
CUPS = [('liam-maccarthy-cup', 'aishc', 'Liam MacCarthy Cup', 'All-Ireland'), ('national-hurling-league-cup', 'nl', 'National League cup', 'National League'), ('mick-mackey-cup', 'mshc', 'Mick Mackey Cup', 'Munster'), ('original-liam-maccarthy-cup', '', 'The original Liam MacCarthy Cup', 'All-Ireland, 1921 to 1992')]
GROUNDS = 'gaelic-grounds-limerick semple-stadium pairc-ui-chaoimh croke-park nowlan-park pearse-stadium walsh-park wexford-park fitzgerald-stadium parnell-park oconnor-park austin-stack-park'.split()
rows = {r['file']: r for r in csv.DictReader(open(src + '/sources.csv', encoding='utf-8'))}
def credit(f):
    r = rows[f]; site = urlparse(r['page']).netloc.replace('www.', '')
    m = re.search(r'credits? ([^.;]+)', r['notes'])
    return dict(page=r['page'], site=site, by=m.group(1).strip() if m else '')
def conv(f, out, size, q=80):
    o = Image.open(src + '/' + f).convert('RGBA'); im = Image.new('RGBA', o.size, (255, 255, 255, 255)); im.alpha_composite(o); im = im.convert('RGB'); im.thumbnail((size, size), Image.LANCZOS)
    os.makedirs(os.path.dirname(out), exist_ok=True); im.save(out, quality=q, method=6); return im.size
M = dict(shirts=[], cups=[], grounds={})
for k, y, t, a, b in SHIRTS:
    f = f'limerick-shirts/{k}.png'; conv(f, f'site/assets/shirts/{k}.webp', 640)
    M['shirts'].append(dict(k=k, y=y, t=t, a=a, b=b, c=credit(f)))
for k, h, t, c in CUPS:
    f = f'cups/{k}.png'; w = conv(f, f'site/assets/cups/{k}.webp', 900)
    M['cups'].append(dict(k=k, h=h, t=t, comp=c, w=w[0], ht=w[1], c=credit(f)))
for k in GROUNDS:
    f = f'stadiums/{k}.png'; w = conv(f, f'site/assets/grounds/{k}.webp', 1100)
    M['grounds'][k] = dict(w=w[0], h=w[1], c=credit(f))
A = json.load(open('tools/data/shirt_archive.json'))['items']   # Richard's shirt archive replaces the retailer shots (7 Nov 2026)
M['shirts'] = json.load(open('tools/data/shirts_extra.json'))['shirts'] + [x for x in A if x['sec'] == 'shirts']; M['archive'] = A   # newest first; hand-kept extras (2027 home)
json.dump(M, open('tools/data/image_sources.json', 'w'), ensure_ascii=False, indent=0)
print('ok')
