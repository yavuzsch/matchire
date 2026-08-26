import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

import { del, get, patch } from "../../api/client"
import { t } from "../../i18n"

export default function JobList() {
  const [jobs, setJobs] = useState([])
  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    get("/jobs/mine").then(setJobs).catch(() => setJobs([]))
  }, [])

  async function updateStatus(jobId, changes) {
    setError(null)
    setMessage(null)

    try {
      const updated = await patch(`/jobs/${jobId}/status`, changes)
      setJobs(jobs.map((job) => (job.id === jobId ? updated : job)))
      setMessage(t.jobList.statusUpdated)
    } catch (err) {
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    }
  }

  async function handleDelete(jobId) {
    if (!window.confirm(t.jobList.deleteConfirm)) {
      return
    }

    setError(null)
    setMessage(null)

    try {
      await del(`/jobs/${jobId}`)
      setJobs(jobs.filter((job) => job.id !== jobId))
      setMessage(t.jobList.deleted)
    } catch (err) {
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    }
  }

  return (
    <div className="mx-auto max-w-3xl p-8">
      <h1 className="mb-6 text-2xl font-bold text-white">{t.jobList.title}</h1>

      {message && <p className="mb-4 text-sm text-green-400">{message}</p>}
      {error && <p className="mb-4 text-sm text-red-400">{error}</p>}
      {jobs.length === 0 && <p className="text-slate-400">{t.jobList.empty}</p>}

      <div className="space-y-3">
        {jobs.map((job) => (
          <div
            key={job.id}
            className={
              job.is_active && !job.is_closed
                ? "rounded bg-slate-800 p-4"
                : "rounded bg-slate-800 p-4 opacity-60"
            }
          >
            <div className="flex items-start justify-between gap-3">
              <h2 className="font-medium text-white">{job.title}</h2>
              <div className="flex gap-2">
                {!job.is_active && (
                  <span className="rounded bg-slate-700 px-2 py-1 text-xs text-slate-300">
                    {t.jobList.inactive}
                  </span>
                )}
                {job.is_closed && (
                  <span className="rounded bg-red-900 px-2 py-1 text-xs text-red-300">
                    {t.jobList.closed}
                  </span>
                )}
              </div>
            </div>

            <p className="text-sm text-slate-400">
              {job.company_name}
              {job.location ? ` · ${job.location}` : ""}
            </p>
            <p className="mt-1 text-xs text-slate-400">
              {job.assessment_slots} {t.jobList.slots} · {t.jobList.postedAt}:{" "}
              {new Date(job.created_at).toLocaleDateString("tr-TR")}
            </p>

            <div className="mt-3 flex flex-wrap items-center gap-4">
              <Link
                to={`/employer/jobs/${job.id}/questions`}
                className="text-sm text-blue-400"
              >
                {t.jobList.manageQuestions}
              </Link>
              <Link
                to={`/employer/jobs/${job.id}/candidates`}
                className="text-sm text-blue-400"
              >
                {t.jobList.viewCandidates}
              </Link>

              <button
                type="button"
                onClick={() => updateStatus(job.id, { is_active: !job.is_active })}
                className="text-sm text-amber-400"
              >
                {job.is_active ? t.jobList.deactivate : t.jobList.activate}
              </button>

              <button
                type="button"
                onClick={() => updateStatus(job.id, { is_closed: !job.is_closed })}
                className="text-sm text-amber-400"
              >
                {job.is_closed ? t.jobList.reopen : t.jobList.close}
              </button>

              <button
                type="button"
                onClick={() => handleDelete(job.id)}
                className="text-sm text-red-400"
              >
                {t.jobList.delete}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}