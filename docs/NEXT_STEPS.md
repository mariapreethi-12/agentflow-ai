# AgentFlow Next Steps

## Immediate Next Milestone

Add the OpenAI Reviewer Agent.

Why this is next:

- PM/PRD, Architect, Backend Code Plan, and QA Plan agents are already real OpenAI agents.
- Reviewer Agent makes the workflow feel safer and more production-minded.
- It is recruiter-visible because it can show risks, security concerns, missing validation, and improvement suggestions.

## Implementation Plan

1. Add `REVIEW_REPORT_SCHEMA` to `backend/app/openai_agents.py`.
2. Add `generate_review_report_with_openai(idea, answers, prd, architecture, backend_plan, qa_plan)`.
3. Include strict JSON schema fields:
   - `score`
   - `strengths`
   - `risks`
   - `recommendations`
4. Optional but impressive:
   - `security_findings`
   - `missing_tests`
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

- Add PostgreSQL persistence.
- Add project history screen.
- Add generated file viewer improvements.
- Add deployment instructions.
- Add README screenshots and a demo GIF.
- Deploy frontend and backend.
