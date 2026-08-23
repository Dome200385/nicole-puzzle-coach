# V6.10.8 – PWA Update + Training Rendering

- Fixed stale PWA service-worker cache (old v696 -> v6108).
- Service worker explicitly checks for an update after launch and reloads on controller change.
- Weekly plan now has an independent fallback renderer triggered immediately after wm-plan arrives.
- The weekly-plan box can no longer fail silently: it shows sessions or an explicit status message.
- Further Training Selection keeps its outer dropdowns.
- Every individual puzzle inside the three selectors is now a nested dropdown with details hidden until tapped.
- Resilient Mode and all coach calculations unchanged.
