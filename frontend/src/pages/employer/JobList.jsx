import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

import { del, get } from "../../api/client"
import { t } from "../../i18n"

export default function JobList() {
  const [jobs, setJobs] = useState([])
  const [message, setMessage] = useState(null)

  useEffect(() => {
    get("/jobs/mine").then(setJobs).catch(() => setJobs([]))
  }, [])

  async function handleArchive(jobId) {
    if (!window.confirm(t.jobList.archiveConfirm)) {
      return
    }

    try {
      await del(`/jobs/${jobId}`)
      setJobs(
        jobs.map((job) =>
          job.id === jobId ? { ...job, is_active: false } : job
        )
      )
      setMessage(t.jobList.archived)
    } catch (err) {
      setMessage(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    }
  }

  return (
    <div className="mx-auto max-w-3xl p-8">
      <h1 className="mb-6 text-2xl font-bold text-white">{t.jobList.title}</h1>

      {message && <p className="mb-4 text-sm text-green-400">{message}</p>}
      {jobs.length === 0 && <p className="text-slate-400">{t.jobList.empty}</p>}

      <div className="space-y-3">
        {jobs.map((job) => (
          <div
            key={job.id}
            className={
              job.is_active
                ? "rounded bg-slate-800 p-4"
                : "rounded bg-slate-800 p-4 opacity-60"
            }
          >
            <div className="flex items-start justify-between gap-3">
              <h2 className="font-medium text-white">{job.title}</h2>
              {!job.is_active && (
                <span className="rounded bg-slate-700 px-2 py-1 text-xs text-slate-300">
                  {t.jobList.inactive}
                </span>
              )}
            </div>

            <p className="text-sm text-slate-400">
              {job.company_name}
              {job.location ? ` · ${job.location}` : ""}
            </p>
            <p className="mt-1 text-xs text-slate-400">
              {job.interview_slots} {t.jobList.slots}
            </p>

            <div className="mt-3 flex items-center gap-4">
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
              {job.is_active && (
                <button
                  type="button"
                  onClick={() => handleArchive(job.id)}
                  className="text-sm text-red-400"
                >
                  {t.jobList.archive}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}