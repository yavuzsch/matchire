import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"

import ProtectedRoute from "./components/ProtectedRoute"
import { t } from "./i18n"
import Login from "./pages/auth/Login"
import Register from "./pages/auth/Register"
import ResumeForm from "./pages/candidate/ResumeForm"
import JobCreate from "./pages/employer/JobCreate"
import JobBrowse from "./pages/candidate/JobBrowse"
import JobList from "./pages/employer/JobList"
import QuestionManage from "./pages/employer/QuestionManage"
import InterviewTake from "./pages/candidate/InterviewTake"

function EmployerHome() {
  return (
    <div className="p-8 text-white">
      <h1 className="mb-4 text-xl font-bold">{t.home.employerPanel}</h1>
      <div className="flex gap-4">
        <a href="/employer/jobs/new" className="text-blue-400">
          {t.home.newJob}
        </a>
        <a href="/employer/jobs" className="text-blue-400">
          {t.jobList.title}
        </a>
      </div>
    </div>
  )
}

function CandidateHome() {
  return (
    <div className="p-8 text-white">
      <h1 className="mb-4 text-xl font-bold">{t.home.candidatePanel}</h1>
      <div className="flex gap-4">
        <a href="/candidate/resume" className="text-blue-400">
          {t.home.myResume}
        </a>
        <a href="/candidate/jobs" className="text-blue-400">
          {t.jobBrowse.title}
        </a>
      </div>
    </div>
  )
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
            path="/employer/jobs/new"
            element={
              <ProtectedRoute role="employer">
                <JobCreate />
              </ProtectedRoute>
            }
          />

          <Route
            path="/employer/jobs"
            element={
              <ProtectedRoute role="employer">
                <JobList />
              </ProtectedRoute>
            }
          />

          <Route
            path="/employer/jobs/:jobId/questions"
            element={
              <ProtectedRoute role="employer">
                <QuestionManage />
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

          <Route
            path="/candidate/resume"
            element={
              <ProtectedRoute role="candidate">
                <ResumeForm />
              </ProtectedRoute>
            }
          />

          <Route
            path="/candidate/jobs"
            element={
              <ProtectedRoute role="candidate">
                <JobBrowse />
              </ProtectedRoute>
            }
          />

          <Route
            path="/candidate/interviews/:applicationId"
            element={
              <ProtectedRoute role="candidate">
                <InterviewTake />
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}