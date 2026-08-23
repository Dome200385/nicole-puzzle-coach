# Nicole Puzzle Coach V6.8.13 – Sync + Progress + Cooldown

This release addresses the case where results entered directly in
MySpeedPuzzling did not appear in the coach until a manual backend sync.

New:
1. Dashboard button: "↻ MySpeedPuzzling aktualisieren"
   - calls the existing cache-bypassing `/sync`
   - reports how many new result rows were detected
   - reloads coach, median Top 5 and progress tiles

2. `/sync` now returns:
   - previous_results_count
   - new_results_count
   - new_results (up to 20)
   This makes it immediately visible whether MySpeedPuzzling actually returned
   the newly entered results.

3. Freshly solved recommendation puzzles get a 7-day cooldown.
   They disappear from "Nächstes empfohlenes Puzzle" and the weekly puzzle
   assignment instead of being proposed again immediately.

4. New "📈 Fortschritt pro Puzzle" tile:
   - latest time
   - previous time
   - personal best
   - improvement / slowdown
   - official MSP solo median where available
   - number of solo attempts

Important:
- We intentionally do NOT auto-sync on every dashboard page load, because the
  MySpeedPuzzling API owner explicitly requested caching/stable API behavior.
- The user has an explicit refresh button when new MSP results are entered.

Deploy into `/app`:
- main.py
- ui.py
- wm_coach.py
- myspeedpuzzling.py

No DB migration.
