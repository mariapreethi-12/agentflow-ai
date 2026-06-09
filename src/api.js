const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `AgentFlow API request failed: ${response.status}`);
  }

  return response.json();
}

export const agentFlowApi = {
  health() {
    return request("/health");
  },
  async listProjects() {
    return request("/projects");
  },
  async createProject(project) {
    const created = await request("/projects", {
      method: "POST",
      body: JSON.stringify(toProjectCreate(project)),
    });
    return fromApiProject(created);
  },
  async getProject(projectId) {
    const project = await request(`/projects/${projectId}`);
    return fromApiProject(project);
  },
  async updateProject(projectId, project) {
    const updated = await request(`/projects/${projectId}`, {
      method: "PATCH",
      body: JSON.stringify(toProjectUpdate(project)),
    });
    return fromApiProject(updated);
  },
  async approveStage(projectId, stage, note) {
    const updated = await request(`/projects/${projectId}/approve`, {
      method: "POST",
      body: JSON.stringify({ stage, note }),
    });
    return fromApiProject(updated);
  },
};

export function fromApiProject(project) {
  return {
    backendProjectId: project.id,
    id: project.id,
    name: project.name,
    idea: project.idea,
    answers: project.answers || {},
    activeStage: project.active_stage,
    approvals: Object.fromEntries(
      Object.entries(project.approvals || {}).map(([stage, approval]) => [
        stage,
        {
          approved: approval.approved,
          approvedAt: approval.approved_at,
          note: approval.note,
        },
      ])
    ),
    artifacts: Object.fromEntries(
      Object.entries(project.artifacts || {}).map(([key, artifact]) => [
        key,
        {
          schema: artifact.schema_name,
          title: artifact.title,
          score: artifact.score,
          generatedAt: artifact.generated_at,
          data: artifact.data,
        },
      ])
    ),
    createdAt: project.created_at,
    updatedAt: project.updated_at,
  };
}

function toProjectCreate(project) {
  return {
    name: project.name,
    idea: project.idea,
    answers: project.answers,
  };
}

function toProjectUpdate(project) {
  return {
    name: project.name,
    idea: project.idea,
    answers: project.answers,
    active_stage: project.activeStage,
  };
}
