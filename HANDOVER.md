# Limerick hurling: where things stand (2 Nov 2026)

Read CLAUDE.md first.

## Done
Live on limerickhurling.wiki (also limerickhurling.richardmcallister.workers.dev), noindex.
Pages: manager, hub, season (any year), results (filters), match, players, player, opponents, opponent, managers, honours, records, search, more. Dark mode, phone tab bar, calendar file. County crests from Richard's gaa_assets folder.
Archive: 786 games 1887-2026 from Wikipedia. Details and checks in tools/data/reconcile.txt.

- 7 Nov 2026: manutd.wiki redesign ported (green masthead, scoreboards, Explore card, calendar subscribe menu); Irish version via English/Gaeilge picker; 2027 home shirt with detail views and two launch photos (tools/data/shirts_extra.json, source not recorded); dates and times stripped out of round names.

- 7 Nov 2026: ground pages have Wikipedia facts, Limerick's record by competition, finals, biggest recorded crowd and a map; Grounds page has a map of all 62 placed grounds. Duplicate ground names merged (66 grounds). No coordinates for Bruff, Tulla, Ballygalget, Riverstown.

## Needs Richard
- Rights for the photos are not cleared. Richard chose to publish them; recheck before removing noindex. No grounds photo yet for Cusack Park (Ennis), Kilmallock, Birr, Portlaoise, Markets Field.

## Open items
- 2027 fixtures are provisional and partial: league rounds 1, 4 and 5 and the Munster order, no Munster dates. Recheck tools/data/fixtures.json when the master fixtures come out.
- Results won't update on their own. A scheduled refresh after each game day would do it, once the 2027 season starts.
- Foireann API key, if a club administrator will request one: fixtures, results and tables from 2013, automatic.
- No team sheets or current panel: Wikipedia's panel list dates from 2021.
- Not ported from manutd.wiki: Ask, match alerts, trips, shirts, timeline, compare, analytics.
- Munster Hurling League (pre-season) is not in the archive.
