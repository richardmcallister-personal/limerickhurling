# Limerick hurling: where things stand (2 Nov 2026)

Read CLAUDE.md first.

## Done
Pages: hub, season (any year), results (filters), match, players, player, opponents, opponent, managers, honours, records, search, more. Dark mode, phone tab bar, calendar file.
Archive: 786 games 1887-2026 from Wikipedia. Details and checks in tools/data/reconcile.txt.

## Needs Richard
- A Cloudflare Worker connected to this repo (name limerickhurling), and a domain. Add the domain to `routes` in wrangler.jsonc, as on irelandrugby.
- Real crest, kit and competition images. The icon is a placeholder sliotar on green.

## Open items
- 2027 fixtures are provisional and partial: league rounds 1, 4 and 5 and the Munster order, no Munster dates. Recheck tools/data/fixtures.json when the master fixtures come out.
- Results won't update on their own. A scheduled refresh after each game day would do it, once the 2027 season starts.
- Foireann API key, if a club administrator will request one: fixtures, results and tables from 2013, automatic.
- No team sheets or current panel: Wikipedia's panel list dates from 2021.
- Not ported from manutd.wiki: Ask, match alerts, trips, shirts, timeline, compare, analytics.
- Munster Hurling League (pre-season) is not in the archive.
