#!/usr/bin/env python3
"""Pull every Limerick senior match out of the downloaded Wikipedia season articles. No network."""
import json, glob, os, re, html, collections as C
W = os.path.join(os.path.dirname(__file__), 'data', 'wiki')

def boxes(t):
    """Yield (start, inner) for each {{footballbox...}} using brace matching."""
    for m in re.finditer(r'\{\{\s*(football ?box(?:[ _]collapsible)?|GAA ?match(?:box)?(?:[ _]collapsible)?)\s*(?=[\n|])', t, re.I):
        i = m.start(); d = 0; j = i
        while j < len(t)-1:
            two = t[j:j+2]
            if two == '{{': d += 1; j += 2; continue
            if two == '}}':
                d -= 1; j += 2
                if d == 0: break
                continue
            j += 1
        yield i, t[m.end():j-2]

def params(s):
    out = {}; d = 0; cur = ''; parts = []
    s = re.sub(r'<ref[^>]*/>', '', s); s = re.sub(r'<ref.*?</ref>', '', s, flags=re.S); s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    i = 0
    while i < len(s):
        two = s[i:i+2]
        if two in ('{{', '[['): d += 1; cur += two; i += 2; continue
        if two in ('}}', ']]'): d -= 1; cur += two; i += 2; continue
        if s[i] == '|' and d == 0: parts.append(cur); cur = ''; i += 1; continue
        cur += s[i]; i += 1
    parts.append(cur)
    for p in parts:
        if '=' in p:
            k, v = p.split('=', 1); out[k.strip().lower()] = v.strip()
    return out

def plain(t):
    t = html.unescape(t or '')
    t = re.sub(r'\[\[File:[^\]]*\]\]', '', t)
    t = re.sub(r'\{\{small\|[^{}]*\}\}', '', t, flags=re.I)
    for _ in range(3): t = re.sub(r'\{\{[^{}]*\}\}', '', t)
    t = re.sub(r'\[\[(?:[^\]|]*\|)?([^\]]*)\]\]', r'\1', t)
    t = re.sub(r'\[https?://\S+ ?([^\]]*)\]', r'\1', t)
    t = re.sub(r"<br\s*/?>", ' ', t, flags=re.I); t = re.sub(r'<[^>]+>', '', t); t = t.replace("'''", '').replace("''", '')
    return re.sub(r'\s+', ' ', t).strip()

def team(t):
    n = plain(t)
    n = re.sub(r'\s*(GAA|county hurling team)$', '', n).strip()
    return n

MON = {m: i+1 for i, m in enumerate('january february march april may june july august september october november december'.split())}
def date(raw, year):
    t = plain(raw)
    m = re.search(r'(\d{1,2})\s*(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})', t)
    if m and m.group(2).lower() in MON: return '%04d-%02d-%02d' % (int(m.group(3)), MON[m.group(2).lower()], int(m.group(1)))
    m = re.search(r'([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})', t)
    if m and m.group(1).lower() in MON: return '%04d-%02d-%02d' % (int(m.group(3)), MON[m.group(1).lower()], int(m.group(2)))
    m = re.search(r'\{\{\s*start date[^|]*\|(\d{4})\|(\d{1,2})\|(\d{1,2})', raw or '', re.I)
    if m: return '%04d-%02d-%02d' % tuple(map(int, m.groups()))
    return None

SCORE = r'(\d{1,2})\s*[-–—:]\s*(\d{1,3})'
def score(raw):
    s = html.unescape(raw or '')
    s = re.sub(r'\{\{small\|[^{}]*\}\}', '', s, flags=re.I); s = re.sub(r'\{\{\s*(?:nbsp|snd|ndash|en dash)\s*\}\}', ' – ', s, flags=re.I)
    s = re.sub(r"<[^>]+>|'''", '', s); s = re.sub(r'\(\d+\)', '', s)
    m = re.findall(SCORE, s)
    if len(m) >= 2: return (int(m[0][0]), int(m[0][1])), (int(m[1][0]), int(m[1][1]))
    return None

