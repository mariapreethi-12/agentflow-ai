# AgentFlow Next Steps

## Immediate Next Milestone

Add the OpenAI QA Agent.

Why this is next:

- PM/PRD, Architect, and Backend Code Plan agents are already real OpenAI agents.
- QA Agent makes the workflow feel more production-minded.
- It is recruiter-visible because it can show tests, edge cases, and manual QA checks.

## Implementation Plan

1. Add `QA_PLAN_SCHEMA` to `backend/app/openai_agents.py`.
2. Add `generate_qa_plan_with_openai(idea, answers, prd, architecture, backend_plan)`.
3. Include strict JSON schema fields:
   - `unit_tests`
   - `api_tests`
   - `edge_cases`
   - `manual_checklist`
4. Optional but impressive:
   - `coverage_notes`
   - `risk_based_priorities`
5. Wire into `backend/app/agent_outputs.py`.
6. Preserve fallback behavior.
7. Add smoke test assertions.
8. Run:

```powershell
npm run build
cd backend
.venv\Scripts\python.exe tests\smoke_test.py
```

9. Commit and push.

## Later Milestones

- Add real Reviewer Agent.
- Add PostgreSQL persistence.
- Add project history screen.
- Add generated file viewer improvements.
- Add deployment instructions.
- Add README screenshots and a demo GIF.
- Deploy frontend and backend.
