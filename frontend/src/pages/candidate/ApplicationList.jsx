import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

import { del, get } from "../../api/client"
import Message from "../../components/Message"
import { t } from "../../i18n"

function compatibilityTone(score) {
  if (score >= 70) return "text-green-400"
  if (score >= 40) return "text-blue-400"
  return "text-ink-soft"
}

function isAssessmentPending(status) {
  return status === "pending" || status === "assessment"
}

export default function ApplicationList() {
  const [applications, setApplications] = useState([])
  const [error, setError] = useState(null)
  const [pendingId, setPendingId] = useState(null)

  useEffect(() => {
    get("/applications/mine").then(setApplications).catch(() => setApplications([]))
  }, [])

  function statusText(application) {
    if (application.status === "accepted") return t.jobBrowse.statusAccepted
    if (application.status === "completed") return t.jobBrowse.statusCompleted
    if (application.status === "assessment") return t.jobBrowse.statusAssessment
    if (application.status === "rejected") return t.jobBrowse.statusRejected
    if (application.assessment_eligible) return t.jobBrowse.statusReadyForAssessment
    return t.jobBrowse.statusPending
  }

  async function withdraw(applicationId) {
    if (!window.confirm(t.applications.withdrawConfirm)) return

    setError(null)
    setPendingId(applicationId)

    try {
      await del(`/applications/${applicationId}`)
      setApplications(applications.filter((item) => item.id !== applicationId))
    } catch (err) {
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    } finally {
      setPendingId(null)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-extrabold text-ink">{t.applications.title}</h1>

      <Message error={error} className="mt-4" />

      {applications.length === 0 && (
        <div className="mt-6">
          <p className="text-sm text-ink-soft">{t.applications.empty}</p>
          <Link
            to="/candidate/jobs"
            className="mt-2 inline-block text-sm font-semibold text-blue-400 hover:text-blue-500"
          >
            {t.applications.emptyCta} →
          </Link>
        </div>
      )}

      <div className="mt-6 space-y-3">
        {applications.map((application) => {
          const job = application.job
          const score = Math.round(application.compatibility_score)

          return (
            <div key={application.id} className="rounded-xl bg-surface p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="font-semibold text-ink">
                    {job ? job.title : t.applications.jobRemoved}
                  </h2>
                  {job && (
                    <p className="mt-1 text-sm text-ink-soft">
                      {job.company_name}
                      {job.location && ` · ${job.location}`}
                    </p>
                  )}
                </div>

                <div className="shrink-0 text-right">
                  <span className={`font-mono text-sm font-medium ${compatibilityTone(score)}`}>
                    {score}%
                  </span>
                  <p className="text-[10px] text-ink-soft">{t.applications.scoreAtApply}</p>
                </div>
              </div>

              {job && !job.is_active && (
                <p className="mt-2 text-xs text-ink-soft">{t.jobBrowse.inactive}</p>
              )}

              <div className="mt-4 space-y-1">
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
                    {isAssessmentPending(application.status)
                      ? t.assessment.start
                      : t.assessment.viewResult}{" "}
                    →
                  </Link>
                )}
              </div>

              {application.status !== "accepted" && (
                <button
                  type="button"
                  onClick={() => withdraw(application.id)}
                  disabled={pendingId === application.id}
                  className="mt-4 text-sm font-medium text-red-400 transition-colors hover:text-red-500 disabled:opacity-50"
                >
                  {pendingId === application.id
                    ? t.applications.withdrawing
                    : t.applications.withdraw}
                </button>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}