#!/usr/bin/env python3
"""All-Ireland senior hurling finals, every county, 1887 on -> site/history/finals.json (never edit that by hand).
Source: Wikipedia's list of finals (who won, scores, captains) joined to its article on each final (date, ground,
referee, crowd), both downloaded by tools/fetch_allireland.py. Where the two disagree the article is used and the
difference is written to tools/data/allireland/report.txt. Run from the repo root."""
import json, re, collections, datetime

D = 'tools/data/allireland/'
LIST = json.load(open(D + 'list.json'))
ART = json.load(open(D + 'articles.json'))
MON = {m: i + 1 for i, m in enumerate('January February March April May June July August September October November December'.split())}

def plain(s):
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    s = re.sub(r'<ref[^>]*/>', '', s); s = re.sub(r'<ref.*?</ref>', '', s, flags=re.S); s = re.sub(r'<ref.*', '', s, flags=re.S)
    s = re.sub(r'\{\{Ref label[^}]*\}\}', '', s); s = re.sub(r'\{\{c\.\}\}|\{\{circa\}\}', 'c. ', s, flags=re.I)
    s = re.sub(r'\{\{[^{}]*\}\}', '', s)
    s = re.sub(r'\[\[File:[^\]]*\]\]', '', s); s = re.sub(r'\[\[(?:[^\]|]*\|)?([^\]]*)\]\]', r'\1', s)
    s = re.sub(r"'{2,}", '', s); s = re.sub(r'<small>.*?</small>', '', s, flags=re.S); s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', s.replace('&nbsp;', ' ')).strip()

def gp(s):
    m = re.match(r'\s*(\d+)\s*[-–]\s*(\d+)', s or '')
    return [int(m.group(1)), int(m.group(2))] if m else None

def iso(s):
    m = re.search(r'(\d{1,2})\s+([A-Z][a-z]+)\s+(\d{4})', s or '')
    return f'{int(m.group(3)):04d}-{MON[m.group(2)]:02d}-{int(m.group(1)):02d}' if m and m.group(2) in MON else None

def num(s):
    m = re.search(r'\d[\d,.]*\d|\d', s or '')
    return int(re.sub(r'\D', '', m.group(0))) if m else None

# ---- the list: one row per game ----
t = LIST['text']; i = t.find('==List of finals'); tab = t[i:t.find('\n|}', i)]
by, notes_ref, year = collections.defaultdict(list), {}, None
for r in re.split(r'\n\|-[^\n]*', tab)[1:]:
    raw = re.split(r'\n\|', '\n' + r.strip())[1:]
    lab = re.search(r'\{\{Ref label\|(\w)', raw[0] or '')
    cells = [plain(re.sub(r'^\s*(?:rowspan|colspan|style|width)[^|\[]*\|', '', c)) for c in raw]
    if re.match(r'^\d{4}', cells[0]):
        year = int(cells[0][:4])
        if lab: notes_ref[year] = lab.group(1)
        cells = cells[1:]
    elif cells[0].lower().startswith('drawn'): cells = cells[1:]
    if len(cells) < 5: continue                      # 1888: not played
    a, sa, b, sb, ven = cells[:5]
    caps = (cells[5:] + ['', ''])[:2]
    by[year].append(dict(a=a.replace('÷', '').strip(), b=b.replace('÷', '').strip(), sa=gp(sa), sb=gp(sb), lv=ven, cw=caps[0], cl=caps[1]))
FOOT = {}
i = t.find('==Footnotes'); j = t.find('\n==', i + 5)
for seg in re.split(r'<br\s*/?>', t[i:j]):
    m = re.search(r'\{\{Note label\|(\w)[^}]*\}\}\s*(.*)', seg, flags=re.I | re.S)
    if m: FOOT[m.group(1)] = plain(m.group(2))

# ---- the articles ----
def block(text, i):
    depth, j = 0, i
    while j < len(text):
        if text.startswith('{{', j): depth += 1; j += 2; continue
        if text.startswith('}}', j):
            depth -= 1; j += 2
            if depth == 0: break
            continue
        j += 1
    return text[i:j]
