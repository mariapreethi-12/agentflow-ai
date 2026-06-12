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

BACKEND_CODE_SCHEMA = {
    "type": "object",
    "properties": {
        "framework": {"type": "string"},
        "files": {"type": "array", "items": {"type": "string"}},
        "validation_rules": {"type": "array", "items": {"type": "string"}},
        "implementation_notes": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "framework",
        "files",
        "validation_rules",
        "implementation_notes",
    ],
    "additionalProperties": False,
}

QA_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "unit_tests": {"type": "array", "items": {"type": "string"}},
        "api_tests": {"type": "array", "items": {"type": "string"}},
        "edge_cases": {"type": "array", "items": {"type": "string"}},
        "manual_checklist": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["unit_tests", "api_tests", "edge_cases", "manual_checklist"],
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


def generate_backend_plan_with_openai(
    idea: str,
    answers: dict[int, str],
    prd: dict[str, Any],
    architecture: dict[str, Any],
) -> dict[str, Any] | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    prompt = _build_backend_plan_prompt(idea, answers, prd, architecture)

    try:
        return _call_openai_json_schema(
            api_key=api_key,
            prompt=prompt,
            schema_name="agentflow_backend_code_output",
            schema=BACKEND_CODE_SCHEMA,
        )
    except httpx.HTTPError:
        return None


def generate_qa_plan_with_openai(
    idea: str,
    answers: dict[int, str],
    prd: dict[str, Any],
    architecture: dict[str, Any],
    backend_plan: dict[str, Any],
) -> dict[str, Any] | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    prompt = _build_qa_plan_prompt(idea, answers, prd, architecture, backend_plan)

    try:
        return _call_openai_json_schema(
            api_key=api_key,
            prompt=prompt,
            schema_name="agentflow_qa_plan_output",
            schema=QA_PLAN_SCHEMA,
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


def _build_backend_plan_prompt(
    idea: str,
    answers: dict[int, str],
    prd: dict[str, Any],
    architecture: dict[str, Any],
) -> str:
    answer_lines = "\n".join(
        f"- Question {index}: {answer}" for index, answer in sorted(answers.items())
    )

    return f"""
You are the Backend Engineer Agent for AgentFlow.

Create an MVP backend implementation plan for this product idea:
{idea}

Product-owner answers:
{answer_lines or "- No answers provided yet."}

PRD context:
Goal: {prd.get("goal", "No goal provided.")}
Users: {", ".join(prd.get("users", []))}
Acceptance criteria: {" | ".join(prd.get("acceptance_criteria", []))}

Architecture context:
Tables: {", ".join(architecture.get("tables", []))}
API routes: {" | ".join(architecture.get("api_routes", []))}
Services: {", ".join(architecture.get("services", []))}

Return a practical FastAPI backend code plan with:
1. The framework and persistence approach.
2. Concrete file paths to generate.
3. Validation rules the backend must enforce.
4. Implementation notes for models, routes, services, and approval boundaries.

Keep the plan scoped to the MVP. Do not claim that auth, deployment, or payment handling is already complete.
""".strip()


def _build_qa_plan_prompt(
    idea: str,
    answers: dict[int, str],
    prd: dict[str, Any],
    architecture: dict[str, Any],
    backend_plan: dict[str, Any],
) -> str:
    answer_lines = "\n".join(
        f"- Question {index}: {answer}" for index, answer in sorted(answers.items())
    )

    return f"""
You are the QA Engineer Agent for AgentFlow.

Create an MVP QA plan for this product idea:
{idea}

Product-owner answers:
{answer_lines or "- No answers provided yet."}

PRD context:
Goal: {prd.get("goal", "No goal provided.")}
Acceptance criteria: {" | ".join(prd.get("acceptance_criteria", []))}

Architecture context:
Tables: {", ".join(architecture.get("tables", []))}
API routes: {" | ".join(architecture.get("api_routes", []))}

Backend plan context:
Framework: {backend_plan.get("framework", "No framework provided.")}
Files: {", ".join(backend_plan.get("files", []))}
Validation rules: {" | ".join(backend_plan.get("validation_rules", []))}

Return a practical QA plan with:
1. Unit tests for services, validators, models, and state transitions.
2. API tests for the generated routes.
3. Edge cases tied to real product risk.
4. Manual QA checklist steps a human reviewer can run during the demo.

Keep this realistic for an MVP. Do not include unrelated enterprise testing or fake completed test results.
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
