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

  async function handleDelete(jobId) {
    if (!window.confirm(t.jobList.deleteConfirm)) {
      return
    }

    try {
      await del(`/jobs/${jobId}`)
      setJobs(jobs.filter((job) => job.id !== jobId))
      setMessage(t.jobList.deleted)
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
          <div key={job.id} className="rounded bg-slate-800 p-4">
            <h2 className="font-medium text-white">{job.title}</h2>
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