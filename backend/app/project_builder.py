from pathlib import Path
import socket
import subprocess
import sys
import time

from app.schemas import Project


GENERATED_APPS_DIR = Path(__file__).resolve().parents[1] / "generated_apps"
RUNNING_APPS: dict[str, dict[str, object]] = {}


def materialize_project(project: Project) -> dict[str, object]:
    output_dir = GENERATED_APPS_DIR / project.id
    output_dir.mkdir(parents=True, exist_ok=True)

    written_files: list[str] = []
    for generated_file in project.generated_files:
        relative_path = Path(generated_file["path"])
        if relative_path.is_absolute() or ".." in relative_path.parts:
            continue

        target = output_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(generated_file["content"], encoding="utf-8")
        written_files.append(str(relative_path).replace("\\", "/"))

    return {
        "output_dir": str(output_dir),
        "files": written_files,
        "run_command": f'cd "{output_dir}" && python -m uvicorn app.main:app --reload --port 9000',
    }


def run_project(project: Project) -> dict[str, object]:
    build_result = materialize_project(project)
    existing = RUNNING_APPS.get(project.id)
    process = existing.get("process") if existing else None
    if process and process.poll() is None:
        return {
            **build_result,
            "app_url": existing["app_url"],
            "pid": process.pid,
            "status": "already_running",
        }

    port = _find_open_port()
    output_dir = Path(build_result["output_dir"])
    log_path = output_dir / "agentflow-run.log"
    log_file = log_path.open("a", encoding="utf-8")
    try:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            cwd=output_dir,
            stdin=subprocess.DEVNULL,
            stdout=log_file,
            stderr=log_file,
            creationflags=_creation_flags(),
        )
        app_url = f"http://127.0.0.1:{port}"
        _wait_for_start(process, port, log_path)
    except Exception:
        log_file.close()
        raise
    RUNNING_APPS[project.id] = {
        "process": process,
        "app_url": app_url,
        "log_file": log_file,
    }
    return {
        **build_result,
        "app_url": app_url,
        "pid": process.pid,
        "status": "started",
    }


def _find_open_port(start: int = 9000, end: int = 9100) -> int:
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("No open port found for generated app.")


def _wait_for_start(
    process: subprocess.Popen, port: int, log_path: Path, timeout_seconds: float = 8
) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(_startup_error(log_path))

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return

        time.sleep(0.2)

    process.terminate()
    raise RuntimeError("Generated app did not start before the timeout.")


def _startup_error(log_path: Path) -> str:
    if not log_path.exists():
        return "Generated app exited before startup."

    log_text = log_path.read_text(encoding="utf-8", errors="replace").strip()
    if not log_text:
        return "Generated app exited before startup."

    lines = log_text.splitlines()
    return "Generated app exited before startup: " + "\n".join(lines[-8:])


def _creation_flags() -> int:
    return getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(
        subprocess, "DETACHED_PROCESS", 0
    )
