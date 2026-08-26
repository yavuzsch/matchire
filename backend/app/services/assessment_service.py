from sqlalchemy.orm import Session

from app.models import Application, ApplicationStatus, Job


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
    if job.is_closed:
        return False

    if application.status in (ApplicationStatus.ASSESSMENT, ApplicationStatus.COMPLETED):
        return True

    return application.id in get_eligible_application_ids(db, job)