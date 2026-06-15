from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.openai_agents import is_openai_configured, openai_model_name
from app.schemas import (
    ApprovalRequest,
    ChatMessageCreate,
    Project,
    ProjectCreate,
    ProjectListItem,
    ProjectUpdate,
)
from app.store import store


app = FastAPI(
    title="AgentFlow API",
    description="Human-in-the-loop multi-agent software engineering workflow API.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ai/status")
def ai_status() -> dict[str, str | bool]:
    return {
        "provider": "openai" if is_openai_configured() else "fallback",
        "openai_configured": is_openai_configured(),
        "model": openai_model_name(),
    }


@app.get("/projects", response_model=list[ProjectListItem])
def list_projects() -> list[ProjectListItem]:
    return [
        ProjectListItem(
            id=project.id,
            name=project.name,
            active_stage=project.active_stage,
            updated_at=project.updated_at,
        )
        for project in store.list_projects()
    ]


@app.post("/projects", response_model=Project, status_code=201)
def create_project(payload: ProjectCreate) -> Project:
    return store.create_project(payload)


@app.get("/projects/{project_id}", response_model=Project)
def get_project(project_id: str) -> Project:
    project = store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.patch("/projects/{project_id}", response_model=Project)
def update_project(project_id: str, payload: ProjectUpdate) -> Project:
    project = store.update_project(project_id, payload)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.post("/projects/{project_id}/approve", response_model=Project)
def approve_project_stage(project_id: str, payload: ApprovalRequest) -> Project:
    project = store.approve_stage(project_id, payload)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.post("/projects/{project_id}/chat", response_model=Project)
def add_project_chat_message(project_id: str, payload: ChatMessageCreate) -> Project:
    project = store.add_chat_message(project_id, payload)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.post("/projects/{project_id}/generate-files", response_model=Project)
def generate_project_files(project_id: str) -> Project:
    project = store.generate_files(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
