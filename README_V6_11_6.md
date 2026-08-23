# V6.11.6
Crash-safe MSP tournament diagnostics.
- Diagnostic endpoint always returns structured JSON for handled failures.
- Removes diagnostic calls to helpers that were not guaranteed to exist in main.py.
- Uses the application's existing token + confirmed-competition helper.
- Separately checks the last saved snapshot.
- Frontend now shows raw HTTP error text if the backend itself returns a non-JSON 500.
