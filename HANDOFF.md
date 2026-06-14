# AgentFlow AI Handoff

Last updated: 2026-06-09

## Repository

- GitHub: https://github.com/mariapreethi-12/agentflow-ai.git
- Local path: `C:\Users\maria\OneDrive\Documents\New project\agentflow-ai`
- Branch: `main`
- Latest pushed commit before persistence milestone: `1019886 Add OpenAI reviewer agent`
- Working tree status at handoff: clean, `main...origin/main`

## Project Goal

AgentFlow is a human-in-the-loop multi-agent software engineering platform. The portfolio story is that a user enters a product idea, then AI agents act like a Product Manager, Architect, Backend Engineer, QA Engineer, Reviewer, and later DevOps Assistant. Humans approve major stages before the workflow continues.

The MVP demo scenario is a dental clinic appointment booking system.

## Current Build Status

Completed:

- React/Vite frontend.
- FastAPI backend.
- Frontend connects to backend with local-storage fallback.
- Project state persistence in the browser.
- Human approval workflow.
- Structured artifact schemas.
- OpenAI-backed PM/PRD Agent.
- OpenAI-backed Architect Agent.
- OpenAI-backed Backend Code Plan Agent.
- OpenAI-backed QA Plan Agent.
- OpenAI-backed Reviewer Agent.
- SQLAlchemy persistence with local SQLite default.
- Deterministic fallback artifacts when OpenAI is unavailable.
- Backend smoke test.
- GitHub repo initialized and pushed.

Current real OpenAI agents:

- PM/PRD Agent:
  - Generates clarifying questions.
  - Generates PRD goal, users, user stories, acceptance criteria, and scope notes.
- Architect Agent:
  - Generates database tables.
  - Generates REST API routes.
  - Generates backend services.
  - Generates a human approval gate.
- Backend Code Plan Agent:
  - Generates FastAPI framework and persistence notes.
  - Generates planned backend file paths.
  - Generates validation rules.
  - Generates implementation notes.
- QA Plan Agent:
  - Generates unit tests.
  - Generates API tests.
  - Generates edge cases.
  - Generates manual QA checklist steps.
- Reviewer Agent:
  - Generates quality score.
  - Generates strengths.
  - Generates risks.
  - Generates recommendations.

Not completed yet:

- PostgreSQL production configuration.
- Auth.
- Deployment.
- README screenshots.
- Demo GIF or video.

## Key Files

- `src/main.jsx`: main frontend UI and API sync behavior.
- `src/api.js`: frontend API client and snake_case/camelCase normalization.
- `src/agentSchemas.js`: frontend fallback artifact schema and demo data.
- `src/styles.css`: dashboard styling.
- `backend/app/main.py`: FastAPI app and route definitions.
- `backend/app/schemas.py`: Pydantic models.
- `backend/app/database.py`: SQLAlchemy engine/session setup with SQLite default and `DATABASE_URL` override.
- `backend/app/db_models.py`: database models for projects, artifacts, and approvals.
- `backend/app/store.py`: database-backed project store.
- `backend/app/agent_outputs.py`: artifact generation coordinator.
- `backend/app/openai_agents.py`: OpenAI Responses API integrations for PM/PRD, Architect, Backend Code Plan, QA Plan, and Reviewer agents.
- `backend/tests/smoke_test.py`: backend route smoke test.
- `backend/.env.example`: environment variable template.

## Local Setup

Backend:

```powershell
cd "C:\Users\maria\OneDrive\Documents\New project\agentflow-ai\backend"
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Frontend in a second PowerShell window:

```powershell
cd "C:\Users\maria\OneDrive\Documents\New project\agentflow-ai"
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

Backend docs:

```text
http://127.0.0.1:8000/docs
```

## Environment

Backend `.env` should exist locally but must not be committed.

Required shape:

```env
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///./agentflow.db
```

