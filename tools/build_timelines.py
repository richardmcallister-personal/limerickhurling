#!/usr/bin/env python3
"""Matchday timelines for finals with a detailed Wikipedia article. Key moments are hand-kept in tools/data/timelines.json;
substitutions and cards come from the article's team sheets ({{suboff|N}}, {{subon|N}}, {{yel|N}}, {{red card||N}},
"X for Y (N mins)"), half-time from its match box, full-time from the archive. Writes site/history/timelines.json."""
import json, re, os, unicodedata
H = json.load(open('tools/data/timelines.json')); H.pop('_', None)
M = {m['id']: m for m in json.load(open('site/history/matches.json'))}
LIM = {p['n'] for p in json.load(open('site/history/clubs.json'))['players']}
def fold(s): return re.sub(r'[^a-z]', '', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower())
LIMF = {fold(n) for n in LIM}
def clean(t):
    t = re.sub(r'<ref[^>]*/>', '', t); t = re.sub(r'<ref[^>]*>.*?</ref>', '', t, flags=re.S)
    t = re.sub(r'\[\[(?:[^\]|]*\|)?([^\]]*)\]\]', r'\1', t)
    return t.replace('&nbsp;', ' ')
def gp(s):
    m = re.search(r'(\d+)\s*[-–]\s*(\d+)', s or '')
    return [int(m.group(1)), int(m.group(2))] if m else None
out, rep = {}, []
for mid, moments in H.items():
    m = M.get(mid); f = f'tools/data/finals/{mid}.json'
    if not m or not os.path.exists(f): rep.append(f'skip {mid}'); continue
    A = json.load(open(f)); raw = A['text']; t = clean(raw)
    dur = 70 if m['y'] >= 1975 else 80 if m['y'] >= 1970 else 60
    ev = []
    # team sheets: a new team starts at a row for jersey 1
    teams, cur = [], None
    for line in t.split('\n'):
        r = re.match(r"\s*\|(?:[^|]*\|\|)?\s*'''(\d+)'''\s*\|\|\s*([^|]+?)\s*(?:\|\||$)(.*)", line)
        if not r: continue
        num, name, rest = int(r.group(1)), r.group(2).strip(), r.group(3)
        if num == 1 and (cur is None or len(cur) > 5): cur = []; teams.append(cur)
        if cur is None: continue
        name = re.sub(r"\s*\((?:c|captain)\)|\{\{[^}]*\}\}|'''|\"", '', name).strip()
        cur.append((num, name, line))
    lim_i = max(range(len(teams)), key=lambda i: sum(fold(n) in LIMF for _, n, _ in teams[i])) if teams else None
    for i, tm in enumerate(teams):
        side = 'L' if i == lim_i else 'O'
        off, on = {}, {}
        for num, name, line in tm:
            for k, mins in re.findall(r'\{\{(suboff|subon)\|(\d+)\}\}', line):
                (off if k == 'suboff' else on).setdefault(int(mins), []).append(name)
            fm = re.search(r'^(.*?)\s+for\s+(.+?)\s*\((\d+)\s*min', name + ' ' + line.split(name, 1)[-1])
            if fm and not re.search(r'\{\{sub', line):
                on.setdefault(int(fm.group(3)), []).append(re.sub(r'\s+for$', '', fm.group(1)).strip()); off.setdefault(int(fm.group(3)), []).append(fm.group(2).strip())
            y = re.search(r'\{\{yel\|(\d+)', line); rd = re.search(r'\{\{(?:red card|sent off)\|[^0-9}]*(\d+)', line)
            if y: ev.append(dict(m=int(y.group(1)) + 0.05, k='card', s=side, who=name, t='Yellow card'))
            if rd: ev.append(dict(m=int(rd.group(1)) + 0.06, k='red', s=side, who=name, t='Red card'))
        for mm in sorted(set(off) | set(on)):
            a, b = off.get(mm, []), on.get(mm, [])
            for j in range(max(len(a), len(b))):
                ev.append(dict(m=mm + 0.01 * j, k='sub', s=side, on=b[j] if j < len(b) else '', off=a[j] if j < len(a) else ''))
    # half-time from the match box; team1 tells which side is Limerick
    ht = None
    for box in re.findall(r'\{\{\s*(?:GAAmatchbox|football box|Footballbox)(.*?)\n\}\}', raw, re.S | re.I):
        F = dict((k.strip().lower(), v.strip()) for k, v in re.findall(r'\|\s*([A-Za-z0-9_ ]+?)\s*=([^\n]*)', box))
        s1, s2 = gp(re.sub(r'\{\{small\|\(\d+\)\}\}', '', F.get('score1', ''))), gp(re.sub(r'\{\{small\|\(\d+\)\}\}', '', F.get('score2', '')))
        limfirst = 'Limerick' in F.get('team1', '')
        want = (m['u'], m['o']) if limfirst else (m['o'], m['u'])
        if (s1, s2) != (list(want[0]), list(want[1])): continue
        sc = re.findall(r'(\d+)\s*[-–]\s*(\d+)', re.sub(r'\{\{small\|\(\d+\)\}\}', '', F.get('ht', '')))
        if len(sc) == 2:
            a, b = [int(x) for x in sc[0]], [int(x) for x in sc[1]]
            ht = a + b if limfirst else b + a
        break
    if ht: ev.append(dict(m=dur / 2 + 0.9, d='HT', k='ht', sc=ht))
    ev.append(dict(m=999, d='FT', k='ft', sc=[m['u'][0], m['u'][1], m['o'][0], m['o'][1]]))
    for e in moments:
        e = dict(e); e.setdefault('d', None); ev.append(e)
    for e in ev:
        if e.get('sc') and 'lead' not in e: e['lead'] = (e['sc'][0] * 3 + e['sc'][1]) - (e['sc'][2] * 3 + e['sc'][3])
    ev.sort(key=lambda e: e['m'])
    ftm = max([x['m'] for x in ev if x['m'] < 999 and not x.get('end')] + [dur])
    for e in ev:
        if e['m'] == 999: e['m'] = ftm + 0.002
        elif e.get('end'): e['m'] = ftm + 0.001
    ev.sort(key=lambda e: e['m'])
    out[mid] = dict(src=A['title'], rev=A['rev'], dur=dur, ev=ev)
    rep.append(f"{mid}: {len(ev)} events ({sum(e['k']=='sub' for e in ev)} subs, {sum(e['k'] in ('card','red') for e in ev)} cards), half-time {ht}")
json.dump(out, open('site/history/timelines.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('\n'.join(rep))
