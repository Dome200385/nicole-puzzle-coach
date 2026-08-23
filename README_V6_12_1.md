# Nicole Puzzle Coach V6.12.1

Fix for MSP Datenstruktur-Diagnose HTTP 500.

Root cause: V6.12.0 called `get_results(token, limit=50)`, but `get_results()` only accepts `(token, cache=True)`. The TypeError occurred before the old safety wrapper was entered.

Changes:
- corrected `get_results(token)` call
- hardened diagnostic calls with lazy factories so synchronous signature/call errors are caught
- per-source error type, stage and elapsed time
- no changes to Coach, WM targets, training logic or persisted user data
