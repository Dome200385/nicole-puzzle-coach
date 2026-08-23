# V6.12.2 – Registration Fingerprint Diagnostics
- Read-only recursive inspection of already-working MSP payloads.
- Searches nested structures for:
  user, player, profile, member, team, category, participant, participation,
  entry, registered, registration, attending, competition, event, signup, joined.
- Specifically checks whether the authenticated player's own ID appears anywhere nested.
- Covers profile, statistics, results, collections, library, competitions list,
  World Jigsaw Puzzle Championship 2026 detail, Swiss Puzzle Championship 2026 detail.
- No writes and no coach/readiness/training changes.
