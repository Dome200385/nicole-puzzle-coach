# Nicole Puzzle Coach V6.8.20

Targeted WM Coach / Readiness audit fix.

Root cause fixed:
- V6.8.19 used an undefined JavaScript function `fmtSec()` while rendering
  the 10-puzzle median audit.
- That exception occurred inside the main WM Coach loading block, so Readiness
  could appear while target times, zone, next puzzle and weekly plan stayed empty.

V6.8.20:
- adds a safe local readiness time formatter
- isolates the median audit rendering in its own try/catch
- shows the exact comparison puzzles without being able to break WM Coach
- keeps the V6.8.19 readiness formula unchanged
- training load remains excluded from Readiness
- improvement remains bonus-only

No database migration.
