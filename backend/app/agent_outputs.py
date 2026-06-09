from datetime import datetime, timezone
from typing import Any

from app.openai_agents import generate_architecture_with_openai, generate_pm_prd_with_openai
from app.schemas import Artifact


DEMO_QUESTIONS = [
    "Who can create appointments: patients only, staff only, or both?",
    "Should dentists define availability manually or sync it from a calendar?",
    "Do appointments need payment before confirmation?",
    "What reminder channels are required: email, SMS, or both?",
    "Can admins override booking conflicts in emergencies?",
]


def generate_artifacts(idea: str, answers: dict[int, str]) -> dict[str, Artifact]:
    answer_list = [answer for answer in answers.values() if answer]
    reminder_choice = _find_answer(answer_list, "reminder")
    payment_choice = _find_answer(answer_list, "payment")
    pm_prd_output = generate_pm_prd_with_openai(idea, answers)
    clarifying_data = (
        {
            **pm_prd_output["clarifying_questions"],
            "generation_source": "openai",
        }
        if pm_prd_output
        else {
            "questions": DEMO_QUESTIONS,
            "assumptions": [
                "The MVP focuses on one clinic location.",
                "Role-based access can start with patient and admin users.",
                "Dentist availability is managed inside the generated app.",
            ],
            "decision_required": "Confirm who can book and how reminders should work.",
            "generation_source": "fallback",
        }
    )
    prd_data = (
        {
            **pm_prd_output["prd"],
            "generation_source": "openai",
        }
        if pm_prd_output
        else {
            "goal": "Let patients request dental appointments while admins manage dentist availability and booking approvals.",
            "users": ["Patients", "Clinic admins", "Dentists"],
            "user_stories": [
                "As a patient, I can request an appointment from available dentist slots.",
                "As an admin, I can approve, reject, or reschedule pending appointments.",
                "As a dentist, I can see my upcoming appointments and availability.",
            ],
            "acceptance_criteria": [
                "The system prevents double-booking for the same dentist and time slot.",
                "Patients must provide valid contact details before requesting an appointment.",
                "Every approval or override is recorded in an audit trail.",
            ],
            "scope_notes": [
                idea,
                reminder_choice or "Email reminders are included in the MVP.",
                payment_choice or "Payments stay out of scope for the first build.",
            ],
            "generation_source": "fallback",
        }
    )
    architecture_output = generate_architecture_with_openai(idea, answers, prd_data)
    architecture_data = (
        {
            **architecture_output,
            "generation_source": "openai",
        }
        if architecture_output
        else {
            "tables": [
                "users",
                "patients",
                "dentists",
                "availability_slots",
                "appointments",
                "reminders",
                "audit_events",
            ],
            "api_routes": [
                "POST /appointments",
                "GET /availability",
                "PATCH /appointments/:id/status",
                "POST /reminders/test",
            ],
            "services": [
                "Scheduling validator",
                "Reminder dispatcher",
                "Admin approval workflow",
                "Audit logger",
            ],
            "approval_gate": "Human reviews schema and route contract before code generation.",
            "generation_source": "fallback",
        }
    )

    return {
        "clarifying_questions": _artifact(
            "clarifying_questions",
            "Clarifying Questions",
            96 if pm_prd_output else 94,
            clarifying_data,
        ),
        "prd": _artifact(
            "prd",
            "Generated PRD",
            93 if pm_prd_output else 91,
            prd_data,
        ),
        "architecture": _artifact(
            "architecture",
            "Architecture Output",
            92 if architecture_output else 88,
            architecture_data,
        ),
        "backend_plan": _artifact(
            "backend_plan",
            "Backend Code Plan",
            84,
            {
                "framework": "FastAPI with SQLAlchemy and PostgreSQL",
                "files": [
                    "app/main.py",
                    "app/models.py",
                    "app/routes/appointments.py",
                    "app/routes/availability.py",
                    "app/services/scheduling.py",
                ],
                "validation_rules": [
                    "Reject duplicate appointments for the same dentist and slot.",
                    "Reject appointments with missing patient contact details.",
                    "Reject bookings for past dates or unavailable slots.",
                ],
                "implementation_notes": [
                    "Use an appointment status enum: pending, approved, cancelled, completed.",
                    "Keep auth as a placeholder until the backend milestone.",
                ],
            },
        ),
        "qa_plan": _artifact(
            "qa_plan",
            "QA Test Cases",
            89,
            {
                "unit_tests": [
                    "Scheduling validator detects conflicts.",
                    "Appointment status transitions follow approval rules.",
                ],
                "api_tests": [
                    "POST /appointments succeeds for an open slot.",
                    "POST /appointments fails for duplicate slots.",
                    "PATCH /appointments/:id/status requires admin role.",
                ],
                "edge_cases": [
                    "Invalid email or phone number.",
                    "Appointment requested outside clinic hours.",
                    "Admin override without audit reason.",
                ],
                "manual_checklist": [
                    "Create patient.",
                    "Request booking.",
                    "Approve as admin.",
                    "Confirm reminder event is logged.",
                ],
            },
        ),
        "review_report": _artifact(
            "review_report",
            "Reviewer Report",
            82,
            {
                "score": 82,
                "strengths": [
                    "Clear approval gates.",
                    "Practical API boundaries.",
                    "Good demo scenario for recruiters.",
                ],
                "risks": [
                    "Auth is still a placeholder.",
                    "Reminder retry handling needs a real implementation.",
                ],
                "recommendations": [
                    "Add role checks before exposing admin actions.",
                    "Add rate limits to appointment creation before a public demo.",
                    "Track reminder delivery status.",
                ],
            },
        ),
    }


def _artifact(schema_name: str, title: str, score: int, data: dict[str, Any]) -> Artifact:
    return Artifact(
        schema_name=schema_name,
        title=title,
        score=score,
        generated_at=datetime.now(timezone.utc),
        data=data,
    )


def _find_answer(answers: list[str], keyword: str) -> str | None:
    return next((answer for answer in answers if keyword in answer.lower()), None)
