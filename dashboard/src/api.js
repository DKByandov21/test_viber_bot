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
  agentQueue: () => request("/api/agent-queue"),
  listTemplates: () => request("/api/templates"),
  createTemplate: (payload) => request("/api/templates", { method: "POST", body: JSON.stringify(payload) }),
  updateTemplate: (key, payload) => request(`/api/templates/${encodeURIComponent(key)}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteTemplate: (key) => request(`/api/templates/${encodeURIComponent(key)}`, { method: "DELETE" }),
  notify: (payload) => request("/notify", { method: "POST", body: JSON.stringify(payload) }),
  agentReply: (payload) => request("/agent-reply", { method: "POST", body: JSON.stringify(payload) }),
}
