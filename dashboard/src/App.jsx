import { Route, BrowserRouter, Routes } from "react-router-dom"
import { AuthProvider } from "./auth/AuthContext"
import ProtectedRoute from "./auth/ProtectedRoute"
import AdminRoute from "./auth/AdminRoute"
import Layout from "./components/Layout"
import Login from "./pages/Login"
import Register from "./pages/Register"
import Conversations from "./pages/Conversations"
import ConversationDetail from "./pages/ConversationDetail"
import SessionDetail from "./pages/SessionDetail"
import AgentQueue from "./pages/AgentQueue"
import Templates from "./pages/Templates"
import Notify from "./pages/Notify"
import Settings from "./pages/Settings"
import Users from "./pages/Users"
import Analytics from "./pages/Analytics"
import Projects from "./pages/Projects"
import ProjectDetail from "./pages/ProjectDetail"
import Triage from "./pages/Triage"
import Voice from "./pages/Voice"

export default function App() {
  return (
    <BrowserRouter basename="/dashboard">
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route path="/" element={<Conversations />} />
              <Route path="/conversations/:sender" element={<ConversationDetail />} />
              <Route path="/conversations/:sender/sessions/:id" element={<SessionDetail />} />
              <Route path="/agent-queue" element={<AgentQueue />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/projects" element={<Projects />} />
              <Route path="/projects/:id" element={<ProjectDetail />} />
              <Route path="/triage" element={<Triage />} />
              <Route element={<AdminRoute />}>
                <Route path="/templates" element={<Templates />} />
                <Route path="/notify" element={<Notify />} />
                <Route path="/voice" element={<Voice />} />
                <Route path="/users" element={<Users />} />
                <Route path="/analytics" element={<Analytics />} />
              </Route>
            </Route>
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
