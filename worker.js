// limerickhurling Worker: serves ./site. No feed or secrets yet; the archive is static JSON built from Wikipedia.
// The site stays noindex until Richard launches it.
export default {
  async fetch(request, env) {
    // One address only: always https, never www. Cloudflare answers plain http unless told not to.
    const u = new URL(request.url);
    if (u.protocol === "http:" || u.hostname === "www.limerickhurling.wiki") {
      u.protocol = "https:";
      if (u.hostname === "www.limerickhurling.wiki") u.hostname = "limerickhurling.wiki";
      return Response.redirect(u.toString(), 301);
    }
    const res = await env.ASSETS.fetch(request);
    const out = new Response(res.body, res);
    out.headers.set("X-Robots-Tag", "noindex");
    out.headers.set("Strict-Transport-Security", "max-age=31536000");
    const p = new URL(request.url).pathname;
    if (p.endsWith(".ics")) out.headers.set("content-type", "text/calendar; charset=utf-8");
    if (p.startsWith("/history/")) out.headers.set("cache-control", "public, max-age=300");
    return out;
  },
};
