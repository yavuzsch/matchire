import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"

import { get, patch } from "../../api/client"
import Message from "../../components/Message"
import ScoreBadge from "../../components/ScoreBadge"
import { t } from "../../i18n"

export default function CandidateList() {
  const { jobId } = useParams()

  const [candidates, setCandidates] = useState([])
  const [openId, setOpenId] = useState(null)
  const [reviews, setReviews] = useState({})
  const [error, setError] = useState(null)
  const [message, setMessage] = useState(null)

  useEffect(() => {
    get(`/applications/job/${jobId}`)
      .then(setCandidates)
      .catch((err) => setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR))
  }, [jobId])

  const sortedCandidates = [...candidates].sort((a, b) => {
    const score = (c) => {
      if (c.status === "withdrawn") return 2
      if (c.status === "rejected") return 1
      return 0
    }
    return score(a) - score(b)
  })

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
      const data = await get(`/assessments/applications/${applicationId}/review`)
      setReviews({ ...reviews, [applicationId]: data })
    } catch (err) {
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    }
  }

  async function updateStatus(applicationId, status) {
    if (status === "rejected" && !window.confirm(t.candidates.rejectConfirm)) {
      return
    }

    setError(null)
    setMessage(null)

    try {
      const updated = await patch(`/applications/${applicationId}/status`, {
        status,
      })

      setCandidates(
        candidates.map((item) =>
          item.application_id === applicationId ? updated : item
        )
      )
      setMessage(t.candidates.statusUpdated)
    } catch (err) {
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    }
  }

  return (
    <div>
      <Link to="/employer/jobs" className="text-sm font-medium text-blue-400 hover:text-blue-500">
        ← {t.candidates.back}
      </Link>

      <h1 className="mt-2 text-2xl font-extrabold text-ink">
        {t.candidates.title}
      </h1>

      <Message error={error} info={message} className="mt-4" />

      {candidates.length === 0 && (
        <p className="mt-6 text-sm text-ink-soft">{t.candidates.empty}</p>
      )}

      <div className="mt-6 space-y-3">
        {sortedCandidates.map((candidate, index) => (
          <div
            key={candidate.application_id}
            className={
              candidate.status === "rejected" || candidate.status === "withdrawn"
                ? "rounded-xl bg-surface p-5 opacity-60"
                : "rounded-xl bg-surface p-5"
            }
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2 className="font-semibold text-ink">
                  {index + 1}. {candidate.full_name}
                </h2>
                <p className="text-sm text-ink-soft">{candidate.email}</p>
              </div>

              {candidate.status === "rejected" && (
                <span className="shrink-0 rounded-full bg-surface-2 px-2.5 py-1 text-xs text-ink-soft">
                  {t.candidates.rejected}
                </span>
              )}

              {candidate.status === "withdrawn" && (
                <span className="shrink-0 rounded-full bg-surface-2 px-2.5 py-1 text-xs text-ink-soft">
                  {t.candidates.withdrawn}
                </span>
              )}

              {candidate.status === "accepted" && (
                <span className="shrink-0 rounded-full bg-green-500/10 px-2.5 py-1 text-xs text-green-400">
                  {t.candidates.accepted}
                </span>
              )}
            </div>

            <div className="mt-3 flex flex-wrap gap-2">
              <ScoreBadge
                label={t.candidates.compatibility}
                value={candidate.compatibility_score}
              />
              <ScoreBadge
                label={t.candidates.assessment}
                value={candidate.assessment_score}
              />
              <ScoreBadge
                label={t.candidates.total}
                value={candidate.total_score}
              />
            </div>

            {candidate.project_summary && (
              <div className="mt-3">
                <p className="text-xs text-ink-soft">
                  {t.candidates.projectSummary}
                </p>
                <p className="mt-1 text-sm text-ink-soft">
                  {candidate.project_summary}
                </p>
              </div>
            )}

            <div className="mt-4 flex flex-wrap items-center justify-between gap-4">
              <button
                type="button"
                onClick={() => toggleAnswers(candidate.application_id)}
                className="text-sm font-medium text-blue-400 hover:text-blue-500"
              >
                {openId === candidate.application_id
                  ? t.candidates.hideAnswers
                  : t.candidates.showAnswers}
              </button>

              <div className="flex items-center gap-3">
                {candidate.status === "rejected" && (
                  <button
                    type="button"
                    onClick={() =>
                      updateStatus(candidate.application_id, "pending")
                    }
                    className="rounded-lg bg-surface-2 px-3 py-1.5 text-xs font-medium text-ink-soft transition-colors hover:text-ink"
                  >
                    {t.candidates.undoReject}
                  </button>
                )}

                {candidate.status === "accepted" && (
                  <button
                    type="button"
                    onClick={() =>
                      updateStatus(candidate.application_id, "pending")
                    }
                    className="rounded-lg bg-surface-2 px-3 py-1.5 text-xs font-medium text-ink-soft transition-colors hover:text-ink"
                  >
                    {t.candidates.undoAccept}
                  </button>
                )}

                {candidate.status === "completed" && (
                  <>
                    <button
                      type="button"
                      onClick={() =>
                        updateStatus(candidate.application_id, "accepted")
                      }
                      className="rounded-lg bg-green-500 px-3 py-1.5 text-xs font-semibold text-white transition-colors hover:bg-green-600"
                    >
                      {t.candidates.accept}
                    </button>
                    <button
                      type="button"
                      onClick={() =>
                        updateStatus(candidate.application_id, "rejected")
                      }
                      className="px-2 text-xs font-medium text-red-400 hover:text-red-500"
                    >
                      {t.candidates.reject}
                    </button>
                  </>
                )}

                {(candidate.status === "pending" ||
                  candidate.status === "assessment") && (
                  <button
                    type="button"
                    onClick={() =>
                      updateStatus(candidate.application_id, "rejected")
                    }
                    className="px-2 text-xs font-medium text-red-400 hover:text-red-500"
                  >
                    {t.candidates.reject}
                  </button>
                )}
              </div>
            </div>

            {openId === candidate.application_id && (
              <div className="mt-4 space-y-3 border-t border-line pt-4">
                {(reviews[candidate.application_id] || []).length === 0 ? (
                  <p className="text-sm text-ink-soft">
                    {t.candidates.noAnswers}
                  </p>
                ) : (
                  reviews[candidate.application_id].map((item, itemIndex) => {
                    const reviewList = reviews[candidate.application_id]
                    const isFinal = candidate.status === "completed"
                    const contribution = isFinal
                      ? Math.round(item.score / reviewList.length)
                      : null

                    return (
                      <div key={itemIndex} className="rounded-lg bg-surface-2 p-3">
                        <p className="text-sm text-ink-soft">
                          {item.question_text}
                        </p>
                        <p className="mt-1 text-sm text-ink">
                          {item.answer_text}
                        </p>
                        {contribution !== null && (
                          <p className="mt-1 text-xs text-blue-400">
                            +{contribution} {t.candidates.pointsLabel}
                          </p>
                        )}
                      </div>
                    )
                  })
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}