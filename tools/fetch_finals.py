"""Download Wikipedia's articles on the All-Ireland and Munster finals Limerick played in (e.g. "2018 All-Ireland Senior
Hurling Championship final") to tools/data/finals/<match id>.json. Their match summaries and team sheets are the source
for the hand-kept timelines in tools/data/timelines.json."""
import json, time, os, urllib.request, urllib.parse, urllib.error
UA = 'limerickhurling.wiki data builder (fan site)'
OUT = 'tools/data/finals/'
def api(**q):
    q.update(format='json', formatversion='2')
    for n in range(10):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request('https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode(q), headers={'User-Agent': UA}), timeout=90))
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(int(e.headers.get('Retry-After', 20)) + 10 * n); continue
            raise
    raise SystemExit('Wikipedia kept refusing; try again later')
os.makedirs(OUT, exist_ok=True)
M = json.load(open('site/history/matches.json'))
F = [m for m in M if m['cn'] in ('AISHC', 'MSHC') and (m.get('rnd') or '').startswith('Final')]
want = {}
for m in F:
    comp = 'All-Ireland' if m['cn'] == 'AISHC' else 'Munster'
    for t in (f"{m['y']} {comp} Senior Hurling Championship final", f"{m['y']} {comp} Senior Hurling Championship Final"):
        want.setdefault(t, m['id'])
titles = list(want)
got = 0
for i in range(0, len(titles), 20):
    d = api(action='query', prop='revisions', rvprop='content|ids', rvslots='main', titles='|'.join(titles[i:i + 20]), redirects='1')
    back = {r['to']: r['from'] for r in d['query'].get('redirects', [])}
    for p in d['query']['pages']:
        if 'revisions' not in p: continue
        mid = want.get(back.get(p['title'], p['title']))
        if not mid or os.path.exists(OUT + mid + '.json'): continue
        json.dump({'title': p['title'], 'rev': p['revisions'][0]['revid'], 'text': p['revisions'][0]['slots']['main']['content']}, open(OUT + mid + '.json', 'w'), ensure_ascii=False)
        got += 1
    time.sleep(5)
print(len(F), 'finals;', got, 'new articles;', len(os.listdir(OUT)), 'in', OUT)
