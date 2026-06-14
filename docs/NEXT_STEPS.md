# AgentFlow Next Steps

## Immediate Next Milestone

Add PostgreSQL persistence.

Why this is next:

- The full core agent chain is now OpenAI-backed.
- PostgreSQL makes projects survive backend restarts.
- Persistence makes the app feel like a real product instead of a single-session demo.

## Implementation Plan

1. Add SQLAlchemy and PostgreSQL dependencies.
2. Create database models for projects, artifacts, and approvals.
3. Replace the in-memory `ProjectStore` with a database-backed store.
4. Add a local `DATABASE_URL` setting with a SQLite fallback if PostgreSQL is not configured.
5. Preserve the existing API contract.
6. Add persistence-focused smoke test assertions.
7. Keep `.env` local-only and do not expose secrets.
8. Run:

```powershell
npm run build
cd backend
.venv\Scripts\python.exe tests\smoke_test.py
```

9. Commit and push.

## Later Milestones

- Add project history screen.
- Add generated file viewer improvements.
- Add deployment instructions.
- Add README screenshots and a demo GIF.
- Deploy frontend and backend.
