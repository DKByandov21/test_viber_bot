import { Route, BrowserRouter, Routes } from "react-router-dom"
import { AuthProvider } from "./auth/AuthContext"
import ProtectedRoute from "./auth/ProtectedRoute"
import Layout from "./components/Layout"
import Login from "./pages/Login"
import Register from "./pages/Register"
import Conversations from "./pages/Conversations"
import ConversationDetail from "./pages/ConversationDetail"
import AgentQueue from "./pages/AgentQueue"
import Templates from "./pages/Templates"
import Notify from "./pages/Notify"
import Settings from "./pages/Settings"

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
              <Route path="/agent-queue" element={<AgentQueue />} />
              <Route path="/templates" element={<Templates />} />
              <Route path="/notify" element={<Notify />} />
              <Route path="/settings" element={<Settings />} />
            </Route>
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
