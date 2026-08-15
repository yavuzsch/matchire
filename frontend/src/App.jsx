import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"

import Layout from "./components/Layout"
import ProtectedRoute from "./components/ProtectedRoute"
import Login from "./pages/auth/Login"
import Register from "./pages/auth/Register"
import InterviewTake from "./pages/candidate/InterviewTake"
import JobBrowse from "./pages/candidate/JobBrowse"
import ResumeForm from "./pages/candidate/ResumeForm"
import CandidateList from "./pages/employer/CandidateList"
import JobCreate from "./pages/employer/JobCreate"
import JobList from "./pages/employer/JobList"
import QuestionManage from "./pages/employer/QuestionManage"

function Protected({ role, children }) {
  return (
    <ProtectedRoute role={role}>
      <Layout>{children}</Layout>
    </ProtectedRoute>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route
          path="/employer/jobs"
          element={<Protected role="employer"><JobList /></Protected>}
        />
        <Route
          path="/employer/jobs/new"
          element={<Protected role="employer"><JobCreate /></Protected>}
        />
        <Route
          path="/employer/jobs/:jobId/questions"
          element={<Protected role="employer"><QuestionManage /></Protected>}
        />
        <Route
          path="/employer/jobs/:jobId/candidates"
          element={<Protected role="employer"><CandidateList /></Protected>}
        />

        <Route
          path="/candidate/jobs"
          element={<Protected role="candidate"><JobBrowse /></Protected>}
        />
        <Route
          path="/candidate/resume"
          element={<Protected role="candidate"><ResumeForm /></Protected>}
        />
        <Route
          path="/candidate/interviews/:applicationId"
          element={<Protected role="candidate"><InterviewTake /></Protected>}
        />

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}