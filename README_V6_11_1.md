# V6.11.1
- Corrects false "Sync fehlgeschlagen": a successful /sync is no longer marked failed because a secondary panel reload fails.
- Resilient Mode now represents actual legacy fallback, not a failure of the separate tournament request.
- WM/readiness/form continue from the latest official MySpeedPuzzling sync snapshot.
- Tournament endpoint now prefers competitions saved by the last successful official sync, then local continuity.
- Tournament UI no longer remains stuck at "Prüfe bestätigte Anmeldung…".
- No training/readiness formulas changed.
