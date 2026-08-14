import { useEffect, useState } from "react"

import { get, post } from "../../api/client"
import { t } from "../../i18n"

export default function JobBrowse() {
  const [jobs, setJobs] = useState([])
  const [appliedIds, setAppliedIds] = useState([])
  const [pendingId, setPendingId] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    get("/jobs").then(setJobs).catch(() => setJobs([]))
    get("/applications/mine")
      .then((applications) => setAppliedIds(applications.map((item) => item.job_id)))
      .catch(() => setAppliedIds([]))
  }, [])

  async function apply(jobId) {
    setError(null)
    setPendingId(jobId)

    try {
      await post("/applications", { job_id: jobId })
      setAppliedIds([...appliedIds, jobId])
    } catch (err) {
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    } finally {
      setPendingId(null)
    }
  }

  return (
    <div className="mx-auto max-w-3xl p-8">
      <h1 className="mb-6 text-2xl font-bold text-white">{t.jobBrowse.title}</h1>

      {error && <p className="mb-4 text-sm text-red-400">{error}</p>}
      {jobs.length === 0 && <p className="text-slate-400">{t.jobBrowse.empty}</p>}

      <div className="space-y-3">
        {jobs.map((job) => (
          <div key={job.id} className="rounded bg-slate-800 p-4">
            <h2 className="font-medium text-white">{job.title}</h2>
            <p className="text-sm text-slate-400">
              {job.company_name}
              {job.location ? ` · ${job.location}` : ""}
            </p>

            {job.description && (
              <p className="mt-2 text-sm text-slate-300">{job.description}</p>
            )}

            <p className="mt-2 text-xs text-slate-400">
              {job.experience_years} {t.jobBrowse.experienceRequired}
              {job.education_level ? ` · ${t.educationLevels[job.education_level]}` : ""}
              {job.field ? ` · ${t.fields[job.field]}` : ""}
            </p>

            <div className="mt-3">
              {appliedIds.includes(job.id) ? (
                <span className="text-sm text-green-400">{t.jobBrowse.applied}</span>
              ) : (
                <button
                  type="button"
                  onClick={() => apply(job.id)}
                  disabled={pendingId === job.id}
                  className="rounded bg-blue-600 px-4 py-1 text-sm text-white disabled:opacity-50"
                >
                  {pendingId === job.id ? t.jobBrowse.applying : t.jobBrowse.apply}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}