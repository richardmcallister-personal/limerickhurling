#!/usr/bin/env python3
"""Ground facts from Wikipedia: coordinates, opened/closed, capacity, record crowd, owner, short lead.
Writes tools/data/ground_facts.json. Candidates per ground are tried in order; the town's article is the last resort (coordinates only, marked town=True)."""
import json, re, time, urllib.parse, urllib.request, urllib.error
UA = 'limerickhurling.wiki data builder (fan site)'
G = json.load(open('site/history/grounds.json'))
TITLES = {'gaelic-grounds': ['Gaelic Grounds'], 'semple-stadium': ['Semple Stadium'], 'pairc-ui-chaoimh': ['Páirc Uí Chaoimh'], 'croke-park': ['Croke Park'],
 'cusack-park-ennis': ['Cusack Park (Ennis)', 'Cusack Park, Ennis'], 'nowlan-park': ['Nowlan Park'], 'fitzgerald-park': ['Fitzgerald Park, Kilmallock', 'Fitzgerald Park (Kilmallock)'],
 'markets-field': ['Markets Field'], 'st-brendans-park': ["St Brendan's Park", "St Brendan's Park, Birr"], 'wexford-park': ['Wexford Park'], 'omoore-park': ["O'Moore Park"],
 'fraher-field': ['Fraher Field'], 'oconnor-park': ["O'Connor Park"], 'walsh-park': ['Walsh Park'], 'pearse-stadium': ['Pearse Stadium'], 'casement-park': ['Casement Park'],
 'parnell-park': ['Parnell Park'], 'cusack-park-mullingar': ['Cusack Park (Mullingar)', 'Cusack Park, Mullingar'], 'fitzgerald-stadium': ['Fitzgerald Stadium'], 'austin-stack-park': ['Austin Stack Park'],
 'duggan-park': ['Duggan Park'], 'okennedy-park': ["O'Kennedy Park"], 'kenny-park': ['Kenny Park'], 'dr-cullen-park': ['Dr Cullen Park', 'Netwatch Cullen Park'], 'corrigan-park': ['Corrigan Park'],
 'pairc-ui-rinn': ['Páirc Uí Rinn'], 'macdonagh-park': ['MacDonagh Park'], 'turners-cross': ['Turners Cross Stadium', "Turners Cross"], 'the-mardyke': ['Mardyke (Cork)', 'The Mardyke'],
 'st-cronans-park': ["St Cronan's Park"], 'kelly-daly-park-rathdowney': [], 'cork-park': [], 'ennis-road-limerick': []}
TOWN = {'Tipperary': 'Tipperary (town)', 'Newport': 'Newport, County Tipperary', 'Charleville Grounds': 'Charleville, County Cork', 'Riverstown Sportsfield': 'Riverstown, County Cork',
 'Ballycastle': 'Ballycastle, County Antrim', 'Lavey': 'Lavey, County Londonderry', 'Ballygalget': 'Ballygalget', 'Bruff': 'Bruff, County Limerick', 'Cushendall': 'Cushendall', 'Tulla': 'Tulla, County Clare',
 'Milltown Malbay': 'Milltown Malbay', 'Waterford Gaelic Field': 'Waterford', 'Waterford Sportsfield': 'Waterford', 'Ennis Grounds': 'Ennis', 'Cork Park': 'Cork (city)', 'Turner\'s Cross': 'Cork (city)', 'The Mardyke': 'Cork (city)', 'Limerick': 'Limerick',
 'Waterford': 'Waterford', 'Cork': 'Cork (city)', 'Dublin': 'Dublin', 'Belfast': 'Belfast', 'Galway': 'Galway', 'Kilkenny': 'Kilkenny', 'Wexford': 'Wexford', 'New Ross': 'New Ross', 'Athenry': 'Athenry',
 'Rathdowney': 'Rathdowney', 'Carlow': 'Carlow', 'Nenagh': 'Nenagh', 'Roscrea': 'Roscrea', 'Clonmel': 'Clonmel', 'Cashel': 'Cashel, County Tipperary', 'Enniscorthy': 'Enniscorthy', 'Gorey': 'Gorey',
 'Ardfert': 'Ardfert', 'Tuam': 'Tuam', 'Tralee': 'Tralee', 'Portlaoise': 'Portlaoise', 'Newcastle West': 'Newcastle West', 'Abbeyfeale': 'Abbeyfeale', 'Kilmallock': 'Kilmallock', 'Ballinasloe': 'Ballinasloe',
 'Ennis': 'Ennis', 'Mullingar': 'Mullingar', 'Birr': 'Birr, County Offaly', 'Dungarvan': 'Dungarvan', 'Tullamore': 'Tullamore', 'Thurles': 'Thurles', 'Killarney': 'Killarney'}
