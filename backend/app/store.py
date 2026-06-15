from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.agent_outputs import generate_artifacts
from app.database import SessionLocal, init_db
from app.db_models import ApprovalRecord, ArtifactRecord, ProjectRecord
from app.file_builder import build_generated_files
from app.schemas import (
    Approval,
    ApprovalRequest,
    Artifact,
    ChatMessageCreate,
    Project,
    ProjectCreate,
    ProjectUpdate,
)


class ProjectStore:
    def __init__(self) -> None:
        init_db()

    def list_projects(self) -> list[Project]:
        with SessionLocal() as session:
            records = session.scalars(
                select(ProjectRecord)
                .options(
                    selectinload(ProjectRecord.approvals),
                    selectinload(ProjectRecord.artifacts),
                )
                .order_by(ProjectRecord.updated_at.desc())
            ).all()
            return [self._to_project(record) for record in records]

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
            chat_messages=self._initial_chat_messages(),
            created_at=now,
            updated_at=now,
        )
        project.generated_files = build_generated_files(project)

        with SessionLocal() as session:
            record = self._create_record(project)
            session.add(record)
            session.commit()
            return self._get_project(session, project.id)

    def get_project(self, project_id: str) -> Project | None:
        with SessionLocal() as session:
            record = self._get_record(session, project_id)
            return self._to_project(record) if record else None

    def update_project(self, project_id: str, payload: ProjectUpdate) -> Project | None:
        with SessionLocal() as session:
            record = self._get_record(session, project_id)
            if not record:
                return None

            update = payload.model_dump(exclude_unset=True)
            if "name" in update:
                record.name = update["name"]
            if "idea" in update:
                record.idea = update["idea"]
            if "answers" in update:
                record.answers = update["answers"]
            if "active_stage" in update:
                record.active_stage = update["active_stage"]
            if "chat_messages" in update:
                record.chat_messages = update["chat_messages"]
            if "generated_files" in update:
                record.generated_files = update["generated_files"]

            if "idea" in update or "answers" in update:
                record.artifacts.clear()
                session.flush()
                artifacts = generate_artifacts(record.idea, self._answers_from_record(record))
                record.artifacts.extend(self._artifact_records(project_id, artifacts))
                project_snapshot = self._to_project(record)
                project_snapshot.artifacts = artifacts
                record.generated_files = build_generated_files(project_snapshot)

            record.updated_at = datetime.now(timezone.utc)
            session.commit()
            return self._get_project(session, project_id)

    def approve_stage(
        self, project_id: str, payload: ApprovalRequest
    ) -> Project | None:
        with SessionLocal() as session:
            record = self._get_record(session, project_id)
            if not record:
                return None

            approval = next(
                (
                    approval_record
                    for approval_record in record.approvals
                    if approval_record.stage == payload.stage
                ),
                None,
            )
            if approval:
                approval.approved = True
                approval.approved_at = datetime.now(timezone.utc)
                approval.note = payload.note or "Approved by human reviewer."
            else:
                record.approvals.append(
                    ApprovalRecord(
                        project_id=project_id,
                        stage=payload.stage,
                        approved=True,
                        approved_at=datetime.now(timezone.utc),
                        note=payload.note or "Approved by human reviewer.",
                    )
                )

            record.active_stage = payload.stage
            record.updated_at = datetime.now(timezone.utc)
            session.commit()
            return self._get_project(session, project_id)

    def generate_files(self, project_id: str) -> Project | None:
        with SessionLocal() as session:
            record = self._get_record(session, project_id)
            if not record:
                return None

            project = self._to_project(record)
            record.generated_files = build_generated_files(project)
            record.updated_at = datetime.now(timezone.utc)
            session.commit()
            return self._get_project(session, project_id)

    def add_chat_message(
        self, project_id: str, payload: ChatMessageCreate
    ) -> Project | None:
        with SessionLocal() as session:
            record = self._get_record(session, project_id)
            if not record:
                return None

            messages = list(record.chat_messages or [])
            now = datetime.now(timezone.utc).isoformat()
            messages.append(
                {
                    "role": payload.role,
                    "content": payload.content,
                    "stage": payload.stage or record.active_stage,
                    "created_at": now,
                }
            )
            if payload.role == "human":
                messages.append(
                    {
                        "role": "assistant",
                        "content": self._assistant_reply(payload.content, record),
                        "stage": record.active_stage,
                        "created_at": now,
                    }
                )
            record.chat_messages = messages
            record.updated_at = datetime.now(timezone.utc)
            session.commit()
            return self._get_project(session, project_id)

    def _get_project(self, session: Session, project_id: str) -> Project:
        record = self._get_record(session, project_id)
        if not record:
            raise ValueError(f"Project not found after write: {project_id}")
        return self._to_project(record)

    def _get_record(self, session: Session, project_id: str) -> ProjectRecord | None:
        return session.scalar(
            select(ProjectRecord)
            .where(ProjectRecord.id == project_id)
            .options(
                selectinload(ProjectRecord.approvals),
                selectinload(ProjectRecord.artifacts),
            )
        )

    def _create_record(self, project: Project) -> ProjectRecord:
        return ProjectRecord(
            id=project.id,
            name=project.name,
            idea=project.idea,
            answers=project.answers,
            chat_messages=project.chat_messages,
            generated_files=project.generated_files,
            active_stage=project.active_stage,
            created_at=project.created_at,
            updated_at=project.updated_at,
            approvals=self._approval_records(project.id, project.approvals),
            artifacts=self._artifact_records(project.id, project.artifacts),
        )

    def _to_project(self, record: ProjectRecord) -> Project:
        return Project(
            id=record.id,
            name=record.name,
            idea=record.idea,
            answers=self._answers_from_record(record),
            chat_messages=record.chat_messages or [],
            generated_files=record.generated_files or [],
            active_stage=record.active_stage,
            approvals={
                approval.stage: Approval(
                    approved=approval.approved,
                    approved_at=approval.approved_at,
                    note=approval.note,
                )
                for approval in record.approvals
            },
            artifacts={
                artifact.artifact_key: Artifact(
                    schema_name=artifact.schema_name,
                    title=artifact.title,
                    score=artifact.score,
                    generated_at=artifact.generated_at,
                    data=artifact.data,
                )
                for artifact in record.artifacts
            },
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    def _answers_from_record(self, record: ProjectRecord) -> dict[int, str]:
        return {int(key): value for key, value in (record.answers or {}).items()}

    def _approval_records(
        self, project_id: str, approvals: dict[str, Approval]
    ) -> list[ApprovalRecord]:
        return [
            ApprovalRecord(
                project_id=project_id,
                stage=stage,
                approved=approval.approved,
                approved_at=approval.approved_at,
                note=approval.note,
            )
            for stage, approval in approvals.items()
        ]

    def _artifact_records(
        self, project_id: str, artifacts: dict[str, Artifact]
    ) -> list[ArtifactRecord]:
        return [
            ArtifactRecord(
                project_id=project_id,
                artifact_key=artifact_key,
                schema_name=artifact.schema_name,
                title=artifact.title,
                score=artifact.score,
                generated_at=artifact.generated_at,
                data=artifact.data,
            )
            for artifact_key, artifact in artifacts.items()
        ]

    def _initial_chat_messages(self) -> list[dict[str, str]]:
        return [
            {
                "role": "assistant",
                "content": "I am ready. Tag me with a question or approve the next step when you want the agent team to continue.",
                "stage": "intake",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ]

    def _assistant_reply(self, content: str, record: ProjectRecord) -> str:
        lowered = content.lower()
        stage = record.active_stage
        file_count = len(record.generated_files or [])
        if "run" in lowered or "launch" in lowered:
            return "Use Run app to start the generated FastAPI app on its own localhost URL. I will keep the built app linked here."
        if "build" in lowered or "files" in lowered:
            return f"I have {file_count} generated files ready. Use Generate files, then Build app, then Run app to turn them into a live API."
        if "approve" in lowered:
            return f"I noted your approval intent for {stage}. Use Approve step to record the official human gate."
        if "@backend" in lowered:
            return "Backend Agent here: I can produce the FastAPI file plan, materialize files, and run the generated API locally."
        if "@qa" in lowered:
            return "QA Agent here: I will focus on route tests, validation edge cases, and manual demo checks."
        if "@reviewer" in lowered:
            return "Reviewer Agent here: I will flag security, validation, missing tests, and production-readiness risks."
        return f"I tagged this note to {stage}. I will keep the human context with the project as the workflow moves forward."


store = ProjectStore()
