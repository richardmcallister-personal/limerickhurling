// limerickhurling Worker: serves ./site. No feed or secrets yet; the archive is static JSON built from Wikipedia.
// The site stays noindex until Richard launches it.
export default {
  async fetch(request, env) {
    const res = await env.ASSETS.fetch(request);
    const out = new Response(res.body, res);
    out.headers.set("X-Robots-Tag", "noindex");
    const p = new URL(request.url).pathname;
    if (p.endsWith(".ics")) out.headers.set("content-type", "text/calendar; charset=utf-8");
    if (p.startsWith("/history/")) out.headers.set("cache-control", "public, max-age=3600");
    return out;
  },
};
