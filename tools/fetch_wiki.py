#!/usr/bin/env python3
"""Download Wikipedia wikitext for hurling season articles, in polite batches, into tools/data/wiki/."""
import json, os, time, urllib.parse, urllib.request, urllib.error
OUT = os.path.join(os.path.dirname(__file__), 'data', 'wiki')
UA = 'limerickhurling data builder (richardmcallister@gmail.com)'
titles = ['Limerick county hurling team', 'List of All-Ireland Senior Hurling Championship finals', 'Munster Senior Hurling Championship', 'National Hurling League']
for y in range(1887, 2027):
    titles += [f'{y} All-Ireland Senior Hurling Championship', f'{y} Munster Senior Hurling Championship', f'{y} National Hurling League', f'{y}-{str(y+1)[2:]} National Hurling League', f'{y}–{str(y+1)[2:]} National Hurling League']
def get(batch):
    q = urllib.parse.urlencode({'action':'query','prop':'revisions','rvprop':'content|ids','rvslots':'main','format':'json','formatversion':'2','redirects':'1','maxlag':'5','titles':'|'.join(batch)})
    for attempt in range(8):
        try:
            with urllib.request.urlopen(urllib.request.Request('https://en.wikipedia.org/w/api.php?'+q, headers={'User-Agent':UA}), timeout=60) as r:
                d = json.load(r)
            if 'error' in d: raise RuntimeError(d['error'])
            return d
        except urllib.error.HTTPError as e:
            wait = int(e.headers.get('Retry-After') or 30)
            print('http', e.code, 'wait', wait, flush=True); time.sleep(min(wait, 120))
        except RuntimeError as e:
            print(e, flush=True); time.sleep(30)
    raise SystemExit('gave up')
found = 0
for i in range(0, len(titles), 40):
    d = get(titles[i:i+40])['query']
    for p in d.get('pages', []):
        if p.get('missing') or not p.get('revisions'): continue
        fn = p['title'].replace(' ', '_').replace('/', '_') + '.json'
        json.dump({'title':p['title'],'rev':p['revisions'][0]['revid'],'text':p['revisions'][0]['slots']['main']['content']}, open(os.path.join(OUT, fn),'w'))
        found += 1
    print(i, 'pages so far', found, flush=True)
    time.sleep(4)
print('DONE', found)
