#!/usr/bin/env python3
"""Build site/history/*.json from tools/data/wiki. No network. Run from the repo root.
Writes tools/data/reconcile.txt: every check against the honours list and every gap, for review."""
import json, os, re, sys, unicodedata, collections as C, datetime as DT
sys.path.insert(0, 'tools')
import parse_wiki as P
OUT = 'site/history/'; os.makedirs(OUT, exist_ok=True)
log = []
def fold(s): return re.sub(r'[^a-z0-9 ]', '', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower())
def slug(s): return re.sub(r' +', '-', fold(s.replace('-', ' ')).strip())

raw, skipped = P.run()
raw = [r for r in raw if r['opp']]

def round_name(r):
    n = (r['rnd'] or '').strip()
    if r['comp'] == 'National League' and r.get('div'):
        return r['div'] + ' ' + (round_name(dict(r, div=None)) or '').lower()
    n = re.sub(r'^(Munster|All-Ireland|National League|NHL|Division \d\w?)\s+', '', n, flags=re.I) if not re.fullmatch(r'Division \d\w?', n) else n
    n = re.sub(r'\s*results?$', '', n, flags=re.I).strip()
    if re.search(r'^\d{1,2}\s+\w+\s+\d{4}', n) or n.lower() in ('fixtures','', 'matches', 'division 1', 'division 1a', 'division 1b', 'division 2', 'division 2a'): n = r['rnd'] if re.fullmatch(r'Division.*', r['rnd'] or '') else ''
    # some Wikipedia boxes put the date or throw-in time in the round field: not a round
    if re.search(r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday|january|february|march|april|june|july|august|september|october|november|december)\b|\d(:|\.)\d\d|\d\s*[ap]m\b|utc', n, re.I): n = re.sub(r'.*?(\b(?:Final|Semi-final|Quarter-final|Round \d+)\b.*)?$', lambda m: m.group(1) or '', n, flags=re.I).strip()
    n = re.sub(r'\s*\d{1,2}[:.]\d\d.*$', '', n).replace('Semifinal', 'Semi-final')
    n = n.replace('Semi-Final', 'Semi-final').replace('Quarter-Final', 'Quarter-final').replace(' Replay', ' replay').replace('First Round', 'First round').replace('Senior Hurling Championship', '')
    return n[:1].upper() + n[1:] if n else ''
for r in raw: r['rnd'] = round_name(r)

# Same game appears in more than one article (Munster games sit in both the Munster and All-Ireland pages). Keep the fuller copy.
def richness(r): return (1 if r['gf'] is not None else 0, len(r['sc']) + len(r['osc']), 1 if r['d'] else 0, 1 if r['v'] else 0, 1 if r['ref'] else 0, 1 if r['att'] else 0)
group = C.OrderedDict()
for r in raw:
    sc = (tuple(r['u']), tuple(r['o']))
    k = (r['y'], r['opp'], sc) if r['gf'] is not None else (r['y'], r['opp'], r['d'], r['comp'])
    group.setdefault(k, []).append(r)
rows = []
for k, v in group.items():
    v.sort(key=richness, reverse=True); best = dict(v[0])
    for o in v[1:]:
        for f in ('d', 'v', 'loc', 'att', 'ref', 'tv', 'rnd'):
            if not best.get(f) and o.get(f): best[f] = o[f]
        for f in ('sc', 'osc'):
            if not best[f] and o[f]: best[f] = o[f]
    rows.append(best)
# Empty stubs (a final listed with no score) dropped when a scored game with that year, opponent and date exists.
scored = {(r['y'], r['opp'], r['d']) for r in rows if r['gf'] is not None}
drop = []
keep = []
for r in rows:
    if r['gf'] is None and not r['wo'] and (r['y'], r['opp'], r['d']) in scored: continue
    if r['gf'] is None and not r['wo']: drop.append(r); continue
    if r['gf'] is None and re.search(r'postpon|cancel', r['wo'] or '', re.I): drop.append(r); continue
    keep.append(r)
rows = keep
log.append('Stubs with no score dropped: ' + '; '.join(f"{r['y']} {r['comp']} v {r['opp']} ({r['wo'] or 'blank'})" for r in drop))

