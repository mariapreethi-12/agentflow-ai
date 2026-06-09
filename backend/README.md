# AgentFlow Backend

FastAPI service for the AgentFlow human-in-the-loop project workflow.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Endpoints

- `GET /health`
- `GET /projects`
- `POST /projects`
- `GET /projects/{project_id}`
- `PATCH /projects/{project_id}`
- `POST /projects/{project_id}/approve`

The first backend milestone uses an in-memory store. PostgreSQL can replace it later without changing the route contract.
