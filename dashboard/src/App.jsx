import { Route, BrowserRouter, Routes } from "react-router-dom"
import Layout from "./components/Layout"
import Conversations from "./pages/Conversations"
import ConversationDetail from "./pages/ConversationDetail"
import AgentQueue from "./pages/AgentQueue"
import Templates from "./pages/Templates"
import Notify from "./pages/Notify"

export default function App() {
  return (
    <BrowserRouter basename="/dashboard">
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Conversations />} />
          <Route path="/conversations/:sender" element={<ConversationDetail />} />
          <Route path="/agent-queue" element={<AgentQueue />} />
          <Route path="/templates" element={<Templates />} />
          <Route path="/notify" element={<Notify />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
