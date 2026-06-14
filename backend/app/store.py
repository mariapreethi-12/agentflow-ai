from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.agent_outputs import generate_artifacts
from app.database import SessionLocal, init_db
from app.db_models import ApprovalRecord, ArtifactRecord, ProjectRecord
from app.schemas import (
    Approval,
    ApprovalRequest,
    Artifact,
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
            created_at=now,
            updated_at=now,
        )

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

            if "idea" in update or "answers" in update:
                record.artifacts.clear()
                session.flush()
                artifacts = generate_artifacts(record.idea, self._answers_from_record(record))
                record.artifacts.extend(self._artifact_records(project_id, artifacts))

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


store = ProjectStore()
