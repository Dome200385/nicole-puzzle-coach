# V6.11.9 – MSP API Route Discovery

Read-only diagnostics after all guessed registration endpoints returned 404.

Checks standard schema locations:
- /openapi.json
- /api/openapi.json
- /api/v1/openapi.json
- Swagger variants

If an OpenAPI schema is available, the UI extracts routes containing:
registration, participation, entry, competition, event.

Also sends OPTIONS to the known working competitions endpoints and reports Allow headers.

No coach/readiness/training changes. No writes to MSP.
