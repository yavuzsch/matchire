import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

import { del, get, patch } from "../../api/client"
import Message from "../../components/Message"
import { getLanguage, t } from "../../i18n"

function JobCard({ job, updateStatus, handleDelete }) {
  return (
    <div className="rounded-xl bg-surface p-5">
      <div className="flex items-start justify-between gap-3">
        <h2 className="font-semibold text-ink">{job.title}</h2>
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
  )
}

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

  const activeOpen = jobs.filter((job) => job.is_active && !job.is_closed)
  const activeClosed = jobs.filter((job) => job.is_active && job.is_closed)
  const inactiveOpen = jobs.filter((job) => !job.is_active && !job.is_closed)
  const inactiveClosed = jobs.filter((job) => !job.is_active && job.is_closed)

  const groups = [
    { key: "activeOpen", label: t.jobList.groupActiveOpen, items: activeOpen, dot: "bg-green-500" },
    { key: "activeClosed", label: t.jobList.groupActiveClosed, items: activeClosed, dot: "bg-blue-500" },
    { key: "inactiveOpen", label: t.jobList.groupInactiveOpen, items: inactiveOpen, dot: "bg-amber-500" },
    { key: "inactiveClosed", label: t.jobList.groupInactiveClosed, items: inactiveClosed, dot: "bg-ink-soft" },
  ]

  return (
    <div>
      <h1 className="text-2xl font-extrabold text-ink">{t.jobList.title}</h1>

      <Message error={error} info={message} className="mt-4" />

      {jobs.length === 0 && (
        <div className="mt-6">
          <p className="text-sm text-ink-soft">{t.jobList.empty}</p>
          <Link
            to="/employer/jobs/new"
            className="mt-2 inline-block text-sm font-semibold text-blue-400 hover:text-blue-500"
          >
            {t.jobList.emptyCta} →
          </Link>
        </div>
      )}

      {groups.map(
        (group) =>
          group.items.length > 0 && (
            <div key={group.key} className="mt-8 first:mt-6">
              <h2 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-ink-soft">
                <span className={`h-1.5 w-1.5 rounded-full ${group.dot}`} />
                {group.label} · {group.items.length}
              </h2>

              <div className="mt-3 space-y-3">
                {group.items.map((job) => (
                  <JobCard
                    key={job.id}
                    job={job}
                    updateStatus={updateStatus}
                    handleDelete={handleDelete}
                  />
                ))}
              </div>
            </div>
          )
      )}
    </div>
  )
}