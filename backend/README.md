# AgentFlow Backend

FastAPI service for the AgentFlow human-in-the-loop project workflow.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## OpenAI PM/PRD Agent

Copy `.env.example` to `.env` and set `OPENAI_API_KEY` to enable real PM/PRD generation through the OpenAI Responses API. `OPENAI_MODEL` defaults to `gpt-4o-mini`.

If `OPENAI_API_KEY` is missing or the OpenAI request fails, the backend automatically uses deterministic fallback artifacts so the demo still runs.

## Endpoints

- `GET /health`
- `GET /ai/status`
- `GET /projects`
- `POST /projects`
- `GET /projects/{project_id}`
- `PATCH /projects/{project_id}`
- `POST /projects/{project_id}/approve`

The first backend milestone uses an in-memory store. PostgreSQL can replace it later without changing the route contract.
