# Nicole Puzzle Coach V6.8.26 – Performance & Sync UX

- Major independent dashboard requests start in parallel instead of sequentially.
- Auxiliary dashboard loaders run in parallel on initial load and after MSP sync.
- Removed obsolete manual-training request and a hidden reference to the deleted manual form.
- MySpeedPuzzling sync button now has a visible spinner plus live status:
  loading -> recalculating dashboard -> completed.
- "Fortschritt pro Puzzle" moved to the bottom of the dashboard.
- Existing Readiness / Coach logic is unchanged.