def _items(text, kind, share):
    """One field of a match box -> {name: [goals, points]}."""
    t = re.sub(r'\s*[\u2010-\u2015\u2212]\s*', '-', plain(text)).replace('\xa0', ' ').replace('\u2019', "'")
    t = re.sub(r'(\d{1,2}-\d{1,3})\s*\([^()]*\)', r'\1', t)                      # "Name 0-5 (0-3f)": the bracket is detail
    t = re.sub(r'\(\s*(\d{1,2}-\d{1,3})\s*(each)?[^()]*\)', lambda m: ' %s %s ' % (m.group(1), m.group(2) or ''), t)   # "Name (1-2)", "A, B (0-1 each)"
    t = re.sub(r'\([^()]*\)', ' ', t)
    t = re.sub(r'(\d{1,2}-\d{1,3})(\s+each)?', lambda m: m.group(1) + (m.group(2) or '') + ',', t)   # missing commas after a score
    t = re.sub(r'(?<=[A-Za-z]) (\d{1,2}) each', r' \1 each,', t)
    out = C.OrderedDict(); pend = []
    def put(n, g, pt):
        n = re.sub(r'\s+', ' ', n).strip(" .,:-")
        if len(n) < 3 or re.search(r'\d', n) or not re.search(r'[^\W\d_]{2}', n): return
        x = out.setdefault(n, [0, 0]); x[0] += g; x[1] += pt
    for part in re.split(r'[,;/&]| and ', t):
        part = part.strip(' .\t')
        if not part or re.fullmatch(r'(none|nil|no scorers?|n/a|each)', part, re.I): continue
        m = re.match(r"^(.*?)\s+(\d{1,2})-(\d{1,3})(\s+each)?$", part) or None
        if m:
            g, pt = int(m.group(2)), int(m.group(3))
            if m.group(4) or share:
                for n in pend: put(n, g, pt)
            else:
                for n in pend: put(n, 1 if kind == 'g' else 0, 1 if kind == 'p' else 0)
            pend = []; put(m.group(1), g, pt); continue
        m = re.match(r"^(.*?)\s+(\d{1,2})(\s+each)?$", part)
        if m:
            k = int(m.group(2)); g, pt = (k, 0) if kind == 'g' else (0, k)
            if m.group(3) or share:
                for n in pend: put(n, g, pt)
            else:
                for n in pend: put(n, 1 if kind == 'g' else 0, 1 if kind == 'p' else 0)
            pend = []; put(m.group(1), g, pt); continue
        if re.fullmatch(r"\d.*", part): continue
        pend.append(part)
    for n in pend: put(n, 1 if kind == 'g' else 0, 1 if kind == 'p' else 0)
    return out

def scorers(g, p, want=None):
    """[[name, goals, points]]. Wikipedia uses goals1/points1 separately or 'Name 1-5 (0-3f)' in goals1, and 'A, B 0-2' for shared tallies,
    which can mean each or (rarely) one entry per name, so try both and keep whichever adds up to the known score."""
    best = None
    for share in (True, False):
        r = C.OrderedDict()
        for src, kind in ((g, 'g'), (p, 'p')):
            for n, (a, b) in _items(src, kind, share).items():
                x = r.setdefault(n, [n, 0, 0]); x[1] += a; x[2] += b
        L = list(r.values())
        if want and [sum(x[1] for x in L), sum(x[2] for x in L)] == list(want): return L
        if best is None: best = L
    return best

def heading_at(t, i):
    hs = [(m.start(), len(m.group(1)), plain(m.group(2))) for m in re.finditer(r'^(={2,6})\s*(.*?)\s*\1\s*$', t, re.M)]
    cur = []
    for s, l, h in hs:
        if s >= i: break
        cur = [c for c in cur if c[0] < l] + [(l, h)]
    return [h for _, h in cur]

def comp_of(fname, heads, rnd):
    f = ' / '.join(heads + [rnd or ''])
    if 'National_Hurling' in fname:
        return 'National League'
    if re.search(r'Munster', f, re.I): return 'Munster Championship'
    if re.search(r'Leinster|Ulster|Connacht|Joe McDonagh|Christy Ring|Nicky Rackard|Lory Meagher|Intermediate|Junior|Minor|Under-|Camogie', f, re.I): return None
    if 'Munster_Senior' in fname: return 'Munster Championship'
    return 'All-Ireland Championship'