def api(params):
    q = urllib.parse.urlencode(dict(params, format='json', formatversion='2', redirects='1', maxlag='5'))
    for _ in range(8):
        try:
            with urllib.request.urlopen(urllib.request.Request('https://en.wikipedia.org/w/api.php?' + q, headers={'User-Agent': UA}), timeout=60) as r: return json.load(r)
        except urllib.error.HTTPError as e:
            w = int(e.headers.get('Retry-After') or 30); print('http', e.code, 'wait', w, flush=True); time.sleep(min(w, 90))
    raise SystemExit('gave up')
want = {}
for g in G:
    c = list(TITLES.get(g['s'], [])) if g['s'] in TITLES else ([g['n']] if g['t'] else [])
    town = TOWN.get(g['t']) or TOWN.get(g['n']) or (g['t'] or None)
    want[g['s']] = (c, town)
titles = sorted({t for c, town in want.values() for t in c + ([town] if town else [])})
pages = {}
for i in range(0, len(titles), 20):
    b = titles[i:i+20]
    d = api(dict(action='query', titles='|'.join(b), prop='coordinates|extracts|revisions|info', colimit='max', exlimit='max', exintro='1', explaintext='1', exsentences='3', rvprop='content', rvslots='main', inprop='url'))['query']
    norm = {x['from']: x['to'] for x in d.get('normalized', [])}; red = {x['from']: x['to'] for x in d.get('redirects', [])}
    byt = {p['title']: p for p in d['pages'] if not p.get('missing')}
    for t in b:
        n = norm.get(t, t); n = red.get(n, n)
        if n in byt: pages[t] = byt[n]
    print(i, len(pages), flush=True); time.sleep(3)
def box(text):
    m = re.search(r'\{\{\s*Infobox[^|]*', text or '', re.I)
    if not m: return {}
    out = {}; t = text[m.start():m.start()+8000]
    for _ in range(4): t = re.sub(r'\{\{\s*(?:unbulleted list|ubl|plainlist|plain list|flatlist|nowrap|small|formatnum|abbr)\s*\|([^{}]*)\}\}', lambda x: x.group(1).replace('|', '; '), t, flags=re.I)
    for k, v in re.findall(r'^[ \t]*\|[ \t]*([a-z_ ]+?)[ \t]*=[ \t]*(.*)$', t, re.M):
        v = re.sub(r'<ref[^>]*/>|<ref.*?</ref>|<!--.*?-->', '', v); v = re.sub(r'\{\{(?:nowrap|small|start date(?: and age)?)\|([^{}]*)\}\}', lambda x: x.group(1).replace('|', ' '), v, flags=re.I)
        v = re.sub(r'\[\[(?:[^\]|]*\|)?([^\]]*)\]\]', r'\1', v); v = re.sub(r'\{\{[^{}]*\}\}', '', v); v = re.sub(r"<br\s*/?>", '; ', v); v = re.sub(r"<[^>]+>|'''?", '', v).strip(' ;')
        v = re.sub(r'^[;\s*]+', '', v).replace('; ;', ';')
        if v and not v.startswith('|') and v != '}}': out[k.strip()] = v
    return out
facts = {}
for s, (c, town) in want.items():
    f = {}
    for t in c:
        p = pages.get(t)
        if p and p.get('coordinates') and not (51.3 < p['coordinates'][0]['lat'] < 55.5 and -10.8 < p['coordinates'][0]['lon'] < -5.3): continue
        if p and (p.get('coordinates') or 'Infobox' in (p.get('revisions') or [{}])[0].get('slots', {}).get('main', {}).get('content', '')):
            b = box(p['revisions'][0]['slots']['main']['content'])
            f = dict(title=p['title'], url=p['fullurl'], lead=p.get('extract', ''), town=False)
            for k, keys in (('opened', ['opened', 'built']), ('closed', ['closed', 'demolished']), ('capacity', ['capacity']), ('record', ['record_attendance', 'record attendance']),
                            ('owner', ['owner']), ('former', ['former_names', 'former names']), ('renovated', ['renovated', 'expanded'])):
                for k2 in keys:
                    if b.get(k2): f[k] = b[k2][:160]; break
            if p.get('coordinates'): f['lat'], f['lon'] = p['coordinates'][0]['lat'], p['coordinates'][0]['lon']
            break
    if 'lat' not in f and town and pages.get(town) and pages[town].get('coordinates'):
        f.setdefault('town', True); f['lat'], f['lon'] = pages[town]['coordinates'][0]['lat'], pages[town]['coordinates'][0]['lon']; f['townpage'] = pages[town]['title']
    facts[s] = f
json.dump(facts, open('tools/data/ground_facts.json', 'w'), ensure_ascii=False, indent=1)
print('with article', sum(1 for f in facts.values() if f.get('title')), 'with coords', sum(1 for f in facts.values() if 'lat' in f), 'of', len(facts))
