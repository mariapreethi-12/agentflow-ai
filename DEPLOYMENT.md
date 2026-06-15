# AgentFlow Deployment

This repo is prepared for a simple free portfolio deployment:

- Backend API: Render
- Database: SQLite on Render's temporary filesystem
- Frontend: Vercel

Do not commit `.env` or your OpenAI API key.

## 1. Deploy Backend On Render

1. Push the latest `main` branch to GitHub.
2. In Render, create a new Blueprint from this repo.
3. Render should detect `render.yaml`.
4. Set these backend environment variables:

```text
OPENAI_API_KEY=your_new_secret_key
OPENAI_MODEL=gpt-4o-mini
FRONTEND_ORIGINS=https://your-vercel-app.vercel.app
```

`DATABASE_URL` is set to `sqlite:////tmp/agentflow.db` in `render.yaml` to avoid paid database setup. This is enough for a portfolio demo, but project data can reset when the free service restarts.

After deploy, verify:

```text
https://your-render-api.onrender.com/health
https://your-render-api.onrender.com/docs
```

## 2. Deploy Frontend On Vercel

1. Import the same GitHub repo in Vercel.
2. Use the repo root as the frontend project root.
3. Vercel should use:

```text
Build Command: npm run build
Output Directory: dist
```

4. Add this Vercel environment variable:

```text
VITE_API_BASE_URL=https://your-render-api.onrender.com
```

5. Deploy.

## 3. Update Render CORS

After Vercel gives you the final frontend URL, go back to Render and set:

```text
FRONTEND_ORIGINS=https://your-vercel-app.vercel.app
```

Redeploy the backend.

## Demo Notes

The deployed app is the main AgentFlow platform: multi-agent workflow, human approval gates, chat, generated files, and persisted projects.

`Run app` launches a generated app on a local machine by starting a child FastAPI server on a local port. That is perfect for the laptop demo, but most hosted platforms do not expose random child-process ports publicly. For deployment, use the hosted AgentFlow workflow as the portfolio demo, and use local mode when you want to show the generated app actually running.

For a production version, switch `DATABASE_URL` to a managed PostgreSQL provider such as Render Postgres or Supabase.
