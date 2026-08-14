# Nicole Puzzle Coach Backend V3

## Was V3 neu kann
- robuste Normalisierung der echten MySpeedPuzzling-Payloads
- aktueller Besitz vs. historisch gelöst / nicht mehr im Besitz
- Performance-Auswertung nach Modus und Teilezahl
- persönliche Baseline und Trend
- Consistency Score
- Turnier-spezifischer Readiness Score
- Next Puzzle Recommendation nur aus der aktuellen Bibliothek
- optional nach geplantem Turnier gefiltert
- automatische persönliche Zielzeit, sobald genügend Resultate vorhanden sind
- `/coach/status` für schnellen Systemcheck

## Wichtige URLs nach Deploy
- `/health`
- `/db/health`
- `/coach/status`
- `/docs`

Nach MySpeedPuzzling OAuth-Freigabe:
- `/auth/myspeedpuzzling/login`
- `/sync`
- `/coach/performance?mode=solo&pieces=500`
- `/coach/library`
- `/coach/next-puzzle`

## GitHub Upload
Diese Version ist absichtlich passend zu deiner aktuellen Struktur gebaut.

Im Repository soll es so aussehen:

- app/
  - __init__.py
  - config.py
  - database.py
  - db_models.py
  - schemas.py
  - crypto.py
  - myspeedpuzzling.py
  - coach.py
  - main.py
- README.md
- render.yaml
- requirements.txt

Die alten Unterordner `app/models` und `app/services` werden nicht mehr benötigt.
