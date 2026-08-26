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

      {error && <p className="mb-4 text-sm text-red-400">{error}</p>}
      {visibleJobs.length === 0 && (
        <p className="text-slate-400">{t.jobBrowse.empty}</p>
      )}

      <div className="space-y-3">
        {visibleJobs.map((job) => {
          const application = findApplication(job.id)
          const isListed = jobs.some((item) => item.id === job.id)

          return (
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
                {job.education_level
                  ? ` · ${t.educationLevels[job.education_level]}`
                  : ""}
                {job.field ? ` · ${t.fields[job.field]}` : ""}
              </p>

              <p className="mt-1 text-xs text-slate-500">
                {new Date(job.created_at).toLocaleDateString("tr-TR")}
              </p>

              {!isListed && (
                <p className="mt-2 text-xs text-amber-400">
                  {t.jobBrowse.inactive}
                </p>
              )}

              <div className="mt-3">
                {application ? (
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-green-400">
                      {t.jobBrowse.applied}
                    </span>
                    {application.interview_eligible && (
                      <Link
                        to={`/candidate/interviews/${application.id}`}
                        className="text-sm text-blue-400"
                      >
                        {t.interview.start}
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