# Player names: "A Gillane", "A. Gillane" and "Aaron Gillane" are one person when only one full first name fits that initial and era.
def parts(n):
    n = n.replace('.', ' ').replace('’', "'"); w = n.split()
    return w
names = C.defaultdict(lambda: C.defaultdict(list))
for r in rows:
    for s in r['sc']:
        w = parts(s[0])
        if len(w) < 2: continue
        first = w[0]; sur = fold(' '.join(w[1:]))
        names[(fold(first)[:1], sur)][fold(first)].append(r['y'])
canon = {}
full = {}
for r in rows:
    for s in r['sc']:
        w = parts(s[0])
        if len(w) >= 2 and len(fold(w[0])) > 1: full.setdefault((fold(w[0]), fold(' '.join(w[1:]))), C.Counter())[' '.join(w)] += 1
# Only initials in the source for many players. Full names come from the team article's linked players plus this hand list
# (initial surname, full name, from, to); anything else stays as printed in the source.
HAND = [('G Kirby','Gary Kirby',1985,2002),('R Bennis','Richie Bennis',1964,1980),('E Cregan','Éamonn Cregan',1963,1984),('É Cregan','Éamonn Cregan',1963,1984),
 ("A O'Shaughnessy","Andrew O'Shaughnessy",2001,2014),('N Moran','Niall Moran',2002,2015),('O Moran','Ollie Moran',1996,2010),('J McKenna','Joe McKenna',1972,1986),
 ('M Keane','Mark Keane',1999,2007),('M Galligan','Mike Galligan',1987,2000),('S Fitzgibbon','Shane Fitzgibbon',1984,1994),('M Mackey','Mick Mackey',1930,1948),
 ('J Mackey','John Mackey',1930,1950),('D Stokes','Dick Stokes',1938,1955),('P McMahon','Paddy McMahon',1933,1943),('B Begley','Brian Begley',1999,2009),
 ('D Byrnes','Diarmaid Byrnes',2014,2030),("L O'Donoghue","Liam O'Donoghue",1971,1988),('E Grimes','Éamonn Grimes',1965,1982),('É Grimes','Éamonn Grimes',1965,1982),
 ('P Kelly','Paddy Kelly',1974,1988),('T Kenny','Terence Kenny',1982,1992),('M Houlihan','Mike Houlihan',1989,2003),('J Gillane','John Gillane',2020,2030)]
HAND = [h for h in HAND if h[0] not in ('T Kenny', 'J Gillane')]
team_txt = json.load(open('tools/data/wiki/Limerick_county_hurling_team.json'))['text']
linked = {}
for a, b in re.findall(r'\[\[([^\]|#]+?)(?:\|([^\]]+))?\]\]', team_txt[team_txt.find('==Players'):team_txt.find('==Honours')]):
    nm = (b or a).replace('_', ' ')
    if not re.search(r'GAA|All Stars?|Hurling|Championship|File:|\d', nm) and len(nm.split()) == 2:
        linked.setdefault((fold(nm.split()[0])[:1], fold(nm.split()[1])), set()).add(nm)
def resolve(n, y):
    w = parts(n)
    if len(w) < 2: return n
    for a, f, lo, hi in HAND:
        if ' '.join(w) == a and lo <= y <= hi: return f
    k = (fold(w[0])[:1], fold(' '.join(w[1:])))
    ini = fold(w[0])[:1]; sur = fold(' '.join(w[1:])); fs = names[(ini, sur)]
    longs = {k: v for k, v in fs.items() if len(k) > 1 and min(abs(y - a) for a in v) <= 12}
    def pretty(c):   # prefer the spelling with accents
        return sorted(c, key=lambda x: (-sum(ord(ch) > 127 for ch in x), -c[x]))[0]
    if len(fold(w[0])) > 1:
        c = full[(fold(w[0]), sur)]
        l = linked.get(k)
        if l and len(l) == 1 and fold(next(iter(l))) == fold(' '.join(w)): return next(iter(l))
        return pretty(c)
    if len(longs) == 1:
        c = full[(next(iter(longs)), sur)]; return pretty(c)
    return ' '.join(w)
