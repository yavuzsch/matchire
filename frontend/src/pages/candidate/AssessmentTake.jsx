import { useEffect, useMemo, useState } from "react"
import { useParams } from "react-router-dom"

import { get, post } from "../../api/client"
import Message from "../../components/Message"
import Spinner from "../../components/Spinner"
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
  const [now, setNow] = useState(() => Date.now())
  const [answers, setAnswers] = useState({})
  const [answeredIds, setAnsweredIds] = useState([])
  const [submitting, setSubmitting] = useState(false)
  const [starting, setStarting] = useState(false)
  const [error, setError] = useState(null)
  const [notReady, setNotReady] = useState(false)
  const [notStarted, setNotStarted] = useState(false)
  const [serverTimeExpired, setServerTimeExpired] = useState(false)

  useEffect(() => {
    get(`/assessments/applications/${applicationId}/questions`)
      .then((data) => {
        setTimeLimitMinutes(data.time_limit_minutes)

        if (data.started_at === null) {
          setNotStarted(true)
          return
        }

        setQuestions(data.questions)
        setStartedAt(new Date(data.started_at).getTime())
      })
      .catch((err) => {
        if (err.code === "NO_QUESTIONS_SELECTED") {
          setNotReady(true)
        } else if (err.code === "ASSESSMENT_TIME_EXPIRED") {
          setServerTimeExpired(true)
        } else {
          setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
        }
      })

    get(`/assessments/applications/${applicationId}/answers`)
      .then((data) => setAnsweredIds(data.map((item) => item.question_id)))
      .catch(() => setAnsweredIds([]))
  }, [applicationId])

  async function start() {
    setError(null)
    setStarting(true)

    try {
      const data = await post(`/assessments/applications/${applicationId}/start`)
      setQuestions(data.questions)
      setStartedAt(new Date(data.started_at).getTime())
      setTimeLimitMinutes(data.time_limit_minutes)
      setNotStarted(false)
    } catch (err) {
      if (err.code === "ASSESSMENT_TIME_EXPIRED") {
        setServerTimeExpired(true)
      } else {
        setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
      }
    } finally {
      setStarting(false)
    }
  }

  const unansweredQuestions = questions.filter((q) => !answeredIds.includes(q.id))
  const hasFilledAnswer = unansweredQuestions.some(
    (q) => (answers[q.id] || "").trim().length > 0
  )
  const completed = questions.length > 0 && answeredIds.length === questions.length

  useEffect(() => {
    if (!timeLimitMinutes || notStarted || completed) {
      return
    }

    const interval = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(interval)
  }, [timeLimitMinutes, notStarted, completed])

  const remainingSeconds = useMemo(() => {
    if (!timeLimitMinutes || !startedAt) {
      return null
    }

    const deadline = startedAt + timeLimitMinutes * 60 * 1000
    return Math.floor((deadline - now) / 1000)
  }, [startedAt, timeLimitMinutes, now])

  const clientTimeExpired =
    !completed &&
    timeLimitMinutes !== null &&
    remainingSeconds !== null &&
    remainingSeconds <= 0

  const timeExpired = serverTimeExpired || clientTimeExpired

  useEffect(() => {
    function handleBeforeUnload(event) {
      if (timeLimitMinutes && !notStarted && !timeExpired && !completed) {
        event.preventDefault()
        event.returnValue = ""
      }
    }

    window.addEventListener("beforeunload", handleBeforeUnload)
    return () => window.removeEventListener("beforeunload", handleBeforeUnload)
  }, [timeLimitMinutes, notStarted, timeExpired, completed])

  function setAnswer(questionId, text) {
    setAnswers({ ...answers, [questionId]: text })
  }

  async function submitAll() {
    setError(null)
    setSubmitting(true)

    const toSubmit = unansweredQuestions.filter(
      (q) => (answers[q.id] || "").trim().length > 0
    )

    if (toSubmit.length === 0) {
      setSubmitting(false)
      return
    }

    try {
      const saved = await post(`/assessments/applications/${applicationId}/answers`, {
        answers: toSubmit.map((q) => ({
          question_id: q.id,
          answer_text: answers[q.id],
        })),
      })

      const savedIds = saved.map((item) => item.question_id)
      setAnsweredIds([...answeredIds, ...savedIds])
    } catch (err) {
      if (err.code === "ASSESSMENT_TIME_EXPIRED") {
        setServerTimeExpired(true)
      } else {
        setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
      }
    } finally {
      setSubmitting(false)
    }
  }

  if (notReady) {
    return (
      <div>
        <h1 className="text-2xl font-extrabold text-ink">{t.assessment.title}</h1>
        <p className="mt-4 text-sm text-ink-soft">{t.assessment.notReady}</p>
      </div>
    )
  }

  if (timeExpired) {
    return (
      <div>
        <h1 className="text-2xl font-extrabold text-ink">{t.assessment.title}</h1>
        <p className="mt-4 text-sm text-blue-400">{t.assessment.timeExpired}</p>
      </div>
    )
  }

  if (notStarted) {
    return (
      <div>
        <h1 className="text-2xl font-extrabold text-ink">{t.assessment.title}</h1>

        <Message error={error} className="mt-4" />

        <div className="mt-6 rounded-xl bg-surface p-6">
          <h2 className="font-semibold text-ink">{t.assessment.beforeStartTitle}</h2>

          <p className="mt-3 text-sm text-ink-soft">
            {timeLimitMinutes
              ? t.assessment.beforeStartWithLimit.replace(
                  "{minutes}",
                  timeLimitMinutes
                )
              : t.assessment.beforeStartNoLimit}
          </p>

          <button
            type="button"
            onClick={start}
            disabled={starting}
            className="mt-6 flex items-center gap-2 rounded-lg bg-blue-500 px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-blue-600 disabled:opacity-50"
          >
            {starting && <Spinner />}
            {starting ? t.assessment.starting : t.assessment.start}
          </button>
        </div>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-2xl font-extrabold text-ink">{t.assessment.title}</h1>

      <Message error={error} className="mt-4" />

      <div className="mt-4 rounded-xl bg-surface p-4">
        {timeLimitMinutes && remainingSeconds !== null ? (
          <>
            <p className="text-sm text-ink-soft">
              {t.assessment.timeRemaining}:{" "}
              <span className="font-mono font-medium text-blue-400">
                {formatRemaining(remainingSeconds)}
              </span>
            </p>
            <p className="mt-1 text-xs text-ink-soft">{t.assessment.leaveWarning}</p>
          </>
        ) : (
          <p className="text-sm text-ink-soft">{t.assessment.noTimeLimit}</p>
        )}
      </div>

      {questions.length > 0 && (
        <p className="mt-4 text-sm text-ink-soft">
          {answeredIds.length}/{questions.length} {t.assessment.progress}
        </p>
      )}

      {completed && (
        <p className="mt-4 text-sm text-green-400">{t.assessment.completed}</p>
      )}

      <div className="mt-4 space-y-3">
        {questions.map((question, index) => (
          <div key={question.id} className="rounded-xl bg-surface p-5">
            <p className="text-sm text-ink">
              {index + 1}. {question.question_text}
            </p>

            {answeredIds.includes(question.id) ? (
              <span className="mt-3 inline-block text-sm text-green-400">
                {t.assessment.answered}
              </span>
            ) : (
              <textarea
                value={answers[question.id] || ""}
                onChange={(e) => setAnswer(question.id, e.target.value)}
                placeholder={t.assessment.answerPlaceholder}
                rows="3"
                className="mt-3 w-full rounded-lg bg-surface-2 px-3 py-2 text-sm text-ink placeholder-ink-soft outline-none ring-blue-500 focus:ring-2"
              />
            )}
          </div>
        ))}
      </div>

      {!completed && questions.length > 0 && (
        <button
          type="button"
          onClick={submitAll}
          disabled={submitting || !hasFilledAnswer}
          className="mt-6 flex items-center gap-2 rounded-lg bg-blue-500 px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-blue-600 disabled:opacity-50"
        >
          {submitting && <Spinner />}
          {submitting ? t.assessment.submitting : t.assessment.submit}
        </button>
      )}
    </div>
  )
}