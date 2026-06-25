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

  const handleLogout = () => {
    logout()
    navigate("/login")
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
              <span className="nav-icon">{item.icon}</span> {item.label}
            </Link>
          ))}
        </nav>
        <div className="user-box">
          <div className="user-email">{user?.email}</div>
          <button onClick={handleLogout}>Изход</button>
        </div>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  )
}