for r in rows:
    m = C.OrderedDict()
    for n, g, p in r['sc']:
        if n.lower() in ('frees', 'free', 'others', 'unknown'): continue
        c = resolve(n, r['y']); x = m.setdefault(c, [c, 0, 0]); x[1] += g; x[2] += p
    r['sc'] = list(m.values())

def sort_key(r): return (r['d'] or f"{r['y']}-99", r['y'])
rows.sort(key=lambda r: (r['y'], r['d'] or '9999'))
order = {'National League': 0, 'Munster Championship': 1, 'All-Ireland Championship': 2}
def venue_kind(r):
    t = (r['v'] + ' ' + r['loc']).lower()
    if re.search(r'gaelic grounds|limerick|markets field|ennis road|rathkeale|kilmallock|newcastle ?west|bruff|adare|askeaton|croom', t): return 'H'
    if r['comp'] == 'National League' and t.strip(): return 'A'
    return 'N' if t.strip() else ''
seen = C.Counter()
for r in rows:
    base = f"{r['y']}-{slug(r['opp'])}"; seen[base] += 1
    r['id'] = base + (f"-{seen[base]}" if seen[base] > 1 else '')
    r['h'] = venue_kind(r)
    r['cn'] = {'National League': 'NL', 'Munster Championship': 'MSHC', 'All-Ireland Championship': 'AISHC'}[r['comp']]

# Grounds: one name per ground. Thurles Sportsfield became Semple Stadium; Jones's Road became Croke Park; the Cork Athletic Grounds
# was rebuilt as Páirc Uí Chaoimh in 1976. The photo in the assets called athletic-grounds is Armagh, so it is not used.
G_RULES = [(r'gaelic grounds', 'gaelic-grounds', 'Gaelic Grounds', 'Limerick', 'gaelic-grounds-limerick'), (r'semple|thurles', 'semple-stadium', 'Semple Stadium', 'Thurles', 'semple-stadium'),
 (r'croke|jones', 'croke-park', 'Croke Park', 'Dublin', 'croke-park'), (r'chaoimh|cork athletic', 'pairc-ui-chaoimh', 'Páirc Uí Chaoimh', 'Cork', 'pairc-ui-chaoimh'),
 (r'nowlan', 'nowlan-park', 'Nowlan Park', 'Kilkenny', 'nowlan-park'), (r'pearse stadium', 'pearse-stadium', 'Pearse Stadium', 'Galway', 'pearse-stadium'),
 (r'walsh park', 'walsh-park', 'Walsh Park', 'Waterford', 'walsh-park'), (r'wexford park', 'wexford-park', 'Wexford Park', 'Wexford', 'wexford-park'),
 (r'fitzgerald stadium', 'fitzgerald-stadium', 'FitzGerald Stadium', 'Killarney', 'fitzgerald-stadium'), (r'parnell', 'parnell-park', 'Parnell Park', 'Dublin', 'parnell-park'),
 (r"o'connor park", 'oconnor-park', "O'Connor Park", 'Tullamore', 'oconnor-park'), (r'austin stack|tralee sportsfield', 'austin-stack-park', 'Austin Stack Park', 'Tralee', 'austin-stack-park'),
 (r'fitzgerald park', 'fitzgerald-park', 'FitzGerald Park', 'Kilmallock', ''), (r'fraher', 'fraher-field', 'Fraher Field', 'Dungarvan', ''), (r"o'moore", 'omoore-park', "O'Moore Park", 'Portlaoise', ''),
 (r'markets field', 'markets-field', 'Markets Field', 'Limerick', ''), (r"st\.? brendan", 'st-brendans-park', "St Brendan's Park", 'Birr', ''), (r'casement', 'casement-park', 'Casement Park', 'Belfast', ''), (r"chíosóg|chiosog", 'cusack-park-ennis', 'Cusack Park', 'Ennis', '')]
def ground(r):
    t = (r['v'] or '').replace('\u2019', "'")
    if not t: return None
    low = t.lower()
    if 'cusack park' in low:
        if 'mullingar' in low or 'teg' in low or r['opp'] == 'Westmeath': return ('cusack-park-mullingar', 'Cusack Park', 'Mullingar', '')
        return ('cusack-park-ennis', 'Cusack Park', 'Ennis', '')
    for rx, s, n, town, ph in G_RULES:
        if re.search(rx, low): return (s, n, town, ph)
    a, _, b = t.partition(',')
    return (slug(t), a.strip(), b.strip(), '')
