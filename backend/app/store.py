from datetime import datetime, timezone

from app.agent_outputs import generate_artifacts
from app.schemas import Approval, ApprovalRequest, Project, ProjectCreate, ProjectUpdate


class ProjectStore:
    def __init__(self) -> None:
        self._projects: dict[str, Project] = {}

    def list_projects(self) -> list[Project]:
        return sorted(
            self._projects.values(),
            key=lambda project: project.updated_at,
            reverse=True,
        )

    def create_project(self, payload: ProjectCreate) -> Project:
        now = datetime.now(timezone.utc)
        project = Project(
            name=payload.name,
            idea=payload.idea,
            answers=payload.answers,
            approvals={
                "intake": Approval(
                    approved=True,
                    approved_at=now,
                    note="Project created from product-owner input.",
                )
            },
            artifacts=generate_artifacts(payload.idea, payload.answers),
            created_at=now,
            updated_at=now,
        )
        self._projects[project.id] = project
        return project

    def get_project(self, project_id: str) -> Project | None:
        return self._projects.get(project_id)

    def update_project(self, project_id: str, payload: ProjectUpdate) -> Project | None:
        project = self.get_project(project_id)
        if not project:
            return None

        update = payload.model_dump(exclude_unset=True)
        for field, value in update.items():
            setattr(project, field, value)

        if "idea" in update or "answers" in update:
            project.artifacts = generate_artifacts(project.idea, project.answers)

        project.updated_at = datetime.now(timezone.utc)
        self._projects[project.id] = project
        return project

    def approve_stage(
        self, project_id: str, payload: ApprovalRequest
    ) -> Project | None:
        project = self.get_project(project_id)
        if not project:
            return None

        project.approvals[payload.stage] = Approval(
            approved=True,
            approved_at=datetime.now(timezone.utc),
            note=payload.note or "Approved by human reviewer.",
        )
        project.active_stage = payload.stage
        project.updated_at = datetime.now(timezone.utc)
        self._projects[project.id] = project
        return project


store = ProjectStore()
