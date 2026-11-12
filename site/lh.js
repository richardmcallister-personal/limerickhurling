/* Limerick hurling: shared helpers. Forked in spirit from manutd.wiki's mu.js; no live feed, everything is static JSON. */
(function(){
var LH=window.LH={}, NAV=[["/","Hub"],["/season/","Season"],["/results/","Results"],["/players/","Players"],["/opponents/","Opponents"],["/managers/","Managers"],["/grounds/","Grounds"],["/honours/","Honours"],["/shirts/","Shirts"],["/videos/","Videos"],["/records/","Records"]];
LH.ROADS=[2018,2020,2021,2022,2023,2026];   /* title runs with a Road to the title page linked from honours, oldest first; the newest is the default */
var C={NL:"National League",MSHC:"Munster",AISHC:"All-Ireland"};
LH.comp=function(c){return C[c]||c};
var esc=LH.esc=function(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})};
function fold(t){return String(t||"").normalize("NFKD").replace(/[̀-ͯ]/g,"").toLowerCase().replace(/[’']/g,"")}
var slug=LH.slug=function(t){return fold(t).replace(/-/g," ").replace(/[^a-z0-9 ]/g,"").trim().replace(/ +/g,"-")};
var CR="antrim carlow clare cork derry donegal down dublin galway kerry kildare kilkenny laois limerick london meath offaly tipperary waterford westmeath wexford".split(" ");
var crest=LH.crest=function(n,s){s=s||18; var k=slug(n); return CR.indexOf(k)<0?"":'<img class="crest" src="/assets/crests/'+k+'.webp" alt="" width="'+s+'" height="'+s+'" style="width:'+s+'px;height:'+s+'px" loading="lazy" decoding="async">'};
LH.vs=function(a,b,s){return '<div class="vs">'+crest(a,s||44)+crest(b,s||44)+'</div>'};
LH.q=function(k){return new URLSearchParams(location.search).get(k)};
var cache={}; LH.get=function(n){return cache[n]||(cache[n]=fetch("/history/"+n+".json"+(window.LH_V?"?v="+window.LH_V:"")).then(function(r){if(!r.ok)throw new Error(n);return r.json()}))};
var fmtD=LH.fmtD=function(d,long){if(!d)return "";return new Date(d+"T12:00:00Z").toLocaleDateString("en-GB",long?{weekday:"short",day:"numeric",month:"short",year:"numeric",timeZone:"UTC"}:{day:"numeric",month:"short",year:"numeric",timeZone:"UTC"})};
var gp=LH.gp=function(a){return a&&a[0]!=null?a[0]+"-"+a[1]:""};
LH.score=function(m){if(!m.r)return '<span class="score rd">'+esc(m.wo||"no result")+'</span>'; return '<span class="score r'+m.r.toLowerCase()+'">'+gp(m.u)+' <small>('+m.gf+')</small> – '+gp(m.o)+' <small>('+m.ga+')</small></span>'};
LH.scs=function(m,lim){var a=(m.sc||[]).slice().sort(function(x,y){return (y[1]*3+y[2])-(x[1]*3+x[2])}); if(lim)a=a.slice(0,lim); return a.map(function(s){return '<a href="/player/?p='+slug(s[0])+'" style="color:inherit">'+esc(s[0])+'</a> '+s[1]+'-'+s[2]}).join(", ")};
LH.row=function(m,opt){opt=opt||{}; var title=crest(m.opp)+'v '+esc(m.opp)+(m.vd?'<span class="vb" title="Video" role="img" aria-label="Video"></span>':'');
  return '<li><span class="d">'+(m.d?fmtD(m.d):m.y)+'</span><span class="o"><a href="/match/?id='+m.id+'">'+title+'</a><small>'+esc(C[m.cn])+(m.rnd?' · '+esc(m.rnd):'')+(m.v&&!opt.nov?' · '+esc(m.v):'')+'</small>'+(opt.sc&&m.sc?'<span class="sclist" style="display:block">'+LH.scs(m,5)+'</span>':'')+'</span>'+LH.score(m)+'</li>'};
/* YouTube: a thumbnail until tapped, then the youtube-nocookie player in place. Videos the uploader won't let others embed open on YouTube. */
LH.video=function(v){var w="https://www.youtube.com/watch?v="+v.id, th='<img src="https://i.ytimg.com/vi/'+v.id+'/hqdefault.jpg" alt="" width="480" height="360" loading="lazy" decoding="async"><span class="ytb" aria-hidden="true"></span>';
  return '<figure class="ytf"><div class="yt">'+(v.e===false?'<a class="ytp" href="'+w+'" target="_blank" rel="noopener" aria-label="Watch on YouTube">'+th+'</a>':'<button type="button" class="ytp" data-yt="'+esc(v.id)+'" aria-label="Play video">'+th+'</button>')+'</div><figcaption class="note"><span>'+(v.k==="full"?"Full game":v.k==="highlights"?"Highlights":"Match video")+'</span> · <span data-noi18n>'+esc(v.ch)+'</span> · <a class="link" href="'+w+'" target="_blank" rel="noopener">YouTube</a>'+(v.e===false?' · <span>Plays on YouTube only</span>':'')+'</figcaption></figure>'};
document.addEventListener("click",function(e){var b=e.target.closest&&e.target.closest("button.ytp"); if(!b)return; var f=document.createElement("iframe");
  f.src="https://www.youtube-nocookie.com/embed/"+encodeURIComponent(b.getAttribute("data-yt"))+"?autoplay=1&rel=0&playsinline=1"; f.title="YouTube video"; f.allow="autoplay; encrypted-media; picture-in-picture; fullscreen"; f.allowFullscreen=true; f.referrerPolicy="strict-origin-when-cross-origin"; b.replaceWith(f)});
/* What a goal was worth: 3 since 1896, 5 from 1892, and before that a goal outweighed any number of points (0 here). */
LH.gv=function(y){return y<1892?0:y<1896?5:3};
/* Clubs (clubs.json, from players' Wikipedia infoboxes): look up a person by archive player slug, a club by slug,
   and who was on the county panel in a year. Only players with a Wikipedia page are there. */
LH.clubIdx=function(C){var A={},S={},W={}; C.players.forEach(function(p){if(p.a)A[p.a]=p; W[p.w]=p}); C.clubs.forEach(function(c){S[c.s]=c});
  return {A:A,S:S,W:W,of:function(name){return A[slug(name)]},
   on:function(y){return C.players.filter(function(p){return p.y&&p.y[0]<=y&&y<=p.y[1]})},
   wiki:function(p){return "https://en.wikipedia.org/wiki/"+encodeURIComponent(p.w.replace(/ /g,"_"))}}};
/* Club badge: a shield in the club's colours (from its Wikipedia infobox) with its initials. Not the club's crest. */
LH.badge=function(c,size){size=size||20; if(!c)return ""; var k=c.col||[], h=Math.round(size*46/40),
  L="M2 2H20V44C11 41.5 2 35 2 24Z", R="M20 2H38V24C38 35 29 41.5 20 44Z", S="M2 2H38V24C38 35 29 41.5 20 44C11 41.5 2 35 2 24Z", t=c.ab||"", fs=t.length>1?13:17;
  var body=k.length?(k.length>1?'<path d="'+L+'" fill="'+k[0]+'"/><path d="'+R+'" fill="'+k[1]+'"/>':'<path d="'+S+'" fill="'+k[0]+'"/>'):'<path d="'+S+'" style="fill:var(--tint)"/>';
  return '<svg class="badge" width="'+size+'" height="'+h+'" viewBox="0 0 40 46" aria-hidden="true">'+body+'<path d="'+S+'" fill="none" stroke="currentColor" stroke-opacity=".28" stroke-width="1.5"/>'+
   (size<28?'':'<text x="20" y="'+(t.length>1?28:30)+'" text-anchor="middle" font-family="system-ui,-apple-system,sans-serif" font-weight="800" font-size="'+fs+'"'+(k.length?' fill="#fff" stroke="rgba(0,0,0,.55)" stroke-width="2.4" paint-order="stroke"':' style="fill:var(--muted)"')+'>'+esc(t)+'</text>')+'</svg>'};
LH.list=function(L,opt){return L.length?'<ul class="mlist">'+L.map(function(m){return LH.row(m,opt)}).join("")+'</ul>':'<p class="empty">Nothing here.</p>'};
LH.tot=function(L){var t={p:0,w:0,d:0,l:0,gf:0,ga:0}; L.forEach(function(m){if(!m.r)return; t.p++; t[m.r.toLowerCase()]++; t.gf+=m.gf; t.ga+=m.ga}); return t};
LH.stat=function(k,v,s){return '<div class="stat"><div class="k">'+esc(k)+'</div><div class="v">'+v+'</div>'+(s?'<div class="s">'+s+'</div>':'')+'</div>'};
LH.nav=function(active){var el=document.querySelector("nav.munav"); if(!el)return;
  // sticky masthead: header and section bar travel together; --mast tells anchors how tall it is (as on manutd.wiki)
  (function(){var h=document.querySelector("header.mu"); if(!h||h.parentNode.classList.contains("mast"))return;
    var m=document.createElement("div"); m.className="mast"; h.parentNode.insertBefore(m,h); m.appendChild(h); m.appendChild(el);
    function set(){document.documentElement.style.setProperty("--mast",m.offsetHeight+"px")} set(); if(window.ResizeObserver)new ResizeObserver(set).observe(m)})();
  el.innerHTML=NAV.map(function(n){return '<a href="'+n[0]+'"'+(n[1]===active?' aria-current="page"':'')+'>'+n[1]+'</a>'}).join("")+'<form class="musearch" role="search" action="/search/"><input type="search" name="q" placeholder="Search players, opponents, seasons…" aria-label="Search the site" autocomplete="off"><div class="hits" hidden></div></form>';
  searchBox(el.querySelector(".musearch"));
  var I={h:'<circle cx="12" cy="12" r="9"/><path d="M12 3v18M3 12h18"/>',s:'<path d="M4 6h16M4 12h16M4 18h10"/>',r:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',p:'<circle cx="12" cy="8" r="4"/><path d="M4 21c1-5 4-7 8-7s7 2 8 7"/>',m:'<circle cx="5" cy="12" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="19" cy="12" r="1.5"/>'};
  var T=[["/","Hub",I.h,["Hub"]],["/season/","Season",I.s,["Season"]],["/results/","Results",I.r,["Results"]],["/players/","Players",I.p,["Players"]],["/more/","More",I.m,["More","Opponents","Managers","Honours","Records","Grounds","Shirts","Videos"]]];
  var t=document.createElement("nav"); t.className="mutabs"; t.setAttribute("aria-label","Sections");
  t.innerHTML=T.map(function(x){return '<a href="'+x[0]+'"'+(x[3].indexOf(active)>=0?' aria-current="page"':'')+'><svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'+x[2]+'</svg>'+x[1]+'</a>'}).join(""); document.body.appendChild(t);
};
var IDX=null; function load(){return IDX||(IDX=fetch("/search.json").then(function(r){return r.json()}).then(function(j){return j.map(function(e){return {t:e[0],k:e[1],u:e[2],s:e[3],f:fold(e[0])}})}))}
var find=LH.find=function(q,n){var w=fold(q).split(/\s+/).filter(Boolean); return load().then(function(L){return L.filter(function(e){return w.every(function(x){return e.f.indexOf(x)>=0})}).sort(function(a,b){return (b.f.indexOf(w[0])===0)-(a.f.indexOf(w[0])===0)}).slice(0,n||8)})};
var hit=LH.hit=function(e){return '<a href="'+e.u+'"><span class="k">'+esc(e.k)+'</span><span class="t">'+esc(e.t)+'<small>'+esc(e.s)+'</small></span></a>'};
function searchBox(f){if(!f)return; var i=f.querySelector("input"), b=f.querySelector(".hits"), last="";
  i.addEventListener("input",function(){var q=i.value.trim(); last=q; if(q.length<2){b.hidden=true;return} find(q,8).then(function(l){if(q!==last)return; b.innerHTML=l.map(hit).join("")+(l.length?'<a class="all" href="/search/?q='+encodeURIComponent(q)+'">All results for “'+esc(q)+'” →</a>':'<span class="none">Nothing matches “'+esc(q)+'”</span>'); b.hidden=false})});
  i.addEventListener("keydown",function(e){if(e.key==="Escape")b.hidden=true});
  document.addEventListener("click",function(e){if(!f.contains(e.target))b.hidden=true});
}
function theme(m){try{if(m==="auto")localStorage.removeItem("mu:theme"); else localStorage.setItem("mu:theme",m)}catch(e){} if(m==="auto")document.documentElement.removeAttribute("data-theme"); else document.documentElement.setAttribute("data-theme",m); document.querySelectorAll(".themesw button").forEach(function(b){b.setAttribute("aria-pressed",b.dataset.m===m)})}
(function(){try{var t=localStorage.getItem("mu:theme"); if(t)document.documentElement.setAttribute("data-theme",t)}catch(e){}})();
/* Site footer, after manutd.wiki: who we are, the sections, official links and Richard's other sites. The page's own source note,
   appearance and language controls stay underneath. */
document.addEventListener("DOMContentLoaded",function(){var f=document.querySelector("footer.mu"); if(!f||f.querySelector(".sitefoot"))return;
  function col(h,L){return '<div class="fcol"><h2>'+h+'</h2><ul>'+L.map(function(l){return '<li><a href="'+l[0]+'"'+(/^https?:/.test(l[0])?' target="_blank" rel="noopener"':'')+'>'+l[1]+'</a></li>'}).join("")+'</ul></div>'}
  var sis=[["https://manutd.wiki/","Manchester United","manutd.wiki","manutd"],["https://irelandfootball.wiki/","Ireland Football","irelandfootball.wiki","irelandfootball"],["https://irelandrugby.wiki/","Ireland Rugby","irelandrugby.wiki","irelandrugby"],["https://footballclub.wiki/","Football Club Wiki","footballclub.wiki","footballclub"]];
  var d=document.createElement("div"); d.className="sitefoot";
  d.innerHTML='<div class="fbrand"><a class="fname" href="/"><img src="/assets/crest-88.png" alt="" width="36" height="36"><span translate="no">Limerick Hurling</span></a><p>An independent fan site about Limerick\'s senior hurlers.</p><p class="fdata">Data: Wikipedia (CC BY-SA), YouTube, OpenStreetMap.</p></div>'+
    '<div class="fcols">'+col("Matchday",[["/","Hub"],["/results/","Fixtures and results"],["/season/","This season"],["webcal://limerickhurling.wiki/calendar.ics","Fixtures in your calendar"]])+
    col("History",[["/honours/","Honours"],["/road/","Road to the title"],["/records/","Records"],["/players/","Players"],["/managers/","Managers"]])+
    col("Explore",[["/opponents/","Opponents"],["/clubs/","Clubs"],["/grounds/","Grounds"],["/shirts/","Shirts"],["/videos/","Videos"]])+
    col("Official",[["https://www.limerickgaa.ie/","limerickgaa.ie"],["https://munstergaa.ie/","munstergaa.ie"],["https://www.gaa.ie/","gaa.ie"],["/more/","More"]])+'</div>'+
    '<div class="fsis"><h2>Other sites</h2><ul>'+sis.map(function(x){return '<li><a href="'+x[0]+'" target="_blank" rel="noopener"><img src="/assets/sites/'+x[3]+'.webp" alt="" width="40" height="40" loading="lazy" decoding="async"><span><b translate="no">'+x[1]+'</b><small translate="no">'+x[2]+'</small></span></a></li>'}).join("")+'</ul></div>';
  f.insertBefore(d,f.firstChild); f.classList.add("big")});
document.addEventListener("DOMContentLoaded",function(){var f=document.querySelector("footer.mu"); if(!f)return; var cur="auto"; try{cur=localStorage.getItem("mu:theme")||"auto"}catch(e){}
  var d=document.createElement("span"); d.className="themesw"; d.setAttribute("role","group"); d.setAttribute("aria-label","Appearance"); d.innerHTML=["auto","light","dark"].map(function(m){return '<button type="button" data-m="'+m+'" aria-pressed="'+(m===cur)+'">'+m+'</button>'}).join(""); d.addEventListener("click",function(e){var b=e.target.closest("button"); if(b)theme(b.dataset.m)}); f.appendChild(document.createTextNode(" Appearance:")); f.appendChild(d)});
// scoreboard: crest and name either side, score (or "v") in the middle
LH.board=function(a,b,m){function side(n){return '<a class="sbt" href="'+(n==="Limerick"?"/":"/opponent/?o="+slug(n))+'">'+crest(n,56)+'<span>'+esc(n)+'</span></a>'}
  var mid=m&&m.r?'<b>'+(a==="Limerick"?gp(m.u)+' – '+gp(m.o):gp(m.o)+' – '+gp(m.u))+'</b><span class="rs '+m.r+'">'+({W:"Won",D:"Drawn",L:"Lost"})[m.r]+'</span>'+(LH.gv(m.y)?'<small>'+(function(){var v=LH.gv(m.y),f=m.u[0]*v+m.u[1],g=m.o[0]*v+m.o[1]; return a==="Limerick"?f+' – '+g:g+' – '+f})()+' on points value</small>':''):'<b class="vs">v</b>';
  return '<div class="sb">'+side(a)+'<div class="sbs">'+mid+'</div>'+side(b)+'</div>'};
var CAL='<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>';
LH.calMenu=function(){var h="limerickhurling.wiki/calendar.ics";
  return '<details class="calmenu"><summary class="btn ghost">'+CAL+'<span>Add to calendar</span></summary><div class="calpop">'+
    '<a href="webcal://'+h+'">Subscribe to every fixture<small>Apple Calendar or Outlook; updates itself when dates are confirmed</small></a>'+
    '<a href="https://calendar.google.com/calendar/r?cid=webcal://'+h+'" target="_blank" rel="noopener">Subscribe in Google Calendar<small>Opens Google Calendar</small></a>'+
    '<a href="/calendar.ics" download>Download the fixtures<small>A one-off .ics file</small></a></div></details>'};
document.addEventListener("click",function(e){document.querySelectorAll("details.calmenu[open]").forEach(function(d){if(!d.contains(e.target))d.removeAttribute("open")})});
document.addEventListener("keydown",function(e){if(e.key==="Escape")document.querySelectorAll("details.calmenu[open]").forEach(function(d){d.removeAttribute("open")})});
LH.credit=function(c,extra){return '<span class="attr">'+(extra?esc(extra)+' ':'')+'Photo: '+(c.page?'<a href="'+esc(c.page)+'" rel="noopener">'+esc(c.by||c.site)+'</a>':esc(c.site))+'</span>'};
LH.fail=function(el){el.innerHTML='<p class="empty">This section could not load. Refresh to try again.</p>'};
})();