def fields(b):
    return {m.group(1): m.group(2).strip() for m in re.finditer(r'\n?\s*\|\s*(\w+)\s*=[ \t]*(.*?)(?=\n[^\n|=]{0,3}\|\s*\w+\s*=|\n?\}\}\Z|\Z)', b, flags=re.S)}
def box(text):
    i = text.find('{{Infobox football match')
    return fields(block(text, i)) if i >= 0 else {}
def boxes(text):
    return [fields(block(text, m.start())) for m in re.finditer(r'\{\{\s*[Ff]ootball ?box', text)]
def parts(s): return [p for p in (plain(x) for x in re.split(r'<br\s*/?>', s or '')) if p]
def spread(L, n):
    """One value per game. Entries are in order of play, or carry a label: (first game), (replay), (2nd replay)."""
    out = [''] * n
    if len(L) == n and not (n > 1 and len(L) == 1): 
        for k, v in enumerate(L): out[k] = v
        if n == 1 or len(L) > 1: return out
    for v in L:
        lo = v.lower()
        k = 0 if 'first game' in lo else 2 if ('2nd replay' in lo or 'second replay' in lo) else n - 1 if 'replay' in lo or 'second game' in lo else (n - 1 if len(L) == 1 else None)
        if k is not None and k < n: out[k] = v
    return out
def unlabel(v): return re.sub(r'\s*\((?:first game|second game|replay|2nd replay|second replay)\)\s*', ' ', v).strip()
def sdate(s, y=None):
    m = re.search(r'\{\{start date\|(\d{4})\|(\d{1,2})\|(\d{1,2})', s or '', flags=re.I)
    if m: return f'{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}'
    m = re.match(r'\s*(\d{4})-(\d{2})-(\d{2})', s or '')
    if m: return m.group(0).strip()
    d = iso(plain(s or ''))
    if not d and y:                                   # "September 4": the season articles leave the year out
        m = re.match(r'\s*([A-Z][a-z]+) (\d{1,2})\b', plain(s or ''))
        if m and m.group(1) in MON: d = f'{y:04d}-{MON[m.group(1)]:02d}-{int(m.group(2)):02d}'
    return d

# Ground names as they were at the time, one spelling each, with where they are. Jones's Road became Croke Park in 1913.
# tn: placed by town only, because the ground itself is gone or was never mapped.
GROUND = {
 'croke park': ('Croke Park', 'Dublin', 53.3608, -6.2511, 0), "jones's road": ("Jones's Road", 'Dublin', 53.3608, -6.2511, 0),
 'clonturk park': ('Clonturk Park', 'Drumcondra, Dublin', 53.3712, -6.2520, 1), 'phoenix park': ('Phoenix Park', 'Dublin', 53.3559, -6.3298, 1),
 "st. patrick's gaa field": ("St Patrick's GAA Field (Pond Field)", 'Inchicore, Dublin', 53.3410, -6.3180, 1),
 'birr sportsfield': ('Birr Sportsfield', 'Birr', 53.0970, -7.9120, 1),
 'fraher field': ('Fraher Field', 'Dungarvan', 52.0967, -7.6236, 0), 'cork athletic grounds': ('Cork Athletic Grounds', 'Cork', 51.8998, -8.4350, 0),
 'tipperary gaa field': ('Tipperary GAA Field', 'Tipperary town', 52.4740, -8.1620, 1), 'tipperary': ('Tipperary', 'Tipperary town', 52.4740, -8.1620, 1),
 'carrick-on-suir': ('Carrick-on-Suir', 'Carrick-on-Suir', 52.3490, -7.4130, 1),
 'nowlan park': ("St James's Park", 'Kilkenny', 52.6564, -7.2394, 0), 'geraldine park': ('Geraldine Park', 'Athy', 52.9920, -6.9870, 1),
 'fitzgerald stadium': ('FitzGerald Stadium', 'Killarney', 52.0664, -9.5081, 0), 'semple stadium': ('Semple Stadium', 'Thurles', 52.6822, -7.8250, 0),
}
def norm(s): return re.sub(r'\s+', ' ', (s or '').lower().replace("jones' road", "jones's road").replace('jones’s road', "jones's road")).strip()
def ground(names, y):
    for nm in names:
        for k in [norm(nm)] + [norm(x) for x in nm.split(',')]:
            if k == 'croke park' and y < 1913: k = "jones's road"
            if k in GROUND: return GROUND[k]
    return None

