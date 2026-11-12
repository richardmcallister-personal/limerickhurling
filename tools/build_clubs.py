#!/usr/bin/env python3
"""Clubs of Limerick's county hurlers, from the infoboxes of their Wikipedia articles (tools/fetch_players.py).
Run after build_archive.py. Writes site/history/clubs.json and tools/data/clubs_report.txt (unmatched and doubtful)."""
import json, re, unicodedata, collections as C
NOW = 2026
A = json.load(open('tools/data/players/articles.json'))
PL = json.load(open('site/history/players.json'))
M = json.load(open('site/history/matches.json'))
def fold(s): return re.sub(r'[^a-z0-9 ]', '', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower())
def slug(s): return re.sub(r' +', '-', fold(s.replace('-', ' ')).strip())
rep = []

def infobox(t):
    m = re.search(r'\{\{\s*infobox [^\n|]*', t, re.I)
    if not m: return None
    i, depth = m.start(), 0
    for j in range(i, len(t) - 1):                      # find the matching }}
        if t[j:j + 2] == '{{': depth += 1
        elif t[j:j + 2] == '}}':
            depth -= 1
            if depth == 0: body = t[i + 2:j]; break
    else: return None
    F, cur = {}, None
    for line in body.split('\n'):
        mm = re.match(r'\s*\|\s*([a-z_]+)\s*=(.*)$', line)
        if mm: cur = mm.group(1); F[cur] = mm.group(2).strip()
        elif cur: F[cur] += '\n' + line.strip()
    return F
def clean(v):
    v = re.sub(r'<ref[^>]*/>|<ref.*?</ref>', '', v or '', flags=re.S)
    v = re.sub(r'\{\{(?:nowrap|small)\|([^{}]*)\}\}', r'\1', v)
    v = re.sub(r'\{\{[^{}]*\}\}', '', v)
    v = re.sub(r'\[\[[^\]|]*\|([^\]]*)\]\]', r'\1', v); v = re.sub(r'\[\[([^\]]*)\]\]', r'\1', v)
    return v
def parts(v):
    v = clean(v)
    return [x.strip(" '\t") for x in re.split(r'<br\s*/?>|\n|\{\{!\}\}', v) if x.strip(" '\t")]
def span(s):
    s = s.replace('—', '–').replace('-', '–')
    m = re.search(r'(\d{4})\s*–\s*(\d{4}|\d\d|present)?', s)
    if m:
        a = int(m.group(1)); b = m.group(2)
        if b is None and not re.search(r'present', s, re.I): return [a, None]       # "2002–": end not given
        b = NOW if b in (None, 'present') else int(b) if len(b) == 4 else int(str(a)[:2] + b)
        return [a, b]
    m = re.search(r'(\d{4})', s)
    return [int(m.group(1)), int(m.group(1))] if m else None
# spellings of the same club; amalgamated or renamed clubs stay separate (Murroe and Murroe-Boher are two clubs)
CLUBFIX = {'Dromin/Athlacca': 'Dromin-Athlacca', 'Hospital–Herbertstown': 'Hospital-Herbertstown', 'Feenagh–Kilmeedy': 'Feenagh-Kilmeedy',
           "St. Mary's": "St Mary's", "St John's GAA (Antrim)": "St John's (Antrim)"}
def clubname(s):
    s = re.sub(r'\[https?://\S+\s+([^\]]+)\]', r'\1', s.strip())          # [http://site Name GAA]
    s = re.sub(r'\s+\d{4}\s*[-–]\s*\d{4}$', '', s)                          # "Murroe-Boher 2005-2019"
    s = re.sub(r'\s*\((?:hurling|Limerick|GAA)\)$', '', s)
    s = re.sub(r'\s+(?:GAA|GAA Club|Hurling Club|HC|CLG)$', '', s)
    return CLUBFIX.get(s.strip(), s.strip())

