import { Navigate } from "react-router-dom"

export default function ProtectedRoute({ role, children }) {
  const token = localStorage.getItem("token")
  const userRole = localStorage.getItem("role")

  if (!token) {
    return <Navigate to="/login" replace />
  }

  if (role && userRole !== role) {
    return (
      <Navigate
        to={userRole === "employer" ? "/employer/jobs" : "/candidate/jobs"}
        replace
      />
    )
  }

  return children
}