# A note where the article explains something the tables cannot. Each is from that final's own article.
HAND = {
 (1905, 1): dict(note='Cork won the first game, but Kilkenny objected that the Cork goalkeeper was a British Army reservist, and a replay was ordered.'),
}

rep, out = [], []
for y in sorted(set(by) | {int(k) for k in ART}):
    rows = by.get(y, []); a = ART.get(str(y)); text = a['text'] if a else ''
    b = box(text); fb = boxes(text)
    if not a: rep.append(f'{y}: no article on the final')
    t1, t2 = plain(b.get('team1', '')), plain(b.get('team2', ''))
    s1, s2 = [gp(x) for x in parts(b.get('team1score')) if gp(x)], [gp(x) for x in parts(b.get('team2score')) if gp(x)]
    n = max(len(rows), len(s1), 1)
    if not rows: rep.append(f'{y}: not in the list of finals'); continue
    # order of play: the list puts the deciding game first with "Drawn match" rows under it, except 1905 and 1908 (first game first)
    if len(rows) > 1 and y not in (1905, 1908): rows = rows[1:] + rows[:1]
    if len(rows) < n:
        rep.append(f"{y}: the list has {len(rows)} game(s), the final's article has {n}; earlier games taken from the article")
        rows = [dict(a=t1, b=t2, sa=s1[k], sb=s2[k], lv='', cw='', cl='') for k in range(n - len(rows))] + rows
    # season article: the last games between the two finalists
    sea = []
    try:
        st = json.load(open(f'tools/data/wiki/{y}_All-Ireland_Senior_Hurling_Championship.json'))['text']
        both = [f for f in boxes(st) if {plain(f.get('team1', '')).split(' (')[0].strip(), plain(f.get('team2', '')).split(' (')[0].strip()} == {rows[-1]['a'], rows[-1]['b']}]
        sea = both[-n:] if len(both) >= n else []
    except FileNotFoundError: pass
    fb = fb if len(fb) == n else []
    dates, refs, atts = spread(re.split(r'<br\s*/?>', b.get('date', '')) if b.get('date') else [], n), spread(parts(b.get('referee')), n), spread(parts(b.get('attendance')), n)
    stad, city = plain(b.get('stadium', '')), plain(b.get('city', ''))
    for k, g in enumerate(rows):
        last = k == n - 1
        e = dict(y=y, n=k + 1, of=n)
        F, S = (fb[k] if fb else {}), (sea[k] if sea else {})
        e['d'] = sdate(dates[k]) or sdate(F.get('date')) or sdate(S.get('date'), y)
        # scores: the final's article first, the list second; say so when they differ
        sa, sb = g['sa'], g['sb']
        if len(s1) == n and t1 and t2:
            art = {t1: s1[k], t2: s2[k]}
            if g['a'] in art and g['b'] in art and (art[g['a']], art[g['b']]) != (sa, sb):
                rep.append(f"{y} game {k+1}: list has {g['a']} {sa} {g['b']} {sb}; the final's article has {art[g['a']]} and {art[g['b']]} (article used)")
                e['alt'] = [sa, sb]; sa, sb = art[g['a']], art[g['b']]
        e['a'], e['b'], e['sa'], e['sb'] = g['a'], g['b'], sa, sb
        e['res'] = 'W' if last else 'D' if (sa[0] * 3 + sa[1]) == (sb[0] * 3 + sb[1]) else 'V'   # V: result set aside, replay ordered
        if e['res'] != 'W' and (sb[0] * 3 + sb[1]) > (sa[0] * 3 + sa[1]): e['a'], e['b'], e['sa'], e['sb'] = e['b'], e['a'], sb, sa
        gr = ground([plain(F.get('stadium', '')), stad if (last or not fb) else '', city if (last or not fb) else '', plain(S.get('stadium', '')), g['lv']], y)
        if gr: e['v'], e['t'], e['lat'], e['lon'] = gr[:4]
        else: rep.append(f"{y} game {k+1}: ground not placed ({stad!r}, {city!r}, list {g['lv']!r})")
        if gr and gr[4]: e['tn'] = 1
        if gr and g['lv'] and last and (ground([g['lv']], y) or (0, 0, 0, 0))[2:4] != gr[2:4]: rep.append(f"{y}: list says {g['lv']!r}; the final's article says {stad!r}, {city!r} (article used)")
        r = unlabel(refs[k]) or plain(F.get('referee', '')) or plain(S.get('referee', ''))
        if r: e['ref'] = r
        at = unlabel(atts[k]) or plain(F.get('attendance', '')) or plain(S.get('attendance', ''))
        if num(at): e['att'] = num(at)
        elif at.strip().startswith('0'): e['att'] = 0     # 2020: played behind closed doors
        if at.lower().startswith('c.'): e['atte'] = 1
        if last:
            if g['cw']: e['cw'] = g['cw']
            if g['cl']: e['cl'] = g['cl']
        mm = spread(parts(b.get('man_of_the_match1a')), n)[k]; mm = unlabel(mm)
        if mm: e['motm'] = mm
        h = HAND.get((y, k + 1), {})
        if h.get('note'): e['note'] = h['note']
        if a: e['w'] = a['title']
        out.append(e)
    if y in notes_ref and FOOT.get(notes_ref[y]) and not out[-1].get('note') and not (y == 1905): out[-1]['note'] = FOOT[notes_ref[y]]