for r in rows:
    g = ground(r)
    r['g'] = g[0] if g else None; r['gi'] = g
def slim(r):
    o = {k: r[k] for k in ('id', 'y', 'cn', 'rnd', 'd', 'opp', 'u', 'o', 'gf', 'ga', 'r', 'v', 'g', 'h') if r.get(k) not in (None, '')}
    if r['wo']: o['wo'] = r['wo']
    if r['sc']: o['sc'] = r['sc']
    return o
# Full match detail, one file (small enough), plus a slim list
matches = [slim(r) for r in rows]
json.dump(matches, open(OUT + 'matches.json', 'w'), ensure_ascii=False, separators=(',', ':'))
detail = {}
for r in rows:
    x = {k: r[k] for k in ('osc', 'att', 'ref', 'tv', 'loc') if r.get(k)}
    x['src'] = r['src']
    detail[r['id']] = x
json.dump(detail, open(OUT + 'detail.json', 'w'), ensure_ascii=False, separators=(',', ':'))

def tot(L):
    pl = [m for m in L if m.get('r')]
    return dict(p=len(pl), w=sum(m['r'] == 'W' for m in pl), d=sum(m['r'] == 'D' for m in pl), l=sum(m['r'] == 'L' for m in pl), gf=sum(m['gf'] for m in pl), ga=sum(m['ga'] for m in pl))
# Opponents
opp = C.defaultdict(list)
for m in matches: opp[m['opp']].append(m)
ol = []
for n, L in opp.items():
    t = tot(L); t.update(n=n, s=slug(n), first=L[0]['y'], last=L[-1]['y'],
        ch=tot([m for m in L if m['cn'] != 'NL']), nl=tot([m for m in L if m['cn'] == 'NL']))
    ol.append(t)
ol.sort(key=lambda x: -x['p'])
json.dump(ol, open(OUT + 'opponents.json', 'w'), ensure_ascii=False, separators=(',', ':'))
# Players: scorers only, no appearance data exists in the source
pl = C.defaultdict(lambda: dict(g=0, p=0, games=0, y=C.Counter(), by=C.defaultdict(lambda: [0, 0, 0]), best=None))
for m in matches:
    for n, g, p in m.get('sc', []):
        x = pl[n]; x['g'] += g; x['p'] += p; x['games'] += 1; x['y'][m['y']] += 1
        b = x['by'][m['y']]; b[0] += g; b[1] += p; b[2] += 1
        if not x['best'] or g*3+p > x['best'][0]: x['best'] = [g*3+p, g, p, m['id']]
pll = []
for n, x in pl.items():
    w = n.split()
    pll.append(dict(n=n, s=slug(n), g=x['g'], p=x['p'], t=x['g']*3+x['p'], c=x['games'], f=min(x['y']), l=max(x['y']), by=[[y]+x['by'][y] for y in sorted(x['by'])], b=x['best']))
pll.sort(key=lambda a: -a['t'])
json.dump(pll, open(OUT + 'players.json', 'w'), ensure_ascii=False, separators=(',', ':'))
# Grounds and images
IM = json.load(open('tools/data/image_sources.json'))
gs = {}
for r, m in zip(rows, matches):
    if not r['gi'] or not m.get('r'): continue
    s, n, town, ph = r['gi']; x = gs.setdefault(s, dict(s=s, n=n, t=town, ph=ph, L=[]))
    x['L'].append(m)
gl = []
for x in gs.values():
    L = x.pop('L'); t = tot(L); t.update(x); t.update(first=L[0]['y'], last=L[-1]['y'])
    if x['ph'] in IM['grounds']: t['c'] = IM['grounds'][x['ph']]['c']; t['iw'] = IM['grounds'][x['ph']]['w']; t['ih'] = IM['grounds'][x['ph']]['h']
    gl.append(t)
