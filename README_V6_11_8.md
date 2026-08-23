# V6.11.8 – Registration Endpoint Diagnostics

Read-only endpoint discovery for MySpeedPuzzling tournament registrations.

It probes likely official API paths such as:
- /me/competitions
- /me/registrations
- /me/competition-registrations
- /players/{player_id}/competitions
- /players/{player_id}/registrations
- /competitions/{id}/registrations
- /competitions/{id}/participants
- /competitions/{id}/entries
- /competitions/{id}/me
- /competitions/{id}/my-registration

For privacy, it does not display other participant identities. It reports only
endpoint success/shape and whether the authenticated player's own id is found.

No writes. No coach/readiness/training formula changes.
