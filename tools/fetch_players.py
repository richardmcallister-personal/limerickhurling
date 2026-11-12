"""Download the Wikipedia articles of Limerick inter-county hurlers (Category:Limerick inter-county hurlers)
to tools/data/players/, then the club articles their infoboxes link to (club_articles.json: colours for the badges).
`--clubs` skips the players and fetches only the clubs. build_clubs.py reads both."""
import json, time, urllib.request, urllib.parse, urllib.error, os
UA = 'limerickhurling.wiki data builder (fan site)'
OUT = 'tools/data/players/'
def api(**q):
    q.update(format='json', formatversion='2')
    for _ in range(8):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request('https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode(q), headers={'User-Agent': UA}), timeout=90))
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(int(e.headers.get('Retry-After', 15))); continue
            raise
    raise SystemExit('Wikipedia kept refusing; try again later')
import re, sys
os.makedirs(OUT, exist_ok=True)
def clubs():
    A = json.load(open(OUT + 'articles.json'))
    T = sorted({t.strip() for v in A.values() for t in re.findall(r'\[\[([^\]|#]+)(?:\|[^\]]*)?\]\]', (re.search(r'\|\s*clubs?\s*=(.*)', v['text']) or [None, ''])[1]) if 'GAA' in t or 'Club' in t or 'Hurling' in t})
    out = {}
    for i in range(0, len(T), 40):
        d = api(action='query', prop='revisions', rvprop='content', rvslots='main', titles='|'.join(T[i:i + 40]), redirects='1')
        for r in d['query'].get('redirects', []): out.setdefault('->' + r['from'], r['to'])
        for p in d['query']['pages']:
            if 'revisions' in p: out[p['title']] = p['revisions'][0]['slots']['main']['content'][:6000]
        time.sleep(3)
    json.dump(out, open(OUT + 'club_articles.json', 'w'), ensure_ascii=False)
    print(len([k for k in out if not k.startswith('->')]), 'club articles')
if '--clubs' in sys.argv: clubs(); raise SystemExit
T, c = [], None
while True:
    q = dict(action='query', list='categorymembers', cmtitle='Category:Limerick inter-county hurlers', cmlimit='500', cmtype='page')
    if c: q['cmcontinue'] = c
    d = api(**q); T += [m['title'] for m in d['query']['categorymembers']]
    c = d.get('continue', {}).get('cmcontinue')
    if not c: break
T = [t for t in T if not t.startswith('List of')]
out = {}
for i in range(0, len(T), 40):
    d = api(action='query', prop='revisions', rvprop='content|ids', rvslots='main', titles='|'.join(T[i:i + 40]), redirects='1')
    for p in d['query']['pages']:
        if 'revisions' in p: out[p['title']] = {'rev': p['revisions'][0]['revid'], 'text': p['revisions'][0]['slots']['main']['content']}
    time.sleep(2)
json.dump(out, open(OUT + 'articles.json', 'w'), ensure_ascii=False)
print(len(out), 'player articles')
clubs()
