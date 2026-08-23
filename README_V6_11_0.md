# Nicole Puzzle Coach V6.11.0 – Live Competition & Resilient Fix

- Fixed race condition that overwrote the complete confirmed competition list with only the next WM competition.
- /msp/my-competitions is now the authoritative renderer for confirmed tournaments.
- Valladolid and Swiss Puzzle Championship can coexist in the confirmed tournament list.
- Competition endpoint exposes whether the MySpeedPuzzling request was genuinely live.
- A successful live competition request clears a false Resilient Mode banner.
- Local tournament fallback no longer makes the entire app look offline.
- wm-plan resilient flag now reflects live/snapshot mode instead of always being true.
- Training, readiness and puzzle recommendation calculations unchanged.
