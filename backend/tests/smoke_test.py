from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app


def main() -> None:
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    ai_status = client.get("/ai/status")
    assert ai_status.status_code == 200
    assert "openai_configured" in ai_status.json()

    created = client.post(
        "/projects",
        json={
            "idea": "Build a dental booking app",
            "answers": {"0": "Patients and staff can book"},
        },
    )
    assert created.status_code == 201
    project = created.json()
    assert project["active_stage"] == "intake"
    assert "prd" in project["artifacts"]
    assert "architecture" in project["artifacts"]
    assert "backend_plan" in project["artifacts"]
    assert "qa_plan" in project["artifacts"]
    assert "review_report" in project["artifacts"]
    assert "tables" in project["artifacts"]["architecture"]["data"]
    assert "files" in project["artifacts"]["backend_plan"]["data"]
    assert "api_tests" in project["artifacts"]["qa_plan"]["data"]
    assert "risks" in project["artifacts"]["review_report"]["data"]
    assert any(file["path"] == "app/main.py" for file in project["generated_files"])

    fetched = client.get(f"/projects/{project['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == project["id"]

    listed = client.get("/projects")
    assert listed.status_code == 200
    assert any(item["id"] == project["id"] for item in listed.json())

    approved = client.post(
        f"/projects/{project['id']}/approve",
        json={"stage": "prd", "note": "Scope approved."},
    )
    assert approved.status_code == 200
    assert approved.json()["approvals"]["prd"]["approved"] is True

    chat = client.post(
        f"/projects/{project['id']}/chat",
        json={"role": "human", "content": "Please keep this build runnable.", "stage": "backend"},
    )
    assert chat.status_code == 200
    assert len(chat.json()["chat_messages"]) >= 2

    files = client.post(f"/projects/{project['id']}/generate-files")
    assert files.status_code == 200
    assert any(file["path"] == "requirements.txt" for file in files.json()["generated_files"])

    build = client.post(f"/projects/{project['id']}/build")
    assert build.status_code == 200
    build_data = build.json()
    assert "app/main.py" in build_data["files"]
    assert Path(build_data["output_dir"], "app", "main.py").exists()

    print("backend smoke test passed")


if __name__ == "__main__":
    main()
