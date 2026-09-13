from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import (
    Application,
    ApplicationStatus,
    AssessmentAnswer,
    AssessmentQuestion,
    Job,
)


def get_eligible_application_ids(db: Session, job: Job) -> list[int]:
    applications = (
        db.query(Application)
        .filter(Application.job_id == job.id)
        .order_by(Application.compatibility_score.desc())
        .limit(job.assessment_slots or 0)
        .all()
    )
    return [application.id for application in applications]


def is_eligible(db: Session, job: Job, application: Application) -> bool:
    if application.status in (ApplicationStatus.REJECTED, ApplicationStatus.ACCEPTED):
        return False

    if job.is_closed:
        return False

    if application.status in (ApplicationStatus.ASSESSMENT, ApplicationStatus.COMPLETED):
        return True

    return application.id in get_eligible_application_ids(db, job)


def has_completed_assessment(db: Session, application: Application, job: Job) -> bool:
    total_selected = (
        db.query(AssessmentQuestion)
        .filter(
            AssessmentQuestion.job_id == job.id,
            AssessmentQuestion.is_selected.is_(True),
        )
        .count()
    )

    if total_selected == 0:
        return False

    answered_count = (
        db.query(AssessmentAnswer)
        .filter(AssessmentAnswer.application_id == application.id)
        .count()
    )

    return answered_count >= total_selected


def is_time_expired(
    application: Application, job: Job, grace_seconds: int = 0
) -> bool:
    if job.assessment_time_limit_minutes is None:
        return False

    if application.assessment_started_at is None:
        return False

    deadline = application.assessment_started_at + timedelta(
        minutes=job.assessment_time_limit_minutes, seconds=grace_seconds
    )
    return datetime.now(timezone.utc) > deadline


def update_assessment_score(db: Session, application: Application, job: Job) -> None:
    selected_count = (
        db.query(AssessmentQuestion)
        .filter(
            AssessmentQuestion.job_id == job.id,
            AssessmentQuestion.is_selected.is_(True),
        )
        .count()
    )

    if selected_count == 0:
        return

    answers = (
        db.query(AssessmentAnswer)
        .filter(AssessmentAnswer.application_id == application.id)
        .all()
    )

    total = sum(answer.score for answer in answers)
    application.assessment_score = round(total / selected_count, 2)

    completed = len(answers) >= selected_count

    if completed:
        weight = job.assessment_weight / 100
        application.total_score = round(
            application.compatibility_score * (1 - weight)
            + application.assessment_score * weight,
            2,
        )
        application.status = ApplicationStatus.COMPLETED
    else:
        application.total_score = application.compatibility_score