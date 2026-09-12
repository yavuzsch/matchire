import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

import { del, get, patch } from "../../api/client"
import Message from "../../components/Message"
import { getLanguage, t } from "../../i18n"

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
      const updated = await patch(`/jobs/${jobId}/settings`, changes)
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

  const sortedJobs = [...jobs].sort(
    (a, b) => Number(!a.is_active) - Number(!b.is_active)
  )

  return (
    <div>
      <h1 className="text-2xl font-extrabold text-ink">{t.jobList.title}</h1>

      <Message error={error} info={message} className="mt-4" />

      {jobs.length === 0 && (
        <p className="mt-6 text-sm text-ink-soft">{t.jobList.empty}</p>
      )}

      <div className="mt-6 space-y-3">
        {sortedJobs.map((job) => (
          <div
            key={job.id}
            className={
              job.is_active
                ? "rounded-xl bg-surface p-5"
                : "rounded-xl bg-surface p-5 opacity-60"
            }
          >
            <div className="flex items-start justify-between gap-3">
              <h2 className="font-semibold text-ink">{job.title}</h2>
              <div className="flex shrink-0 gap-2">
                {!job.is_active && (
                  <span className="rounded-full bg-surface-2 px-2.5 py-1 text-xs text-ink-soft">
                    {t.jobList.inactive}
                  </span>
                )}
                {job.is_closed && (
                  <span className="rounded-full bg-amber-500/10 px-2.5 py-1 text-xs text-amber-400">
                    {t.jobList.closed}
                  </span>
                )}
              </div>
            </div>

            <p className="mt-1 text-sm text-ink-soft">
              {job.company_name}
              {job.location && ` · ${job.location}`}
            </p>
            <p className="mt-2 text-xs text-ink-soft">
              {job.assessment_slots} {t.jobList.slots} · {t.jobList.postedAt}:{" "}
              {new Date(job.created_at).toLocaleDateString(
                getLanguage() === "tr" ? "tr-TR" : "en-US"
              )}
            </p>

            <div className="mt-4 flex flex-wrap items-center justify-between gap-4">
              <div className="flex gap-4">
                <Link
                  to={`/employer/jobs/${job.id}/questions`}
                  className="text-sm font-medium text-blue-400 hover:text-blue-500"
                >
                  {t.jobList.manageQuestions}
                </Link>
                <Link
                  to={`/employer/jobs/${job.id}/candidates`}
                  className="text-sm font-medium text-blue-400 hover:text-blue-500"
                >
                  {t.jobList.viewCandidates}
                </Link>
              </div>

              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => updateStatus(job.id, { is_active: !job.is_active })}
                  className="rounded-lg bg-surface-2 px-3 py-1.5 text-xs font-medium text-ink-soft transition-colors hover:text-ink"
                >
                  {job.is_active ? t.jobList.deactivate : t.jobList.activate}
                </button>

                <button
                  type="button"
                  onClick={() => updateStatus(job.id, { is_closed: !job.is_closed })}
                  className="rounded-lg bg-surface-2 px-3 py-1.5 text-xs font-medium text-ink-soft transition-colors hover:text-ink"
                >
                  {job.is_closed ? t.jobList.reopen : t.jobList.close}
                </button>

                <button
                  type="button"
                  onClick={() => handleDelete(job.id)}
                  className="px-2 text-xs font-medium text-red-400 hover:text-red-500"
                >
                  {t.jobList.delete}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}