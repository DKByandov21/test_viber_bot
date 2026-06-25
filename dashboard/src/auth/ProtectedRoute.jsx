import { Navigate, Outlet } from "react-router-dom"
import { useAuth } from "./AuthContext"

export default function ProtectedRoute() {
  const { user, loading } = useAuth()

  if (loading) return <p className="page-loading">Зареждане...</p>
  if (!user) return <Navigate to="/login" replace />

  return <Outlet />
}