HOME = re.compile(r'gaelic grounds|limerick|markets field|ennis road|rathkeale|kilmallock|newcastle ?west', re.I)
def run():
    rows = []; skipped = C.Counter()
    for f in sorted(glob.glob(os.path.join(W, '*.json'))):
        b = os.path.basename(f); m = re.match(r'(\d{4})', b)
        if not m: continue
        yr = int(m.group(1)); t = json.load(open(f))['text']
        for i, inner in boxes(t):
            p = params(inner)
            a, c = team(p.get('team1', '')), team(p.get('team2', ''))
            if 'Limerick' not in (a, c): continue
            s = score(p.get('score') or ' – '.join(x for x in (p.get('score1',''), p.get('score2','')) if x))
            heads = heading_at(t, i); rnd = plain(p.get('round', '')) or None
            comp = comp_of(b, heads, rnd)
            if comp is None: skipped['other grade'] += 1; continue
            raw_date = p.get('date', '')
            d = date(raw_date, yr)
            if not rnd:
                r = re.sub(r'^.*?<br\s*/?>', '', raw_date) if re.search(r'<br', raw_date, re.I) else (raw_date if not d else '')
                rnd = plain(r) or (heads[-1] if heads else None)
            us = a == 'Limerick'; opp = c if us else a
            if s:
                ug, up = s[0] if us else s[1]; og, op = s[1] if us else s[0]
                gf = ug*3+up; ga = og*3+op
                res = 'W' if gf > ga else 'L' if gf < ga else 'D'
            else:
                ug = up = og = op = gf = ga = None; res = None
                if not re.search(r'w/o|walkover|scr', plain(p.get('score','')), re.I) and (p.get('score') or p.get('score1')): skipped['no score: '+b[:4]+' '+plain(p.get('score',''))[:12]] += 1
            sc = scorers(p.get('goals1' if us else 'goals2', ''), p.get('points1' if us else 'points2', ''), [ug, up] if s else None)
            oc = scorers(p.get('goals2' if us else 'goals1', ''), p.get('points2' if us else 'points1', ''), [og, op] if s else None)
            venue = plain(p.get('stadium', '') or p.get('venue', '')); loc = plain(p.get('location', ''))
            dv = re.search(r'Division (\dB?|2A|2B|3A?)\b', ' / '.join(heads) + ' ' + (rnd or ''))
            div = 'Division ' + dv.group(1) if dv and dv.group(1) not in ('1',) else None
            rows.append(dict(div=div, tv=plain(p.get('tv','')), y=yr, comp=comp, rnd=rnd, d=d, opp=opp, u=[ug, up], o=[og, op], gf=gf, ga=ga, r=res, sc=sc, osc=oc, v=venue, loc=loc,
                             att=plain(p.get('attendance', '')), ref=plain(p.get('referee', '')), wo=plain(p.get('score','')) if not s else None, src=b[:-5].replace('_', ' ')))
    return rows, skipped
if __name__ == '__main__':
    rows, sk = run()
    print(len(rows)); print(sk.most_common(30))
    json.dump(rows, open('/tmp/claude-0/-home-claude/10cfb72c-5155-5226-ad0c-778a6c0c2667/scratchpad/raw.json', 'w'))
    c = C.Counter((r['comp']) for r in rows); print(c)
    by = C.Counter(r['y']//10*10 for r in rows); print(sorted(by.items()))
    print('no date', sum(1 for r in rows if not r['d']), 'no score', sum(1 for r in rows if r['gf'] is None), 'with scorers', sum(1 for r in rows if r['sc']))
    for r in rows[-6:]: print({k: r[k] for k in ('y','comp','rnd','d','opp','u','o','r','v','loc')}, r['sc'][:4])
    for r in [x for x in rows if x['y'] in (1897,1940,1973)][:8]: print({k: r[k] for k in ('y','comp','rnd','d','opp','u','o','r','v')}, r['sc'][:3])
