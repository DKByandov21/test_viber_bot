import { useState } from "react"
import { Link, Outlet, useLocation } from "react-router-dom"
import { getApiKey, setApiKey } from "../api"

const NAV_ITEMS = [
  { to: "/", label: "Разговори" },
  { to: "/agent-queue", label: "Agent Queue" },
  { to: "/templates", label: "Templates" },
  { to: "/notify", label: "Изпрати Notify" },
]

export default function Layout() {
  const location = useLocation()
  const [keyInput, setKeyInput] = useState(getApiKey())

  const saveKey = () => {
    setApiKey(keyInput.trim())
    window.location.reload()
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <h1>Viber Bot</h1>
        <nav>
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className={location.pathname === item.to ? "active" : ""}
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="api-key-box">
          <label>X-API-Key</label>
          <input
            type="password"
            value={keyInput}
            onChange={(e) => setKeyInput(e.target.value)}
            placeholder="API key"
          />
          <button onClick={saveKey}>Запази</button>
        </div>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  )
}
