import json
import os
from typing import Any

import httpx
from dotenv import load_dotenv


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = "gpt-4o-mini"
load_dotenv()

PM_PRD_SCHEMA = {
    "type": "object",
    "properties": {
        "clarifying_questions": {
            "type": "object",
            "properties": {
                "questions": {"type": "array", "items": {"type": "string"}},
                "assumptions": {"type": "array", "items": {"type": "string"}},
                "decision_required": {"type": "string"},
            },
            "required": ["questions", "assumptions", "decision_required"],
            "additionalProperties": False,
        },
        "prd": {
            "type": "object",
            "properties": {
                "goal": {"type": "string"},
                "users": {"type": "array", "items": {"type": "string"}},
                "user_stories": {"type": "array", "items": {"type": "string"}},
                "acceptance_criteria": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "scope_notes": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "goal",
                "users",
                "user_stories",
                "acceptance_criteria",
                "scope_notes",
            ],
            "additionalProperties": False,
        },
    },
    "required": ["clarifying_questions", "prd"],
    "additionalProperties": False,
}

ARCHITECTURE_SCHEMA = {
    "type": "object",
    "properties": {
        "tables": {"type": "array", "items": {"type": "string"}},
        "api_routes": {"type": "array", "items": {"type": "string"}},
        "services": {"type": "array", "items": {"type": "string"}},
        "approval_gate": {"type": "string"},
    },
    "required": ["tables", "api_routes", "services", "approval_gate"],
    "additionalProperties": False,
}


def is_openai_configured() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def openai_model_name() -> str:
    return os.getenv("OPENAI_MODEL", DEFAULT_MODEL)


def generate_pm_prd_with_openai(
    idea: str, answers: dict[int, str]
) -> dict[str, Any] | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    prompt = _build_pm_prd_prompt(idea, answers)

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                OPENAI_RESPONSES_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": openai_model_name(),
                    "input": prompt,
                    "text": {
                        "format": {
                            "type": "json_schema",
                            "name": "agentflow_pm_prd_output",
                            "strict": True,
                            "schema": PM_PRD_SCHEMA,
                        }
                    },
                },
            )
            response.raise_for_status()
    except httpx.HTTPError:
        return None

    return _extract_json(response.json())


def generate_architecture_with_openai(
    idea: str, answers: dict[int, str], prd: dict[str, Any]
) -> dict[str, Any] | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    prompt = _build_architecture_prompt(idea, answers, prd)

    try:
        return _call_openai_json_schema(
            api_key=api_key,
            prompt=prompt,
            schema_name="agentflow_architecture_output",
            schema=ARCHITECTURE_SCHEMA,
        )
    except httpx.HTTPError:
        return None


def _build_pm_prd_prompt(idea: str, answers: dict[int, str]) -> str:
    answer_lines = "\n".join(
        f"- Question {index}: {answer}" for index, answer in sorted(answers.items())
    )

    return f"""
You are the Product Manager Agent for AgentFlow, a human-in-the-loop AI software engineering platform.

Create concise, recruiter-demo-ready PM output for this product idea:
{idea}

Known product-owner answers:
{answer_lines or "- No answers provided yet."}

Return:
1. Five clarifying questions.
2. Three assumptions.
3. One decision required.
4. A PRD with goal, users, user stories, acceptance criteria, and scope notes.

Keep the content practical for an MVP and avoid pretending deployment or auth is complete.
""".strip()


def _build_architecture_prompt(
    idea: str, answers: dict[int, str], prd: dict[str, Any]
) -> str:
    answer_lines = "\n".join(
        f"- Question {index}: {answer}" for index, answer in sorted(answers.items())
    )

    return f"""
You are the Architect Agent for AgentFlow.

Design the MVP architecture for this product idea:
{idea}

Product-owner answers:
{answer_lines or "- No answers provided yet."}

PRD context:
Goal: {prd.get("goal", "No goal provided.")}
Users: {", ".join(prd.get("users", []))}
User stories: {" | ".join(prd.get("user_stories", []))}
Acceptance criteria: {" | ".join(prd.get("acceptance_criteria", []))}

Return a practical engineering architecture with:
1. Database table names.
2. REST API routes with HTTP methods.
3. Backend services.
4. One human approval gate before implementation.

Keep it scoped to an MVP. Do not include deployment, auth provider setup, or advanced infrastructure unless essential.
""".strip()


def _call_openai_json_schema(
    api_key: str, prompt: str, schema_name: str, schema: dict[str, Any]
) -> dict[str, Any] | None:
    with httpx.Client(timeout=30) as client:
        response = client.post(
            OPENAI_RESPONSES_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": openai_model_name(),
                "input": prompt,
                "text": {
                    "format": {
                        "type": "json_schema",
                        "name": schema_name,
                        "strict": True,
                        "schema": schema,
                    }
                },
            },
        )
        response.raise_for_status()

    return _extract_json(response.json())


def _extract_json(payload: dict[str, Any]) -> dict[str, Any] | None:
    text = payload.get("output_text")
    if isinstance(text, str):
        return _parse_json(text)

    for item in payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"}:
                parsed = _parse_json(content.get("text", ""))
                if parsed:
                    return parsed

    return None


def _parse_json(value: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return None

    return parsed if isinstance(parsed, dict) else None
