import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

import { get, post } from "../../api/client"
import { t } from "../../i18n"

export default function JobBrowse() {
  const [jobs, setJobs] = useState([])
  const [applications, setApplications] = useState([])
  const [pendingId, setPendingId] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    get("/jobs").then(setJobs).catch(() => setJobs([]))
    get("/applications/mine").then(setApplications).catch(() => setApplications([]))
  }, [])

  function findApplication(jobId) {
    return applications.find((item) => item.job_id === jobId)
  }

  function statusText(application) {
    if (application.status === "accepted") {
      return t.jobBrowse.statusAccepted
    }

    if (application.status === "completed") {
      return t.jobBrowse.statusCompleted
    }

    if (application.status === "assessment") {
      return t.jobBrowse.statusAssessment
    }

    if (application.status === "rejected") {
      return t.jobBrowse.statusRejected
    }

    if (application.assessment_eligible) {
      return t.jobBrowse.statusReadyForAssessment
    }

    return t.jobBrowse.statusPending
  }

  const visibleJobs = [...jobs]

  applications.forEach((application) => {
    if (!application.job) {
      return
    }
    if (!visibleJobs.some((job) => job.id === application.job_id)) {
      visibleJobs.push(application.job)
    }
  })

  async function apply(jobId) {
    setError(null)
    setPendingId(jobId)

    try {
      const application = await post("/applications", { job_id: jobId })
      setApplications([...applications, application])
    } catch (err) {
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    } finally {
      setPendingId(null)
    }
  }

  return (
    <div className="mx-auto max-w-3xl p-8">
      <h1 className="mb-6 text-2xl font-bold text-white">{t.jobBrowse.title}</h1>

      {error && (
        <div className="mb-4 space-y-1">
          <p className="text-sm text-red-400">{error}</p>
          <Link to="/candidate/resume" className="text-sm text-blue-400">
            {t.jobBrowse.goToResume}
          </Link>
        </div>
      )}

      {visibleJobs.length === 0 && (
        <p className="text-slate-400">{t.jobBrowse.empty}</p>
      )}

      <div className="space-y-3">
        {visibleJobs.map((job) => {
          const application = findApplication(job.id)
          const isListed = jobs.some((item) => item.id === job.id)

          return (
            <div key={job.id} className="rounded bg-slate-800 p-4">
              <div className="flex items-start justify-between gap-3">
                <h2 className="font-medium text-white">{job.title}</h2>

                {job.compatibility_score !== null &&
                  job.compatibility_score !== undefined && (
                    <span className="shrink-0 rounded bg-slate-700 px-2 py-1 text-xs font-medium text-emerald-400">
                      %{Math.round(job.compatibility_score)} {t.jobBrowse.compatibility}
                    </span>
                  )}
              </div>

              <p className="text-sm text-slate-400">
                {job.company_name}
                {job.location ? ` · ${job.location}` : ""}
              </p>

              {job.description && (
                <p className="mt-2 text-sm text-slate-300">{job.description}</p>
              )}

              <p className="mt-2 text-xs text-slate-400">
                {job.experience_years} {t.jobBrowse.experienceRequired}
                {job.education_level
                  ? ` · ${t.educationLevels[job.education_level]}`
                  : ""}
                {job.field ? ` · ${t.fields[job.field]}` : ""}
              </p>

              <p className="mt-1 text-xs text-slate-500">
                {new Date(job.created_at).toLocaleDateString("tr-TR")}
              </p>

              {job.is_closed && (
                <p className="mt-1 text-xs text-slate-500">
                  {t.jobBrowse.assessmentClosed}
                </p>
              )}

              {!isListed && (
                <p className="mt-2 text-xs text-amber-400">
                  {t.jobBrowse.inactive}
                </p>
              )}

              <div className="mt-3">
                {application ? (
                  <div className="space-y-1">
                    <p
                      className={
                        application.status === "rejected"
                          ? "text-sm text-slate-400"
                          : "text-sm text-green-400"
                      }
                    >
                      {statusText(application)}
                    </p>

                    {application.assessment_eligible &&
                      application.status !== "completed" && (
                        <Link
                          to={`/candidate/assessments/${application.id}`}
                          className="text-sm text-blue-400"
                        >
                          {t.assessment.start}
                        </Link>
                      )}
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => apply(job.id)}
                    disabled={pendingId === job.id}
                    className="rounded bg-blue-600 px-4 py-1 text-sm text-white disabled:opacity-50"
                  >
                    {pendingId === job.id
                      ? t.jobBrowse.applying
                      : t.jobBrowse.apply}
                  </button>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}