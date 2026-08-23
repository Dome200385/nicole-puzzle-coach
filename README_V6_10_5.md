# V6.10.5 – Today Leak Cleanup

- Removed all legacy WM/training metric blocks from the visible Training section.
- Legacy JS target IDs retained as hidden data sinks under WM to avoid breaking calculations.
- Today cannot display Training/WM/Progress sections through mobile CSS leakage.
- Further training selection remains only in Training.
- Resilient Mode and calculation logic unchanged.
