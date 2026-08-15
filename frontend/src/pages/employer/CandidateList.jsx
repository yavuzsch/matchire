import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"

import { get } from "../../api/client"
import ScoreBadge from "../../components/ScoreBadge"
import { t } from "../../i18n"

export default function CandidateList() {
  const { jobId } = useParams()

  const [candidates, setCandidates] = useState([])
  const [openId, setOpenId] = useState(null)
  const [reviews, setReviews] = useState({})
  const [error, setError] = useState(null)

  useEffect(() => {
    get(`/applications/job/${jobId}`)
      .then(setCandidates)
      .catch((err) => setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR))
  }, [jobId])

  async function toggleAnswers(applicationId) {
    if (openId === applicationId) {
      setOpenId(null)
      return
    }

    setOpenId(applicationId)

    if (reviews[applicationId]) {
      return
    }

    try {
      const data = await get(`/interviews/applications/${applicationId}/review`)
      setReviews({ ...reviews, [applicationId]: data })
    } catch (err) {
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    }
  }

  return (
    <div className="mx-auto max-w-3xl p-8">
      <Link to="/employer/jobs" className="text-sm text-blue-400">
        {t.candidates.back}
      </Link>

      <h1 className="mb-6 mt-2 text-2xl font-bold text-white">
        {t.candidates.title}
      </h1>

      {error && <p className="mb-4 text-sm text-red-400">{error}</p>}
      {candidates.length === 0 && (
        <p className="text-slate-400">{t.candidates.empty}</p>
      )}

      <div className="space-y-3">
        {candidates.map((candidate, index) => (
          <div key={candidate.application_id} className="rounded bg-slate-800 p-4">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="font-medium text-white">
                  {index + 1}. {candidate.full_name}
                </h2>
                <p className="text-sm text-slate-400">{candidate.email}</p>
              </div>
            </div>

            <div className="mt-3 flex flex-wrap gap-2">
              <ScoreBadge
                label={t.candidates.compatibility}
                value={candidate.compatibility_score}
              />
              <ScoreBadge
                label={t.candidates.interview}
                value={candidate.interview_score}
              />
              <ScoreBadge
                label={t.candidates.total}
                value={candidate.total_score}
              />
            </div>

            <button
              type="button"
              onClick={() => toggleAnswers(candidate.application_id)}
              className="mt-3 text-sm text-blue-400"
            >
              {openId === candidate.application_id
                ? t.candidates.hideAnswers
                : t.candidates.showAnswers}
            </button>

            {openId === candidate.application_id && (
              <div className="mt-3 space-y-3">
                {(reviews[candidate.application_id] || []).length === 0 ? (
                  <p className="text-sm text-slate-400">
                    {t.candidates.noAnswers}
                  </p>
                ) : (
                  reviews[candidate.application_id].map((item, itemIndex) => (
                    <div key={itemIndex} className="rounded bg-slate-900 p-3">
                      <p className="text-sm text-slate-300">
                        {item.question_text}
                      </p>
                      <p className="mt-1 text-sm text-white">
                        {item.answer_text}
                      </p>
                      <p
                        className={
                          item.is_correct
                            ? "mt-1 text-xs text-green-400"
                            : "mt-1 text-xs text-red-400"
                        }
                      >
                        {item.is_correct
                          ? t.candidates.correct
                          : t.candidates.incorrect}{" "}
                        · {item.score}
                      </p>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}