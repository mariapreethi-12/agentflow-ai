from pathlib import Path

from app.schemas import Project


GENERATED_APPS_DIR = Path(__file__).resolve().parents[1] / "generated_apps"


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
