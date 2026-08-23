# Nicole Puzzle Coach V6.8.25

Changes:
- Persistent daily WM-Readiness history using the existing database connection
  (no new ORM model and no manual migration required).
- Stores one row per day: readiness, form signal, consistency, median hits,
  comparable puzzle count.
- Displays up to 30 recent daily bars plus 7/14/30-day changes.
- Training week plan moved directly after "Nächstes empfohlenes Puzzle".
- WM Simulation moved directly after the weekly plan.
- "Training zusätzlich manuell erfassen" removed.
- "Zusätzliche manuelle Trainings" display removed.
- Current balanced V6.8.24 Readiness calculation remains unchanged.
