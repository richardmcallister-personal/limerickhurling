#!/usr/bin/env python3
"""Write site/<page>/index.html from tools/pages/<page>.html with the shared shell. Run from the repo root after editing a page."""
import os, glob, re
HEAD = '''<!doctype html><html lang="en-IE"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex"><meta name="theme-color" content="#00693e">
<title>Limerick Hurling · {title}</title>
<link rel="icon" href="/assets/favicon-32.png" type="image/png"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"><link rel="manifest" href="/manifest.webmanifest">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="Limerick">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Archivo:wght@300;400;500;600;700&display=swap">
<link rel="stylesheet" href="/mu.css"></head><body><a class="skip" href="#main-content">Skip to main content</a><div class="wrap">
<header class="mu"><a class="brand" href="/"><img src="/assets/crest-88.png" alt="" width="44" height="44" decoding="async"><h1><small>Luimneach</small>Limerick Hurling</h1></a><div class="from" id="from">{kick}<span>{sub}</span></div></header>
<nav class="munav" aria-label="Sections"></nav>
<main id="main-content" tabindex="-1">
'''
FOOT = '''
</main>
<footer class="mu">Results and scorers from <a href="https://en.wikipedia.org/wiki/Limerick_county_hurling_team">Wikipedia</a> (CC BY-SA 4.0), where match records are incomplete in early seasons. An independent fan site, not connected to Limerick GAA or the GAA.</footer>
</div>
<script src="/lh.js"></script>
<script>
(function(){{
LH.nav({nav!r});
var $=function(i){{return document.getElementById(i)}}, E=LH.esc;
{script}
}})();
</script></body></html>
'''
for f in sorted(glob.glob('tools/pages/*.html')):
    name = os.path.basename(f)[:-5]; t = open(f, encoding='utf-8').read()
    meta = dict(re.findall(r'^<!--(\w+):(.*?)-->\s*$', t, re.M))
    t = re.sub(r'^<!--\w+:.*?-->\s*\n', '', t, flags=re.M)
    body, script = t.split('<script>', 1); script = script.rsplit('</script>', 1)[0]
    out = 'site/index.html' if name == 'index' else f'site/{name}/index.html'
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(HEAD.format(title=meta.get('title', name), kick=meta.get('kick', ''), sub=meta.get('sub', '')) + body + FOOT.format(nav=meta.get('nav', ''), script=script))
print('ok')
