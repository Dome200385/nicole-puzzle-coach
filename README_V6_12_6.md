# V6.12.6 – Stable Confirmed Tournaments + Diagnostic Cleanup

Root cause confirmed by comparing V6.10.9 with current code:
- MSP competition listing remains live and returns all competitions.
- Current exposed competition payloads do not expose a personal registration flag.
- V6.10.9 displayed known confirmed tournaments by merging configured confirmation identities with tournament data.
- Later versions removed that merge while trying to eliminate local fallback.

V6.12.6:
- Uses official MSP competition metadata live for name/date/location/status.
- Keeps only the identity (slug) of the two already confirmed registrations in app configuration.
- Registration lookup failure no longer marks the whole coach Resilient.
- Last official snapshot is used only if the MSP competition list itself is temporarily unavailable.
- Removes temporary developer diagnostic cards from the normal UI.
- No changes to readiness/training/performance formulas.
