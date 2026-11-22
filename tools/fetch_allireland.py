"""Download Wikipedia's list of All-Ireland senior hurling finals and its article on each final (every county, 1887 on)
to tools/data/allireland/list.json and articles.json. tools/build_finals.py turns them into site/history/finals.json.
Run once a year after the final. Wikipedia rate limits: the script waits and retries."""
import json, time, os, datetime, urllib.request, urllib.parse, urllib.error
UA = 'limerickhurling.wiki data builder (fan site)'
OUT = 'tools/data/allireland/'
def api(**q):
    q.update(format='json', formatversion='2')
    for n in range(10):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request('https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode(q), headers={'User-Agent': UA}), timeout=90))
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(min(int(e.headers.get('Retry-After', 20)), 60) + 5 * n); continue
            raise
    raise SystemExit('Wikipedia kept refusing; try again later')
os.makedirs(OUT, exist_ok=True)
d = api(action='query', prop='revisions', rvprop='content|ids', rvslots='main', titles='List of All-Ireland Senior Hurling Championship finals')
p = d['query']['pages'][0]
json.dump({'title': p['title'], 'rev': p['revisions'][0]['revid'], 'text': p['revisions'][0]['slots']['main']['content']}, open(OUT + 'list.json', 'w'), ensure_ascii=False)
titles = [f'{y} All-Ireland Senior Hurling Championship final' for y in range(1887, datetime.date.today().year + 1)]
out = {}
for i in range(0, len(titles), 25):
    d = api(action='query', prop='revisions', rvprop='content|ids', rvslots='main', redirects='1', titles='|'.join(titles[i:i + 25]))
    red = {r['to']: r['from'] for r in d['query'].get('redirects', [])}
    for p in d['query']['pages']:
        if p.get('missing'): continue
        src = red.get(p['title'], p['title'])
        out[src[:4]] = {'title': p['title'], 'rev': p['revisions'][0]['revid'], 'text': p['revisions'][0]['slots']['main']['content']}
    print(len(out), 'articles'); time.sleep(2)
json.dump(out, open(OUT + 'articles.json', 'w'), ensure_ascii=False)
