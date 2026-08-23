# V6.11.2
Fix for the remaining stuck state visible in V6.11.1.
- The separate tournament request now has an 8-second client timeout.
- The backend MSP tournament call has a 7-second timeout.
- A hanging tournament endpoint can no longer leave “Prüfe bestätigte Anmeldung…” indefinitely.
- Core readiness/form data remains independent.
- Resilient Mode continues to represent only the core fallback state, not tournament availability.
