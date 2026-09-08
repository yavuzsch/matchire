import { useEffect, useMemo, useState } from "react"
import { useParams } from "react-router-dom"

import { get, post } from "../../api/client"
import { t } from "../../i18n"

function formatRemaining(seconds) {
  const clamped = Math.max(0, seconds)
  const minutes = Math.floor(clamped / 60)
  const secs = clamped % 60
  return `${minutes}:${String(secs).padStart(2, "0")}`
}

export default function AssessmentTake() {
  const { applicationId } = useParams()

  const [questions, setQuestions] = useState([])
  const [startedAt, setStartedAt] = useState(null)
  const [timeLimitMinutes, setTimeLimitMinutes] = useState(null)
  const [now, setNow] = useState(Date.now())
  const [answers, setAnswers] = useState({})
  const [answeredIds, setAnsweredIds] = useState([])
  const [pendingId, setPendingId] = useState(null)
  const [error, setError] = useState(null)
  const [notReady, setNotReady] = useState(false)
  const [timeExpired, setTimeExpired] = useState(false)

  useEffect(() => {
    get(`/assessments/applications/${applicationId}/questions`)
      .then((data) => {
        setQuestions(data.questions)
        setStartedAt(new Date(data.started_at).getTime())
        setTimeLimitMinutes(data.time_limit_minutes)
      })
      .catch((err) => {
        if (err.code === "NO_QUESTIONS_SELECTED") {
          setNotReady(true)
        } else if (err.code === "ASSESSMENT_TIME_EXPIRED") {
          setTimeExpired(true)
        } else {
          setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
        }
      })

    get(`/assessments/applications/${applicationId}/answers`)
      .then((data) => setAnsweredIds(data.map((item) => item.question_id)))
      .catch(() => setAnsweredIds([]))
  }, [applicationId])

  useEffect(() => {
    if (!timeLimitMinutes) {
      return
    }

    const interval = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(interval)
  }, [timeLimitMinutes])

  useEffect(() => {
    function handleBeforeUnload(event) {
      if (timeLimitMinutes && !timeExpired) {
        event.preventDefault()
        event.returnValue = ""
      }
    }

    window.addEventListener("beforeunload", handleBeforeUnload)
    return () => window.removeEventListener("beforeunload", handleBeforeUnload)
  }, [timeLimitMinutes, timeExpired])

  const remainingSeconds = useMemo(() => {
    if (!timeLimitMinutes || !startedAt) {
      return null
    }

    const deadline = startedAt + timeLimitMinutes * 60 * 1000
    return Math.floor((deadline - now) / 1000)
  }, [startedAt, timeLimitMinutes, now])

  useEffect(() => {
    if (remainingSeconds !== null && remainingSeconds <= 0 && !timeExpired) {
      setTimeExpired(true)
    }
  }, [remainingSeconds, timeExpired])

  function setAnswer(questionId, text) {
    setAnswers({ ...answers, [questionId]: text })
  }

  async function submit(questionId) {
    setError(null)
    setPendingId(questionId)

    try {
      await post(`/assessments/applications/${applicationId}/answers`, {
        question_id: questionId,
        answer_text: answers[questionId] || "",
      })
      setAnsweredIds([...answeredIds, questionId])
    } catch (err) {
      if (err.code === "ASSESSMENT_TIME_EXPIRED") {
        setTimeExpired(true)
      } else {
        setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
      }
    } finally {
      setPendingId(null)
    }
  }

  const completed = questions.length > 0 && answeredIds.length === questions.length

  if (notReady) {
    return (
      <div className="mx-auto max-w-3xl p-8">
        <h1 className="mb-6 text-2xl font-bold text-white">{t.assessment.title}</h1>
        <p className="text-slate-400">{t.assessment.notReady}</p>
      </div>
    )
  }

  if (timeExpired) {
    return (
      <div className="mx-auto max-w-3xl p-8">
        <h1 className="mb-6 text-2xl font-bold text-white">{t.assessment.title}</h1>
        <p className="text-amber-400">{t.assessment.timeExpired}</p>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl p-8">
      <h1 className="mb-6 text-2xl font-bold text-white">{t.assessment.title}</h1>

      {error && <p className="mb-4 text-sm text-red-400">{error}</p>}

      <div className="mb-4 rounded bg-slate-800 p-3">
        {timeLimitMinutes && remainingSeconds !== null ? (
          <>
            <p className="text-sm text-slate-300">
              {t.assessment.timeRemaining}:{" "}
              <span className="font-mono text-amber-400">
                {formatRemaining(remainingSeconds)}
              </span>
            </p>
            <p className="mt-1 text-xs text-slate-500">{t.assessment.leaveWarning}</p>
          </>
        ) : (
          <p className="text-sm text-slate-400">{t.assessment.noTimeLimit}</p>
        )}
      </div>

      {questions.length > 0 && (
        <p className="mb-4 text-sm text-slate-400">
          {answeredIds.length}/{questions.length} {t.assessment.progress}
        </p>
      )}

      {completed && (
        <p className="mb-4 text-sm text-green-400">{t.assessment.completed}</p>
      )}

      <div className="space-y-4">
        {questions.map((question, index) => (
          <div key={question.id} className="rounded bg-slate-800 p-4">
            <p className="mb-3 text-sm text-slate-200">
              {index + 1}. {question.question_text}
            </p>

            {answeredIds.includes(question.id) ? (
              <span className="text-sm text-green-400">{t.assessment.answered}</span>
            ) : (
              <>
                <textarea
                  value={answers[question.id] || ""}
                  onChange={(e) => setAnswer(question.id, e.target.value)}
                  placeholder={t.assessment.answerPlaceholder}
                  rows="3"
                  className="w-full rounded bg-slate-700 px-3 py-2 text-white placeholder-slate-400"
                />

                <button
                  type="button"
                  onClick={() => submit(question.id)}
                  disabled={pendingId === question.id}
                  className="mt-2 rounded bg-blue-600 px-4 py-1 text-sm text-white disabled:opacity-50"
                >
                  {pendingId === question.id
                    ? t.assessment.submitting
                    : t.assessment.submit}
                </button>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}