gl.sort(key=lambda g: -g['p'])
json.dump(gl, open(OUT + 'grounds.json', 'w'), ensure_ascii=False, separators=(',', ':'))
json.dump(dict(shirts=IM['shirts'], cups=IM['cups']), open(OUT + 'media.json', 'w'), ensure_ascii=False, separators=(',', ':'))
# Seasons
se = []
for y in sorted({m['y'] for m in matches}):
    L = [m for m in matches if m['y'] == y]; t = tot(L); t['y'] = y
    t['c'] = {c: tot([m for m in L if m['cn'] == c]) for c in ('NL', 'MSHC', 'AISHC') if any(m['cn'] == c for m in L)}
    se.append(t)
json.dump(se, open(OUT + 'seasons.json', 'w'), separators=(',', ':'))

# Honours from the team article
team = json.load(open('tools/data/wiki/Limerick_county_hurling_team.json'))['text']
hon = team[team.find('==Honours=='):]; hon = hon[:hon.find('==References')]
def years(label, kind):
    m = re.search(re.escape(label) + r".*?'''" + kind + r" \((\d+)\):''' (.*)", hon, re.S)
    if not m: return None
    line = m.group(2).split('\n')[0]; return dict(n=int(m.group(1)), y=[x for x in re.findall(r'\d{4}(?:[–-]\d{2,4})?', P.plain(line))])
H = C.OrderedDict()
for lab, key in (('All-Ireland Senior Hurling Championship', 'aishc'), ('National Hurling League', 'nl'), ('Munster Senior Hurling Championship', 'mshc')):
    H[key] = dict(w=years(lab, 'Winners'), ru=years(lab, 'Runners-up'))
json.dump(H, open(OUT + 'honours.json', 'w'), separators=(',', ':'))

# Managers from the team article's table; the record is what the archive holds for those years
tbl = team[team.find('==Managerial history=='):]; tbl = tbl[:tbl.find('|}')]
mg = []
for row in tbl.split('|-')[1:]:
    c = [x.strip() for x in re.split(r'\|\|?', re.sub(r'\[\[[^\]]*\]\]', lambda m: m.group(0).replace('|', '\x01'), row.replace('\n', ''))) ]
    c = [x.replace('\x01', '|') for x in c if x != '']
    if len(c) < 4 or not re.match(r'\d{4}', c[2]): continue
    who = []
    for x in re.split(r'<br\s*/?>', c[0]):
        nm = P.plain(x); lk = re.search(r'\[\[([^\]|]+)', x)
        who.append(dict(n=nm, s=slug(nm), w=lk.group(1).strip().replace(' ', '_') if lk else ''))
    a = int(c[2]); b = 2026 if c[3] == 'Present' else int(c[3])
    start = a + 1 if mg and str(mg[-1]['t']) == str(a) else a   # a handover year belongs to the outgoing manager
    L = [m for m in matches if start <= m['y'] <= b and m.get('r')]
    mg.append(dict(n=who, f=a, t=c[3], a=start, b=b, ai=P.plain(c[4]) if len(c) > 4 else '', mu=P.plain(c[5]) if len(c) > 5 else '', nl=P.plain(c[6]) if len(c) > 6 else '', rec=tot(L)))
json.dump(mg, open(OUT + 'managers.json', 'w'), ensure_ascii=False, separators=(',', ':'))
seen_m = {}
for m_ in mg:
    for w_ in m_['n']:
        seen_m.setdefault(w_['s'], w_)
        if w_['w'] and not seen_m[w_['s']]['w']: seen_m[w_['s']]['w'] = w_['w']
# Fixtures, hand-kept in tools/data/fixtures.json
fx = json.load(open('tools/data/fixtures.json'))
json.dump(fx, open(OUT + 'fixtures.json', 'w'), ensure_ascii=False, separators=(',', ':'))
ics = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//limerickhurling//EN', 'CALSCALE:GREGORIAN', 'X-WR-CALNAME:Limerick hurling']
for f in fx['games']:
    if not f.get('d') or f.get('approx'): continue   # no calendar entry until there is a real date
    d = f['d'].replace('-', ''); e = (DT.date.fromisoformat(f['d']) + DT.timedelta(days=1)).strftime('%Y%m%d')
    home = f['h'] == 'H'
    ics += ['BEGIN:VEVENT', f"UID:{f['d']}-{slug(f['opp'])}@limerickhurling", f"DTSTAMP:{DT.datetime.now(DT.UTC).strftime('%Y%m%dT%H%M%SZ')}", f"DTSTART;VALUE=DATE:{d}", f"DTEND;VALUE=DATE:{e}",
            f"SUMMARY:{'Limerick v ' + f['opp'] if home else f['opp'] + ' v Limerick'} ({f['comp']}, provisional)", f"LOCATION:{f.get('v','')}", 'STATUS:TENTATIVE', 'END:VEVENT']
