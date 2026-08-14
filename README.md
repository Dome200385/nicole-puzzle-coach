# Nicole Puzzle Coach Backend V1

Enthalten:
- FastAPI Backend
- Render Blueprint
- MySpeedPuzzling OAuth2
- Read-only Scopes: profile, results, statistics, collections
- Daten-Sync
- Turnier-Eingabe
- Swagger unter /docs

## Deployment
1. Dateien in ein neues GitHub-Repository hochladen.
2. Render -> New -> Blueprint -> Repository verbinden.
3. Nach dem ersten Deploy die Render-URL notieren.
4. APP_BASE_URL in Render auf diese URL setzen.
5. Bei MySpeedPuzzling Redirect URL eintragen:
   https://DEINE-RENDER-URL.onrender.com/auth/myspeedpuzzling/callback
6. OAuth-Antrag absenden.
7. Nach Freigabe MSP_CLIENT_ID und MSP_CLIENT_SECRET in Render setzen.
8. /auth/myspeedpuzzling/login öffnen.

V1 speichert Tokens absichtlich nur temporär. Nach erfolgreichem API-Test folgt PostgreSQL + Coach Engine.
