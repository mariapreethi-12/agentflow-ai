# AgentFlow AI

AgentFlow is a human-in-the-loop multi-agent software engineering platform that turns a product idea into engineering-ready artifacts: clarifying questions, PRDs, architecture plans, backend code plans, QA cases, review reports, and deployment thinking.

The MVP focuses on a clear recruiter-friendly demo: a dental clinic appointment booking system moves through an AI software team with approval gates between major steps.

## MVP Workflow

- Product owner enters an app idea.
- PM Agent asks clarifying questions.
- PRD Agent generates scope, user stories, and acceptance criteria.
- Architect Agent generates database tables, API routes, and services.
- Backend Agent outlines FastAPI files and validation logic.
- QA Agent generates test cases and manual QA checks.
- Reviewer Agent scores quality and flags risks.

## Tech Stack

- React frontend
- Vite
- FastAPI backend
- Pydantic schemas
- TypeScript-ready JavaScript
- Lucide icons
- Future targets: PostgreSQL, LangGraph, OpenAI API

## Run Locally

Frontend:

```bash
npm install
npm run dev
```

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs open at `http://127.0.0.1:8000/docs`.

The frontend connects to the FastAPI backend at `http://127.0.0.1:8000` by default. If the backend is not running, the UI falls back to local storage so the demo still works.

To enable real PM/PRD, Architecture, Backend Code Plan, and QA Plan generation, copy `backend/.env.example` to `backend/.env` and set `OPENAI_API_KEY`. Without a key, AgentFlow uses deterministic fallback artifacts.

## API Contract

- `GET /health`
- `GET /ai/status`
- `GET /projects`
- `POST /projects`
- `GET /projects/{project_id}`
- `PATCH /projects/{project_id}`
- `POST /projects/{project_id}/approve`

## Portfolio Angle

This project demonstrates agent orchestration, human approval gates, product thinking, generated engineering artifacts, QA planning, review scoring, and production-minded AI workflow design.
