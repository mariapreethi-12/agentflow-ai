# AgentFlow Next Steps

## Immediate Next Milestone

Add deployment and demo polish.

Why this is next:

- The full core agent chain is OpenAI-backed.
- Projects now persist locally through SQLAlchemy and SQLite.
- Projects now keep human chat messages and generated runnable backend files.
- Generated backend files can be built into local folders under `backend/generated_apps/`.
- Generated backend apps can be launched on a local URL with Run app.
- A polished README/demo package will make the project easier to show recruiters.

## Implementation Plan

1. Capture screenshots of the main workflow.
2. Add README screenshots and a concise demo section.
3. Create a short GIF/video showing idea input, approval gates, and OpenAI-generated artifacts.
4. Add deployment notes for frontend and backend.
5. Optionally add PostgreSQL production setup instructions with `DATABASE_URL`.
6. Keep `.env` local-only and do not expose secrets.
7. Run:

```powershell
npm run build
cd backend
.venv\Scripts\python.exe tests\smoke_test.py
```

8. Commit and push.

## Later Milestones

- Add generated file viewer improvements.
- Add project history screen.
- Add generated frontend React files.
- Add deployment instructions.
- Add README screenshots and a demo GIF.
- Deploy frontend and backend.
