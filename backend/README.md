# AgentFlow Backend

FastAPI service for the AgentFlow human-in-the-loop project workflow.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## OpenAI Agents

Copy `.env.example` to `.env` and set `OPENAI_API_KEY` to enable real PM/PRD, Architecture, Backend Code Plan, QA Plan, and Review Report generation through the OpenAI Responses API. `OPENAI_MODEL` defaults to `gpt-4o-mini`.

If `OPENAI_API_KEY` is missing or the OpenAI request fails, the backend automatically uses deterministic fallback artifacts so the demo still runs.

## Persistence

The backend uses SQLAlchemy. By default it persists projects to local SQLite at `backend/agentflow.db`.

Set `DATABASE_URL` to a PostgreSQL connection string when you are ready to use Postgres, for example:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/agentflow
```

## Endpoints

- `GET /health`
- `GET /ai/status`
- `GET /projects`
- `POST /projects`
- `GET /projects/{project_id}`
- `PATCH /projects/{project_id}`
- `POST /projects/{project_id}/approve`
- `POST /projects/{project_id}/chat`
- `POST /projects/{project_id}/generate-files`

The API contract stays the same whether the backend uses local SQLite or PostgreSQL.
