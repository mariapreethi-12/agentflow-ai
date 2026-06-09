# AgentFlow Next Steps

## Immediate Next Milestone

Add the OpenAI Backend Code Agent.

Why this is next:

- PM/PRD and Architect agents are already real OpenAI agents.
- Backend Code Agent makes the workflow feel like a true software engineering team.
- It is recruiter-visible because it can show planned FastAPI files, validation rules, and implementation notes.

## Implementation Plan

1. Add `BACKEND_CODE_SCHEMA` to `backend/app/openai_agents.py`.
2. Add `generate_backend_plan_with_openai(idea, answers, prd, architecture)`.
3. Include strict JSON schema fields:
   - `framework`
   - `files`
   - `validation_rules`
   - `implementation_notes`
4. Optional but impressive:
   - `code_snippets`
   - each snippet can have `file_path` and `content`.
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

- Add real QA Agent.
- Add real Reviewer Agent.
- Add PostgreSQL persistence.
- Add project history screen.
- Add generated file viewer improvements.
- Add deployment instructions.
- Add README screenshots and a demo GIF.
- Deploy frontend and backend.

