from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProjectRecord(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    idea: Mapped[str] = mapped_column(Text, nullable=False)
    answers: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    chat_messages: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    generated_files: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    active_stage: Mapped[str] = mapped_column(String(32), nullable=False, default="intake")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    approvals: Mapped[list["ApprovalRecord"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    artifacts: Mapped[list["ArtifactRecord"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class ApprovalRecord(Base):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stage: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    note: Mapped[str] = mapped_column(Text, nullable=False)

    project: Mapped[ProjectRecord] = relationship(back_populates="approvals")


class ArtifactRecord(Base):
    __tablename__ = "artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    artifact_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    schema_name: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    project: Mapped[ProjectRecord] = relationship(back_populates="artifacts")
