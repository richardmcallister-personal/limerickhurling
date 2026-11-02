/* Limerick hurling: shared helpers. Forked in spirit from manutd.wiki's mu.js; no live feed, everything is static JSON. */
(function(){
var LH=window.LH={}, NAV=[["/","Hub"],["/season/","Season"],["/results/","Results"],["/players/","Players"],["/opponents/","Opponents"],["/managers/","Managers"],["/grounds/","Grounds"],["/honours/","Honours"],["/shirts/","Shirts"],["/records/","Records"]];
var C={NL:"National League",MSHC:"Munster",AISHC:"All-Ireland"};
LH.comp=function(c){return C[c]||c};
var esc=LH.esc=function(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})};
function fold(t){return String(t||"").normalize("NFKD").replace(/[̀-ͯ]/g,"").toLowerCase().replace(/[’']/g,"")}
var slug=LH.slug=function(t){return fold(t).replace(/-/g," ").replace(/[^a-z0-9 ]/g,"").trim().replace(/ +/g,"-")};
var CR="antrim carlow clare cork derry donegal down dublin galway kerry kildare kilkenny laois limerick london meath offaly tipperary waterford westmeath wexford".split(" ");
var crest=LH.crest=function(n,s){s=s||18; var k=slug(n); return CR.indexOf(k)<0?"":'<img class="crest" src="/assets/crests/'+k+'.webp" alt="" width="'+s+'" height="'+s+'" style="width:'+s+'px;height:'+s+'px" loading="lazy" decoding="async">'};
LH.vs=function(a,b,s){return '<div class="vs">'+crest(a,s||44)+crest(b,s||44)+'</div>'};
LH.q=function(k){return new URLSearchParams(location.search).get(k)};
var cache={}; LH.get=function(n){return cache[n]||(cache[n]=fetch("/history/"+n+".json").then(function(r){if(!r.ok)throw new Error(n);return r.json()}))};
var fmtD=LH.fmtD=function(d,long){if(!d)return "";return new Date(d+"T12:00:00Z").toLocaleDateString("en-GB",long?{weekday:"short",day:"numeric",month:"short",year:"numeric",timeZone:"UTC"}:{day:"numeric",month:"short",year:"numeric",timeZone:"UTC"})};
var gp=LH.gp=function(a){return a&&a[0]!=null?a[0]+"-"+a[1]:""};
LH.score=function(m){if(!m.r)return '<span class="score rd">'+esc(m.wo||"no result")+'</span>'; return '<span class="score r'+m.r.toLowerCase()+'">'+gp(m.u)+' <small>('+m.gf+')</small> – '+gp(m.o)+' <small>('+m.ga+')</small></span>'};
LH.scs=function(m,lim){var a=(m.sc||[]).slice().sort(function(x,y){return (y[1]*3+y[2])-(x[1]*3+x[2])}); if(lim)a=a.slice(0,lim); return a.map(function(s){return '<a href="/player/?p='+slug(s[0])+'" style="color:inherit">'+esc(s[0])+'</a> '+s[1]+'-'+s[2]}).join(", ")};
LH.row=function(m,opt){opt=opt||{}; var title=crest(m.opp)+'v '+esc(m.opp);
  return '<li><span class="d">'+(m.d?fmtD(m.d):m.y)+'</span><span class="o"><a href="/match/?id='+m.id+'">'+title+'</a><small>'+esc(C[m.cn])+(m.rnd?' · '+esc(m.rnd):'')+(m.v&&!opt.nov?' · '+esc(m.v):'')+'</small>'+(opt.sc&&m.sc?'<span class="sclist" style="display:block">'+LH.scs(m,5)+'</span>':'')+'</span>'+LH.score(m)+'</li>'};
LH.list=function(L,opt){return L.length?'<ul class="mlist">'+L.map(function(m){return LH.row(m,opt)}).join("")+'</ul>':'<p class="empty">Nothing here.</p>'};
LH.tot=function(L){var t={p:0,w:0,d:0,l:0,gf:0,ga:0}; L.forEach(function(m){if(!m.r)return; t.p++; t[m.r.toLowerCase()]++; t.gf+=m.gf; t.ga+=m.ga}); return t};
LH.stat=function(k,v,s){return '<div class="stat"><div class="k">'+esc(k)+'</div><div class="v">'+v+'</div>'+(s?'<div class="s">'+s+'</div>':'')+'</div>'};
LH.nav=function(active){var el=document.querySelector("nav.munav"); if(!el)return;
  el.innerHTML=NAV.map(function(n){return '<a href="'+n[0]+'"'+(n[1]===active?' aria-current="page"':'')+'>'+n[1]+'</a>'}).join("")+'<form class="musearch" role="search" action="/search/"><input type="search" name="q" placeholder="Search players, opponents, seasons…" aria-label="Search the site" autocomplete="off"><div class="hits" hidden></div></form>';
  searchBox(el.querySelector(".musearch"));
  var I={h:'<circle cx="12" cy="12" r="9"/><path d="M12 3v18M3 12h18"/>',s:'<path d="M4 6h16M4 12h16M4 18h10"/>',r:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',p:'<circle cx="12" cy="8" r="4"/><path d="M4 21c1-5 4-7 8-7s7 2 8 7"/>',m:'<circle cx="5" cy="12" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="19" cy="12" r="1.5"/>'};
  var T=[["/","Hub",I.h,["Hub"]],["/season/","Season",I.s,["Season"]],["/results/","Results",I.r,["Results"]],["/players/","Players",I.p,["Players"]],["/more/","More",I.m,["More","Opponents","Managers","Honours","Records","Grounds","Shirts"]]];
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
document.addEventListener("DOMContentLoaded",function(){var f=document.querySelector("footer.mu"); if(!f)return; var cur="auto"; try{cur=localStorage.getItem("mu:theme")||"auto"}catch(e){}
  var d=document.createElement("span"); d.className="themesw"; d.setAttribute("role","group"); d.setAttribute("aria-label","Appearance"); d.innerHTML=["auto","light","dark"].map(function(m){return '<button type="button" data-m="'+m+'" aria-pressed="'+(m===cur)+'">'+m+'</button>'}).join(""); d.addEventListener("click",function(e){var b=e.target.closest("button"); if(b)theme(b.dataset.m)}); f.appendChild(document.createTextNode(" Appearance:")); f.appendChild(d)});
LH.credit=function(c,extra){return '<span class="attr">'+(extra?esc(extra)+' ':'')+'Photo: <a href="'+esc(c.page)+'" rel="noopener">'+esc(c.by||c.site)+'</a></span>'};
LH.fail=function(el){el.innerHTML='<p class="empty">This section could not load. Refresh to try again.</p>'};
})();
