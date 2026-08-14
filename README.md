# Nicole Puzzle Coach Backend V2

Neu:
- PostgreSQL/SQLAlchemy
- persistente verschlüsselte OAuth-Tokens
- persistente MySpeedPuzzling-Snapshots
- Turniere und Trainingseinheiten
- erster Tournament Readiness Score
- Python 3.13.5 im Blueprint

## Nächster Render-Schritt
1. Render -> New -> PostgreSQL.
2. Name: `nicole-puzzle-coach-db`
3. Internal Database URL kopieren.
4. Beim Web Service Environment setzen:
   `DATABASE_URL=<Internal Database URL>`
5. Optional aber empfohlen:
   `TOKEN_ENCRYPTION_KEY=<lange zufällige Zeichenfolge>`
6. V2 nach GitHub hochladen/committen. Render deployt automatisch.
7. Test:
   `/health`
   `/db/health`
   `/docs`

Nach OAuth-Freigabe MSP_CLIENT_ID und MSP_CLIENT_SECRET ersetzen und `/auth/myspeedpuzzling/login` öffnen.
