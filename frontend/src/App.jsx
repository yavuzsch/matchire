import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"

import ProtectedRoute from "./components/ProtectedRoute"
import Login from "./pages/auth/Login"
import Register from "./pages/auth/Register"

function EmployerHome() {
  return <div className="p-8 text-white">İşveren paneli</div>
}

function CandidateHome() {
  return <div className="p-8 text-white">Aday paneli</div>
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-900">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route
            path="/employer"
            element={
              <ProtectedRoute role="employer">
                <EmployerHome />
              </ProtectedRoute>
            }
          />

          <Route
            path="/candidate"
            element={
              <ProtectedRoute role="candidate">
                <CandidateHome />
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}