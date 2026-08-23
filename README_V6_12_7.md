# V6.12.7 – Fast Live Tournament Fix

Root cause fixed:
- `/msp/my-competitions` previously called `get_my_confirmed_competitions()`,
  which probed many competition detail endpoints sequentially.
- This could take tens of seconds and left the UI stuck on
  "Prüfe bestätigte Anmeldung…".
- `/coach/wm-plan` used the same expensive helper, which could incorrectly
  push the dashboard into Snapshot/Resilient mode.

V6.12.7:
- One MSP `/competitions` list call only.
- Known confirmed registration identities are matched by slug.
- Tournament name/date/location/status remain live MSP metadata.
- Per-competition detail probing is not used in normal app loading.
- Resilient Mode now reflects actual MSP list availability, not missing
  personal registration endpoints.
- Sync uses the same fast path.
- No readiness/form/training formula changes.