people = []
LINKS = {}
for title, v in sorted(A.items()):
    F = infobox(v['text'])
    if not F: rep.append(f'no infobox: {title}'); continue
    name = clean(F.get('name', '')).strip() or re.sub(r' \(.*\)$', '', title)
    if not name or name.lower() in ('', 'name'): name = re.sub(r' \(.*\)$', '', title)
    cn, cy = parts(F.get('counties', '')), parts(F.get('ic_years', ''))
    lim = [span(cy[i]) for i, c in enumerate(cn) if 'Limerick' in c and i < len(cy) and span(cy[i])]
    if not lim and cy and len(cn) <= 1: lim = [span(cy[0])] if span(cy[0]) else []
    lim = [x for x in lim if x]; ends = [x[1] for x in lim if x[1]]
    ly = [min(x[0] for x in lim), max(ends) if ends else None] if lim else None
    up = re.search(r'(20\d\d)', F.get('ic_update', ''))
    stale = bool(ly and ly[1] == NOW and re.search(r'present', F.get('ic_years', ''), re.I) and up and int(up.group(1)) < NOW - 1)
    if stale: ly[1] = int(up.group(1))                  # "present" in an infobox last updated years ago
    for tgt, lab in re.findall(r'\[\[([^\]|#]+)(?:\|([^\]]*))?\]\]', F.get('club', '') or F.get('clubs', '')):
        LINKS.setdefault(clubname(lab or tgt), set()).add(tgt.strip())
    cl, cly = parts(F.get('club', '') or F.get('clubs', '')), parts(F.get('cl_years', ''))
    clubs = []
    for i, c in enumerate(cl):
        c = clubname(c)
        if not c or c.lower() in ('none', 'n/a'): continue
        clubs.append([c, span(cly[i]) if i < len(cly) else None])
    # the club he played for while with Limerick: overlapping years, else the first listed
    main = [c for c, y in clubs if y and ly and y[0] <= (ly[1] or NOW) and (y[1] or NOW) >= ly[0]]
    if not main and clubs:
        li = [i for i, c in enumerate(cn) if 'Limerick' in c]
        if li and li[0] > 0: main = [clubs[-1][0]]                       # came to Limerick from another county: latest club
        else: main = [clubs[0][0]]
    pos = clean(F.get('ic_position', '')).split('\n')[0].strip()
    b = re.search(r'(1[89]\d\d|20[0-2]\d)', clean(F.get('birth_date', '')) + ' ' + F.get('birth_date', ''))
    ai = re.match(r'\s*(\d+)', clean(F.get('ic_all_ireland', '')))
    people.append(dict(st=stale, n=name, w=title, cl=main, all=[c for c, y in clubs], y=ly, pos=pos, b=int(b.group(1)) if b else None, ai=int(ai.group(1)) if ai else 0))
    if not main: rep.append(f'no club: {title}')
    if not ly: rep.append(f'no Limerick years: {title}')

# link to archive scorers by folded name, using years to split namesakes
byname = C.defaultdict(list)
for p in PL: byname[fold(p['n'])].append(p)
for p in people:
    cands = byname.get(fold(p['n']), []) or byname.get(fold(re.sub(r' \(.*\)$', '', p['w'])), [])
    if p['y']: cands = [c for c in cands if c['f'] <= (p['y'][1] or NOW) + 1 and c['l'] >= p['y'][0] - 1] or ([] if len(cands) > 1 else cands)
    if len(cands) == 1: p['a'] = cands[0]['s']
    elif len(cands) > 1: rep.append(f"two archive players for {p['w']}: {[c['s'] for c in cands]}")
# archive names printed with initials ("C Carey"): link only when one article fits (same initial and surname,
# Limerick years covering his scoring years) and no other archive name points at that article
taken = {p['a'] for p in people if p.get('a')}
ini = C.defaultdict(list)
for a in PL:
    t = fold(a['n']).split(' ', 1)
    if len(t) == 2 and len(t[0]) <= 2 and a['s'] not in taken:
        c = [p for p in people if not p.get('a') and p['y'] and 'goalkeeper' not in p['pos'].lower() and fold(p['n']).split(' ', 1)[-1] == t[1] and fold(p['n'])[:1] == t[0][:1]
             and p['y'][0] - 1 <= a['f'] and a['l'] <= (p['y'][1] or NOW) + 1]
        if len(c) == 1: ini[c[0]['w']].append(a)
for w, al in ini.items():
    if len(al) == 1:
        p = next(p for p in people if p['w'] == w); p['a'] = al[0]['s']; p['i'] = 1
        rep.append(f"initials: {al[0]['n']} ({al[0]['f']}-{al[0]['l']}) = {w} ({p['y']})")
used = C.Counter(p.get('a') for p in people if p.get('a'))
for p in people:                                       # a stale "present" never ends before his last recorded score
    a = next((x for x in PL if x['s'] == p.get('a')), None)
    if p.pop('st', False) and a and a['l'] > p['y'][1]: p['y'][1] = a['l']
    if p['y'] and p['y'][1] is None:                   # open end: his last recorded score, else only the first season is known
        p['y'][1] = max(a['l'], p['y'][0]) if a else p['y'][0]; rep.append(f"open-ended county years: {p['w']} -> {p['y']}")
