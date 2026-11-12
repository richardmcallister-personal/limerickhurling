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


## 7 Nov 2026: videos
- 8 videos from Richard's playlist on 6 games (2018 semi and final, 2020, 2021, 2022, 2023 finals). Match pages play them in place (youtube-nocookie, tap to play); /videos/ lists them by season; ▶ marker on result rows.
- 2022 full game (IksdLKTa22I) has embedding off: shown as a link to YouTube. Clare v Cork 2024 (PoViqHOY-XY) left out, no Limerick.
- Later 7 Nov: playlist grew to 27; 18 more added (2026 final and semi, Munster games 2018-2026, 2001 Munster quarter-final, 1996 final). 26 videos on 24 games. Label "Match video" where the uploader doesn't say full game or highlights (Joco Sports, Wilderness of Tigers, GAA 1996).

## 11 Nov 2026: Road to the title
- New page /road/?y=2018: header (first since 1973, record, scores, top scorer, crowds, cup photo), route strip, game-by-game timeline (stage, scoreboard, date, ground, crowd, referee, scorers, opposition scorers, video link, match page), campaign scorers, map of grounds in order.
- Linked from honours (feature card and the 2018 year in the titles table) and from each 2018 Munster/All-Ireland match page. LH.ROADS = [2018].
- 2018 name slips fixed in HAND: T Morrisey to Tom Morrissey, D O'Donnovan to Darragh O'Donovan. The 2018 final source lists only 3-15 of 3-16 for Limerick; the page says so.
- Next candidates: 1973 and 1940 (all scorers add up), 2020 and 2021.

## 11 Nov 2026: all title runs since 2018, footer
- Road to the title now for 2018, 2020, 2021, 2022, 2023, 2026, with a year switcher on the page and on the honours card.
- 2020 v Clare (25 Oct) was both the league final and the Munster quarter-final: kept as one game with cn2/rnd2, shown on the road page and match page.
- Parser fix: "A, B, 0-1" (stray comma before a shared score) gave each name a goal. Fixed six games (2001 Antrim, 2004 Waterford, Clare and Tipperary, 2006 Clare, 2018 Offaly); 2023 Waterford now reads as the source has it (1-17 of 1-18).
- Round names: SF2 and Semi-finals now Semi-final.
- 2026 Munster: Wikipedia has no scorers for Limerick's five games, so the page marks them not recorded and hides the top-scorer tile.
- fetch_wiki.py User-Agent no longer carries Richard's email.
- Footer from manutd.wiki: brand, Matchday / History / Explore / Official columns, Other sites (manutd.wiki, irelandfootball.wiki, irelandrugby.wiki, footballclub.wiki), on the masthead green.

## 11 Nov 2026: How the score was made
- Match page: new section under the scoreboard turns each side's goals-points into a total (2-18 = 2 goals x 3 + 18 points = 24), states the margin, and says when goals beat a side with more points (or the reverse). Uses the rule of the day for 1887-1895.
- Scorer tables now show each player's points value and share of the side's total, with a stacked bar; any gap between the source's scorers and the final score shows as "Not in the source". Scorers sit straight after the explanation; the video moved below them.

## 12 Nov 2026: Clubs
- Source: Wikipedia's Category:Limerick inter-county hurlers (256 players, 55 clubs). Infobox gives club, county years, position, All-Ireland medals.
- /clubs/: by season (pick a year, all games / championship / league; clubs on the panel and their scoring that season; All-Ireland years as shortcuts), decades grid for the 16 biggest clubs, all clubs table. /club/?c=: players, county-panel timeline, scoring by competition.
- Player pages show club, years with Limerick, position and a Wikipedia link ("Probably Ciarán Carey" where linked by initials). Match pages show the club under each Limerick scorer. Road to the title has a Clubs section.
- 136 archive scorers linked (78 by initial and surname; listed in tools/data/clubs_report.txt for review).
- Club badges (12 Nov): no source has crests for every club (Wikipedia ~5 of 55, Limerick GAA has no directory), so Richard chose drawn shields in each club's colours from its Wikipedia infobox. 49 clubs have colours; 6 with no article are grey. Shown on clubs, club, player, match and road pages, noted as not the clubs' crests. Real crests could replace them if Richard supplies a folder.
