const API_BASE = import.meta.env.VITE_API_BASE_URL || ""

export function getApiKey() {
  return localStorage.getItem("apiKey") || ""
}

export function setApiKey(key) {
  localStorage.setItem("apiKey", key)
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": getApiKey(),
      ...options.headers,
    },
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.message || `Request failed: ${response.status}`)
  }
  return data
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
