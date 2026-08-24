
# V6.12.8 – Shared Competition Pipeline

Verified architecture fix:
- Single shared MSP competition fetch pipeline.
- In-process 15-minute competition cache.
- asyncio lock prevents duplicate concurrent competition requests.
- `/coach/wm-plan` and `/msp/my-competitions` share that payload.
- Competition metadata failure does not decide Resilient Mode.
- Frontend timeout is longer than backend timeout.
- Loading state is guaranteed to terminate.
- Snapshot continuity remains available.
- No readiness/form/training formula changes.