for s, n in used.items():
    if n > 1: rep.append(f'archive player {s} matched {n} articles; unlinked'); [p.pop('a') for p in people if p.get('a') == s]

# clubs
CL = {}
for p in people:
    for c in p['cl']:
        k = slug(c); CL.setdefault(k, dict(s=k, n=c, p=[]))['p'].append(p['w'])
APS = {p['s']: p for p in PL}
for c in CL.values():
    ps = [p for p in people if p['w'] in c['p']]
    ys = [p['y'] for p in ps if p['y'] and p['y'][1]]
    c['f'] = min(y[0] for y in ys) if ys else None; c['l'] = max(y[1] for y in ys) if ys else None
    arch = [APS[p['a']] for p in ps if p.get('a')]
    c['g'] = sum(a['g'] for a in arch); c['pt'] = sum(a['p'] for a in arch); c['ai'] = sum(p['ai'] for p in ps)
# colours for the club badges, from each club's Wikipedia infobox (colour boxes, else kit colours, else colour words)
import os
CA = json.load(open('tools/data/players/club_articles.json')) if os.path.exists('tools/data/players/club_articles.json') else {}
NAMED = {'green': '#00843d', 'white': '#ffffff', 'red': '#d0021b', 'blue': '#0047ab', 'navy': '#1f2a5c', 'sky blue': '#6cace4', 'gold': '#f2b705', 'yellow': '#ffd700',
         'amber': '#ffbf00', 'black': '#111111', 'maroon': '#7a1f2b', 'purple': '#5b2a86', 'orange': '#f28c00', 'saffron': '#f4c430', 'claret': '#7f1734', 'grey': '#8a8d91'}
def colours(t):
    m = re.search(r'\|\s*colou?rs\s*=([^\n]*)', t)
    v = m.group(1) if m else ''
    h = re.findall(r'#([0-9A-Fa-f]{6})\b', v)
    if h: return ['#' + x.lower() for x in h][:3]
    kit = [re.search(r'\|\s*' + k + r'\s*=\s*#?([0-9A-Fa-f]{6})\b', t) for k in ('body', 'leftarm', 'shorts', 'socks')]
    kit = ['#' + x.group(1).lower() for x in kit if x]
    if kit: return list(dict.fromkeys(kit))[:3]
    words = re.findall(r'sky blue|' + '|'.join(sorted(NAMED, key=len, reverse=True)), clean(v).lower())
    return [NAMED[w] for w in dict.fromkeys(words)][:3]
def article(n):
    first = fold(re.split(r'[-/ ]', n)[0])
    ts = sorted(LINKS.get(n, []), key=lambda x: (0 if 'Limerick' in x else 1))
    for t in ts:
        t2 = CA.get('->' + t, t)
        if t2 in CA and first in fold(t2): return t2
    return None
for c in CL.values():
    a = article(c['n'])
    if a: c['wa'] = a; c['col'] = colours(CA[a])
    w = [x for x in re.split(r"[\s/-]+", c['n'].replace("'s", "s")) if x and x[0].isalpha() and x.lower() not in ('st', 'na', 'gaa', 'the')]
    c['ab'] = (w[0][:1] + (w[1][:1] if len(w) > 1 else '')).upper() if w else c['n'][:2].upper()
    if c['n'].startswith('Na '): c['ab'] = 'NP' if 'Piarsaigh' in c['n'] else c['ab']
    if c['n'].startswith('St '): c['ab'] = 'S' + c['ab'][:1]
    if not c.get('col'): rep.append(f"no colours: {c['n']} ({a or 'no article'})")
out = dict(players=people, clubs=sorted(CL.values(), key=lambda c: (-len(c['p']), c['n'])))
json.dump(out, open('site/history/clubs.json', 'w'), ensure_ascii=False, separators=(',', ':'))
linked = sum(1 for p in people if p.get('a'))
top = sorted(PL, key=lambda p: -p['t'])[:60]
miss = [p['n'] for p in top if p['s'] not in {q.get('a') for q in people}]
rep = [f'{len(people)} players from Wikipedia, {len(CL)} clubs, {linked} linked to archive scorers',
       f'top 60 archive scorers with no club: {miss}'] + rep
open('tools/data/clubs_report.txt', 'w').write('\n'.join(rep) + '\n')
print('\n'.join(rep[:2]))
