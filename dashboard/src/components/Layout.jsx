import { useEffect, useState } from "react"
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom"
import { useAuth } from "../auth/AuthContext"

const NAV_ITEMS = [
  { to: "/", label: "Разговори", icon: "💬" },
  { to: "/agent-queue", label: "Agent Queue", icon: "🧑‍💼" },
  { to: "/templates", label: "Templates", icon: "📄" },
  { to: "/notify", label: "Изпрати Notify", icon: "📤" },
]

export default function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const [collapsed, setCollapsed] = useState(() => localStorage.getItem("sidebarCollapsed") === "true")

  useEffect(() => {
    localStorage.setItem("sidebarCollapsed", collapsed)
  }, [collapsed])

  const handleLogout = () => {
    logout()
    navigate("/login")
  }

  const initial = user?.email?.[0]?.toUpperCase() || "?"

  return (
    <div className="layout">
      <aside className={`sidebar ${collapsed ? "collapsed" : ""}`}>
        <div className="sidebar-top">
          <h1><span className="logo-dot" />{!collapsed && "Viber Bot"}</h1>
          <button
            className="collapse-btn"
            onClick={() => setCollapsed((c) => !c)}
            title={collapsed ? "Разшири" : "Свий"}
          >
            {collapsed ? "»" : "«"}
          </button>
        </div>
        <nav>
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className={location.pathname === item.to ? "active" : ""}
              title={collapsed ? item.label : undefined}
            >
              <span className="nav-icon">{item.icon}</span>
              {!collapsed && <span>{item.label}</span>}
            </Link>
          ))}
        </nav>
        <div className="user-box">
          <Link
            to="/settings"
            className={`user-row ${location.pathname === "/settings" ? "active" : ""}`}
            title={collapsed ? user?.email : undefined}
          >
            <span className="avatar">{initial}</span>
            {!collapsed && <span className="user-email">{user?.email}</span>}
          </Link>
          <button className="secondary" onClick={handleLogout} title={collapsed ? "Изход" : undefined}>
            {collapsed ? "⎋" : "Изход"}
          </button>
        </div>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  )
}
