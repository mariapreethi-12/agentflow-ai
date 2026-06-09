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

    approved = client.post(
        f"/projects/{project['id']}/approve",
        json={"stage": "prd", "note": "Scope approved."},
    )
    assert approved.status_code == 200
    assert approved.json()["approvals"]["prd"]["approved"] is True

    print("backend smoke test passed")


if __name__ == "__main__":
    main()