ics.append('END:VCALENDAR')
open('site/calendar.ics', 'w').write('\r\n'.join(ics) + '\r\n')
# Search index
idx = [[p['n'], 'Player', '/player/?p=' + p['s'], f"{p['g']}-{p['p']} recorded, {p['f']}-{p['l']}"] for p in pll]
idx += [[o['n'], 'Opponent', '/opponent/?o=' + o['s'], f"{o['p']} recorded games"] for o in ol]
idx += [[w_['n'], 'Manager', '/manager/?m=' + k_, 'Limerick manager'] for k_, w_ in seen_m.items()]
idx += [[g['n'] + (', ' + g['t'] if g['t'] else ''), 'Ground', '/ground/?g=' + g['s'], f"{g['p']} recorded games"] for g in gl]
idx += [[str(s['y']), 'Season', '/season/?y=' + str(s['y']), f"{s['p']} recorded games"] for s in se]
json.dump(idx, open('site/search.json', 'w'), ensure_ascii=False, separators=(',', ':'))
json.dump(dict(built=DT.date.today().isoformat(), revs=None), open(OUT + 'status.json', 'w'))

# Check finals against the honours list
def final_year(y): return y
def is_final(m): return re.fullmatch(r'(Final|Final replay|Final \(refixture\))', m.get('rnd', ''), re.I) is not None
for cn, key, lab in (('AISHC', 'aishc', 'All-Ireland'), ('MSHC', 'mshc', 'Munster')):
    won = sorted({m['y'] for m in matches if m['cn'] == cn and is_final(m) and m.get('r') == 'W'})
    want = sorted(int(x[:4]) for x in (H[key]['w'] or {}).get('y', []))
    log.append(f"{lab} titles: list {len(want)}, finals won in archive {len(won)}. Listed, no final found: {sorted(set(want)-set(won))}. Final won, not listed: {sorted(set(won)-set(want))}")
won = sorted({m['y'] for m in matches if m['cn'] == 'NL' and is_final(m) and m.get('r') == 'W'})
want = sorted(int(x[:4]) for x in H['nl']['w']['y'])
log.append(f"League titles: list {len(want)}, finals won in archive {len(won)}. Listed, no final found: {sorted(set(want)-set(won))}. Final won, not listed: {sorted(set(won)-set(want))}")
log.append(f"Matches: {len(matches)}; with a score {sum(1 for m in matches if m.get('r'))}; with a date {sum(1 for m in matches if m.get('d'))}; with Limerick scorers {sum(1 for m in matches if m.get('sc'))}")
log.append('By competition: ' + str(C.Counter(m['cn'] for m in matches)))
# scorer sum vs score check
bad = []
for m in matches:
    if m.get('sc') and m.get('r'):
        g = sum(s[1] for s in m['sc']); p = sum(s[2] for s in m['sc'])
        if [g, p] != list(m['u']): bad.append(f"{m['id']}: score {m['u'][0]}-{m['u'][1]}, scorers add to {g}-{p}")
log.append(f"Scorers that don't add up to the score: {len(bad)} of {sum(1 for m in matches if m.get('sc'))}")
log += bad
log.append('Parser skipped: ' + str(skipped.most_common(40)))
open('tools/data/reconcile.txt', 'w').write('\n'.join(log) + '\n')
print('\n'.join(log[:8]))
print('top', [(p['n'], p['g'], p['p'], p['t'], p['c']) for p in pll[:14]])
print('seasons', [(s['y'], s['p'], s['w'], s['d'], s['l']) for s in se[-6:]])
print(H)
print(C.Counter(m.get('rnd','') for m in matches).most_common(25))
print(tot(matches))
