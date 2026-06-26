import { useEffect, useState } from "react"
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom"
import { useAuth } from "../auth/AuthContext"

const NAV_GROUPS = [
  {
    key: "viberbot",
    label: "Viber Bot",
    icon: "🤖",
    items: [
      { to: "/", label: "Разговори", icon: "💬" },
      { to: "/agent-queue", label: "Agent Queue", icon: "🧑‍💼" },
      { to: "/templates", label: "Templates", icon: "📄", adminOnly: true },
      { to: "/notify", label: "Изпрати Notify", icon: "📤", adminOnly: true },
    ],
  },
  {
    key: "projects",
    label: "Projects",
    icon: "🗂️",
    items: [
      { to: "/projects", label: "Проекти", icon: "📁" },
      { to: "/triage", label: "Triage", icon: "🛎️" },
    ],
  },
  {
    key: "admin",
    label: "Admin",
    icon: "🛡️",
    adminOnly: true,
    items: [
      { to: "/analytics", label: "Analytics", icon: "📊", adminOnly: true },
      { to: "/users", label: "Потребители", icon: "👥", adminOnly: true },
    ],
  },
]

function loadOpenGroups() {
  try {
    return JSON.parse(localStorage.getItem("sidebarOpenGroups")) || {}
  } catch {
    return {}
  }
}

export default function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const isAdmin = user?.role === "admin"

  const [collapsed, setCollapsed] = useState(() => localStorage.getItem("sidebarCollapsed") === "true")
  const [openGroups, setOpenGroups] = useState(loadOpenGroups)

  useEffect(() => {
    localStorage.setItem("sidebarCollapsed", collapsed)
  }, [collapsed])

  useEffect(() => {
    localStorage.setItem("sidebarOpenGroups", JSON.stringify(openGroups))
  }, [openGroups])

  // Auto-open the group containing the current route.
  useEffect(() => {
    const activeGroup = NAV_GROUPS.find((g) => g.items.some((item) => item.to === location.pathname))
    if (activeGroup && !openGroups[activeGroup.key]) {
      setOpenGroups((prev) => ({ ...prev, [activeGroup.key]: true }))
    }
  }, [location.pathname])

  const toggleGroup = (key) => {
    setOpenGroups((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  const handleLogout = () => {
    logout()
    navigate("/login")
  }

  const initial = user?.email?.[0]?.toUpperCase() || "?"
  const visibleGroups = NAV_GROUPS.filter((g) => !g.adminOnly || isAdmin)

  return (
    <div className="layout">
      <aside className={`sidebar ${collapsed ? "collapsed" : ""}`}>
        <div className="sidebar-top">
          <h1><span className="logo-dot" />{!collapsed && "Business Hub"}</h1>
          <button
            className="collapse-btn"
            onClick={() => setCollapsed((c) => !c)}
            title={collapsed ? "Разшири" : "Свий"}
          >
            {collapsed ? "»" : "«"}
          </button>
        </div>
        <nav>
          {visibleGroups.map((group) => {
            const visibleItems = group.items.filter((item) => !item.adminOnly || isAdmin)
            const isOpen = collapsed || openGroups[group.key]
            return (
              <div key={group.key} className="nav-group">
                <button
                  className="nav-group-header"
                  onClick={() => toggleGroup(group.key)}
                  title={collapsed ? group.label : undefined}
                >
                  <span className="nav-icon">{group.icon}</span>
                  {!collapsed && (
                    <>
                      <span>{group.label}</span>
                      <span className={`chevron ${isOpen ? "open" : ""}`}>▾</span>
                    </>
                  )}
                </button>
                {isOpen && (
                  <div className="nav-subitems">
                    {visibleItems.map((item) => (
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
                  </div>
                )}
              </div>
            )
          })}
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
