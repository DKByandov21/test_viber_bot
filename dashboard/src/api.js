const API_BASE = import.meta.env.VITE_API_BASE_URL || ""

export function getToken() {
  return localStorage.getItem("token") || ""
}

export function setToken(token) {
  localStorage.setItem("token", token)
}

export function clearToken() {
  localStorage.removeItem("token")
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
      ...options.headers,
    },
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.message || `Request failed: ${response.status}`)
  }
  return data
}

export const authApi = {
  register: (payload) => request("/api/auth/register", { method: "POST", body: JSON.stringify(payload) }),
  login: (payload) => request("/api/auth/login", { method: "POST", body: JSON.stringify(payload) }),
  verify: (payload) => request("/api/auth/verify", { method: "POST", body: JSON.stringify(payload) }),
  me: () => request("/api/auth/me"),
  updateMe: (payload) => request("/api/auth/me", { method: "PUT", body: JSON.stringify(payload) }),
}

export const api = {
  listConversations: () => request("/api/conversations"),
  getConversation: (sender) => request(`/api/conversations/${encodeURIComponent(sender)}`),
  resetConversation: (sender) => request(`/api/conversations/${encodeURIComponent(sender)}`, { method: "DELETE" }),
  listSessions: (sender) => request(`/api/conversations/${encodeURIComponent(sender)}/sessions`),
  getSession: (id) => request(`/api/sessions/${id}`),
  agentQueue: () => request("/api/agent-queue"),
  listTemplates: () => request("/api/templates"),
  createTemplate: (payload) => request("/api/templates", { method: "POST", body: JSON.stringify(payload) }),
  updateTemplate: (key, payload) => request(`/api/templates/${encodeURIComponent(key)}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteTemplate: (key) => request(`/api/templates/${encodeURIComponent(key)}`, { method: "DELETE" }),
  notify: (payload) => request("/notify", { method: "POST", body: JSON.stringify(payload) }),
  notifyRaw: (message) => request("/notify/raw", { method: "POST", body: JSON.stringify(message) }),
  agentReply: (payload) => request("/agent-reply", { method: "POST", body: JSON.stringify(payload) }),
  stats: () => request("/api/stats"),
  voiceCall: (payload) => request("/api/voice/call", { method: "POST", body: JSON.stringify(payload) }),
  listUsers: () => request("/api/users"),
  updateUserRole: (id, role) => request(`/api/users/${id}`, { method: "PUT", body: JSON.stringify({ role }) }),
  deleteUser: (id) => request(`/api/users/${id}`, { method: "DELETE" }),
}

export const projectsApi = {
  list: () => request("/api/projects"),
  get: (id) => request(`/api/projects/${id}`),
  create: (payload) => request("/api/projects", { method: "POST", body: JSON.stringify(payload) }),
  update: (id, payload) => request(`/api/projects/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  remove: (id) => request(`/api/projects/${id}`, { method: "DELETE" }),

  listSprints: (projectId) => request(`/api/projects/${projectId}/sprints`),
  createSprint: (projectId, payload) => request(`/api/projects/${projectId}/sprints`, { method: "POST", body: JSON.stringify(payload) }),
  updateSprint: (id, payload) => request(`/api/sprints/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  removeSprint: (id) => request(`/api/sprints/${id}`, { method: "DELETE" }),

  listTasks: (params = {}) => {
    const query = new URLSearchParams(params).toString()
    return request(`/api/tasks${query ? `?${query}` : ""}`)
  },
  triage: () => request("/api/triage"),
  createTask: (payload) => request("/api/tasks", { method: "POST", body: JSON.stringify(payload) }),
  updateTask: (id, payload) => request(`/api/tasks/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  removeTask: (id) => request(`/api/tasks/${id}`, { method: "DELETE" }),

  listDocs: (projectId) => request(`/api/projects/${projectId}/docs`),
  getDoc: (id) => request(`/api/docs/${id}`),
  createDoc: (projectId, payload) => request(`/api/projects/${projectId}/docs`, { method: "POST", body: JSON.stringify(payload) }),
  updateDoc: (id, payload) => request(`/api/docs/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  removeDoc: (id) => request(`/api/docs/${id}`, { method: "DELETE" }),
}
