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
  listProjects() {
    return request("/projects");
  },
  createProject(project) {
    return request("/projects", {
      method: "POST",
      body: JSON.stringify(project),
    });
  },
  getProject(projectId) {
    return request(`/projects/${projectId}`);
  },
  updateProject(projectId, project) {
    return request(`/projects/${projectId}`, {
      method: "PATCH",
      body: JSON.stringify(project),
    });
  },
  approveStage(projectId, stage, note) {
    return request(`/projects/${projectId}/approve`, {
      method: "POST",
      body: JSON.stringify({ stage, note }),
    });
  },
};