# Limerick's finals link to the site's own match pages
M = json.load(open('site/history/matches.json'))
for e in out:
    if 'Limerick' in (e['a'], e['b']):
        opp = e['b'] if e['a'] == 'Limerick' else e['a']
        c = [m for m in M if m['cn'] == 'AISHC' and m['y'] == e['y'] and m['opp'] == opp]
        hit = [m for m in c if m.get('d') and m.get('d') == e.get('d')] or (c if len(c) == 1 and e['of'] == 1 else [])
        if hit: e['m'] = hit[0]['id']
        else: rep.append(f"{e['y']} game {e['n']}: Limerick final not matched to the archive")

# ---- checks ----
titles = collections.Counter(e['a'] for e in out if e['res'] == 'W')
lost = collections.Counter(e['b'] for e in out if e['res'] == 'W')
years = sorted({e['y'] for e in out})
rep.insert(0, f"{len(out)} games in {len(years)} championships, {years[0]}-{years[-1]}; missing years: {[y for y in range(years[0], years[-1] + 1) if y not in years]}")
rep.insert(1, 'Titles: ' + ', '.join(f'{c} {n}' for c, n in titles.most_common()))
rep.insert(2, 'Runners-up: ' + ', '.join(f'{c} {n}' for c, n in lost.most_common()))
rep.insert(3, f"No date: {[ (e['y'], e['n']) for e in out if not e.get('d')]}")
rep.insert(4, f"No crowd: {[ (e['y'], e['n']) for e in out if e.get('att') is None]}")
rep.insert(5, f"No referee: {[ (e['y'], e['n']) for e in out if not e.get('ref')]}")
for e in out:
    if e.get('d') and not (e['y'] <= int(e['d'][:4]) <= e['y'] + 3): rep.append(f"{e['y']} game {e['n']}: date {e['d']} looks wrong")
open(D + 'report.txt', 'w').write('\n'.join(rep) + '\n')
json.dump({'src': {'list': LIST['rev'], 'built': datetime.date.today().isoformat()}, 'gaps': [{'y': 1888, 'note': FOOT.get('f', '')}], 'games': out}, open('site/history/finals.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('\n'.join(rep))