Important: a previous API key was accidentally pasted visibly during setup. That old key should be treated as compromised and revoked. The current key must remain private and should never be pasted into chat, screenshots, commits, or logs.

## Verification Commands

Frontend build:

```powershell
cd "C:\Users\maria\OneDrive\Documents\New project\agentflow-ai"
npm run build
```

Backend smoke test:

```powershell
cd "C:\Users\maria\OneDrive\Documents\New project\agentflow-ai\backend"
.venv\Scripts\python.exe tests\smoke_test.py
```

Real OpenAI generation check:

```powershell
cd "C:\Users\maria\OneDrive\Documents\New project\agentflow-ai\backend"
.venv\Scripts\python.exe -c "from pathlib import Path; import sys; sys.path.insert(0, str(Path.cwd())); from fastapi.testclient import TestClient; from app.main import app; c=TestClient(app); r=c.post('/projects', json={'idea':'Build an appointment booking system for a dental clinic with dentists, patients, reminders, and admin approval','answers':{'0':'Patients and staff can book','1':'Admins define availability','2':'No payment for MVP','3':'Email reminders','4':'Admins can override with audit reason'}}); data=r.json(); print('pm_source', data['artifacts']['prd']['data'].get('generation_source')); print('architecture_source', data['artifacts']['architecture']['data'].get('generation_source'))"
```

Expected output after the reviewer-agent milestone:

```text
pm_source openai
architecture_source openai
backend_source openai
qa_source openai
review_source openai
```

If OpenAI is not configured or fails, expected fallback output:

```text
pm_source fallback
architecture_source fallback
```

## Errors Encountered and Fixes

- `npm install` timed out in sandbox:
  - Fixed by rerunning with elevated permission.
- `npm run build` initially hit Windows `EPERM` path access:
  - Fixed by rerunning with elevated permission.
- Git push blocked by dubious ownership:
  - Fixed with `git config --global --add safe.directory 'C:/Users/maria/OneDrive/Documents/New project/agentflow-ai'`.
- `gh` CLI was not available:
  - User manually created GitHub repo and provided URL.
- PowerShell rejected `OPENAI_API_KEY=...`:
  - Correct PowerShell method is writing `.env` with `Set-Content`.
- Placeholder API key caused OpenAI `401 invalid_api_key`:
  - Fixed by replacing placeholder with the real rotated key in `backend/.env`.
- Backend smoke test initially failed because `httpx` was missing:
  - Fixed by adding `httpx==0.28.1` to backend requirements.
- Python import failed in smoke test:
  - Fixed by adding backend root to `sys.path` in `backend/tests/smoke_test.py`.
- Python cache files were accidentally staged:
  - Fixed by unstaging and adding `__pycache__/` and `*.pyc` to `.gitignore`.

## Git Milestones

- `51bf012 Initial AgentFlow MVP`
- `3cd874f Add persisted workflow state`
- `0551d48 Add FastAPI backend skeleton`
- `1de9969 Connect frontend to backend API`
- `cc9926e Add OpenAI PM PRD agent`
- `4dab919 Add OpenAI architect agent`

## Recommended Next Step

Build deployment and demo polish.

Suggested scope:

- Add README screenshots.
- Add a short demo GIF or video.
- Add production deployment notes for frontend and backend.
- Optionally configure PostgreSQL via `DATABASE_URL` for a deployed backend.
- Optionally add a project history view that reads persisted projects from `/projects`.
- Run `npm run build` and backend smoke test.
- Commit and push.

## Command for the Next Agent

Use this prompt:

```text
Continue the AgentFlow project from C:\Users\maria\OneDrive\Documents\New project\agentflow-ai. Read HANDOFF.md first. The repo is pushed to https://github.com/mariapreethi-12/agentflow-ai.git on main. Do not expose or print the OpenAI API key. The next milestone is deployment/demo polish: README screenshots, a demo GIF or video, and deployment notes. Verify with frontend build and backend smoke test, commit, and push.
```
