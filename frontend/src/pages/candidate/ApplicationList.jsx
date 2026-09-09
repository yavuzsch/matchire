import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

import { del, get } from "../../api/client"
import { t } from "../../i18n"

export default function ApplicationList() {
  const [applications, setApplications] = useState([])
  const [error, setError] = useState(null)
  const [pendingId, setPendingId] = useState(null)

  useEffect(() => {
    get("/applications/mine").then(setApplications).catch(() => setApplications([]))
  }, [])

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

  async function withdraw(applicationId) {
    if (!window.confirm(t.applications.withdrawConfirm)) {
      return
    }

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
    <div className="mx-auto max-w-3xl p-8">
      <h1 className="mb-6 text-2xl font-bold text-white">{t.applications.title}</h1>

      {error && <p className="mb-4 text-sm text-red-400">{error}</p>}

      {applications.length === 0 && (
        <p className="text-slate-400">{t.applications.empty}</p>
      )}

      <div className="space-y-3">
        {applications.map((application) => {
          const job = application.job

          return (
            <div key={application.id} className="rounded bg-slate-800 p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="font-medium text-white">
                    {job ? job.title : t.applications.jobRemoved}
                  </h2>
                  {job && (
                    <p className="text-sm text-slate-400">
                      {job.company_name}
                      {job.location ? ` · ${job.location}` : ""}
                    </p>
                  )}
                </div>

                <span className="shrink-0 rounded bg-slate-700 px-2 py-1 text-xs font-medium text-emerald-400">
                  %{Math.round(application.compatibility_score)}{" "}
                  {t.jobBrowse.compatibility}
                </span>
              </div>

              {job && !job.is_active && (
                <p className="mt-2 text-xs text-amber-400">
                  {t.jobBrowse.inactive}
                </p>
              )}

              <div className="mt-3 space-y-1">
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

              {application.status !== "accepted" && (
                <button
                  type="button"
                  onClick={() => withdraw(application.id)}
                  disabled={pendingId === application.id}
                  className="mt-3 text-sm text-red-400 disabled:opacity-50"
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