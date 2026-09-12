import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

import { get, post } from "../../api/client"
import Message from "../../components/Message"
import Spinner from "../../components/Spinner"
import { getLanguage, t } from "../../i18n"

function compatibilityTone(score) {
  if (score >= 70) return { bar: "bg-green-400", text: "text-green-400" }
  if (score >= 40) return { bar: "bg-blue-400", text: "text-blue-400" }
  return { bar: "bg-line", text: "text-ink-soft" }
}

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
    if (application.status === "accepted") return t.jobBrowse.statusAccepted
    if (application.status === "completed") return t.jobBrowse.statusCompleted
    if (application.status === "assessment") return t.jobBrowse.statusAssessment
    if (application.status === "rejected") return t.jobBrowse.statusRejected
    if (application.assessment_eligible) return t.jobBrowse.statusReadyForAssessment
    return t.jobBrowse.statusPending
  }

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
    <div>
      <h1 className="text-2xl font-extrabold text-ink">{t.jobBrowse.title}</h1>

      <Message error={error} className="mt-4" />

      {jobs.length === 0 && (
        <p className="mt-6 text-sm text-ink-soft">{t.jobBrowse.empty}</p>
      )}

      <div className="mt-6 space-y-3">
        {jobs.map((job) => {
          const application = findApplication(job.id)
          const score =
            job.compatibility_score !== null && job.compatibility_score !== undefined
              ? Math.round(job.compatibility_score)
              : null
          const tone = score !== null ? compatibilityTone(score) : null

          return (
            <div key={job.id} className="rounded-xl bg-surface p-5">
              <div className="flex items-start justify-between gap-4">
                <h2 className="font-semibold text-ink">{job.title}</h2>

                {score !== null && (
                  <div className="flex shrink-0 items-center gap-2">
                    <span className="h-1.5 w-12 overflow-hidden rounded-full bg-surface-2">
                      <span
                        className={`block h-full rounded-full ${tone.bar}`}
                        style={{ width: `${score}%` }}
                      />
                    </span>
                    <span className={`font-mono text-sm font-medium ${tone.text}`}>
                      {score}%
                    </span>
                  </div>
                )}
              </div>

              <p className="mt-1 text-sm text-ink-soft">
                {job.company_name}
                {job.location && ` · ${job.location}`}
              </p>

              {job.description && (
                <p className="mt-3 text-sm text-ink-soft">{job.description}</p>
              )}

              <p className="mt-3 text-xs text-ink-soft">
                {job.experience_years} {t.jobBrowse.experienceRequired}
                {job.education_level && ` · ${t.educationLevels[job.education_level]}`}
                {job.field && ` · ${t.fields[job.field]}`}
              </p>

              <p className="mt-1 font-mono text-xs text-ink-soft">
                {new Date(job.created_at).toLocaleDateString(
                  getLanguage() === "tr" ? "tr-TR" : "en-US"
                )}
              </p>

              {job.is_closed && (
                <p className="mt-2 text-xs text-ink-soft">{t.jobBrowse.assessmentClosed}</p>
              )}

              <div className="mt-4">
                {application ? (
                  <div className="space-y-1">
                    <p
                      className={
                        application.status === "rejected"
                          ? "text-sm text-ink-soft"
                          : "text-sm text-green-400"
                      }
                    >
                      {statusText(application)}
                    </p>

                    {application.assessment_eligible && (
                      <Link
                        to={`/candidate/assessments/${application.id}`}
                        className="text-sm font-medium text-blue-400 hover:text-blue-500"
                      >
                        {application.status === "completed"
                          ? t.assessment.viewResult
                          : t.assessment.start}{" "}
                        →
                      </Link>
                    )}
                  </div>
                ) : job.withdrawn ? (
                  <p className="text-xs text-ink-soft">{t.jobBrowse.withdrawnNotice}</p>
                ) : (
                  <button
                    type="button"
                    onClick={() => apply(job.id)}
                    disabled={pendingId === job.id}
                    className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-blue-600 disabled:opacity-50"
                  >
                    {pendingId === job.id ? t.jobBrowse.applying : t.jobBrowse.apply}
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