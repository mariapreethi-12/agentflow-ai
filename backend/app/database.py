import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import event
from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agentflow.db")
is_sqlite = DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False, "timeout": 30} if is_sqlite else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


if is_sqlite:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragmas(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.close()


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    if is_sqlite:
        _ensure_sqlite_columns()


def _ensure_sqlite_columns() -> None:
    inspector = inspect(engine)
    if "projects" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("projects")}
    with engine.begin() as connection:
        if "chat_messages" not in columns:
            connection.execute(
                text("ALTER TABLE projects ADD COLUMN chat_messages JSON DEFAULT '[]' NOT NULL")
            )
        if "generated_files" not in columns:
            connection.execute(
                text("ALTER TABLE projects ADD COLUMN generated_files JSON DEFAULT '[]' NOT NULL")
            )


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
