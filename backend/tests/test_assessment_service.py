import pytest

from app.models import (
    Application,
    ApplicationStatus,
    AssessmentAnswer,
    AssessmentQuestion,
    Job,
    User,
    UserRole,
)
from app.services.assessment_service import (
    get_eligible_application_ids,
    is_eligible,
    update_assessment_score,
)


@pytest.fixture
def employer(db):
    user = User(
        email="employer@test.com",
        hashed_password="x",
        full_name="Employer",
        role=UserRole.EMPLOYER,
    )
    db.add(user)
    db.commit()
    return user


def make_job(db, employer, **kwargs) -> Job:
    defaults = {
        "employer_id": employer.id,
        "title": "Backend Developer",
        "company_name": "Test AS",
        "assessment_slots": 2,
    }
    defaults.update(kwargs)

    job = Job(**defaults)
    db.add(job)
    db.commit()
    return job


def make_application(db, job, score, status=ApplicationStatus.PENDING) -> Application:
    candidate = User(
        email=f"candidate{score}@test.com",
        hashed_password="x",
        full_name=f"Candidate {score}",
        role=UserRole.CANDIDATE,
    )
    db.add(candidate)
    db.commit()

    application = Application(
        job_id=job.id,
        candidate_id=candidate.id,
        compatibility_score=score,
        total_score=score,
        status=status,
    )
    db.add(application)
    db.commit()
    return application


class TestEligibleIds:
    def test_returns_top_candidates_only(self, db, employer):
        job = make_job(db, employer, assessment_slots=2)
        low = make_application(db, job, 40)
        high = make_application(db, job, 90)
        mid = make_application(db, job, 70)

        eligible = get_eligible_application_ids(db, job)

        assert high.id in eligible
        assert mid.id in eligible
        assert low.id not in eligible

    def test_empty_when_no_slots(self, db, employer):
        job = make_job(db, employer, assessment_slots=0)
        make_application(db, job, 90)

        assert get_eligible_application_ids(db, job) == []


class TestIsEligible:
    def test_top_candidate_is_eligible(self, db, employer):
        job = make_job(db, employer, assessment_slots=1)
        application = make_application(db, job, 90)

        assert is_eligible(db, job, application) is True

    def test_low_candidate_is_not_eligible(self, db, employer):
        job = make_job(db, employer, assessment_slots=1)
        make_application(db, job, 90)
        low = make_application(db, job, 40)

        assert is_eligible(db, job, low) is False

    def test_closed_job_blocks_everyone(self, db, employer):
        job = make_job(db, employer, assessment_slots=5, is_closed=True)
        application = make_application(db, job, 90)

        assert is_eligible(db, job, application) is False

    def test_started_candidate_keeps_access(self, db, employer):
        job = make_job(db, employer, assessment_slots=1)
        started = make_application(db, job, 40, ApplicationStatus.ASSESSMENT)
        make_application(db, job, 90)

        assert is_eligible(db, job, started) is True

    def test_completed_candidate_keeps_access(self, db, employer):
        job = make_job(db, employer, assessment_slots=1)
        completed = make_application(db, job, 40, ApplicationStatus.COMPLETED)
        make_application(db, job, 90)

        assert is_eligible(db, job, completed) is True

    def test_closed_job_blocks_started_candidate(self, db, employer):
        job = make_job(db, employer, assessment_slots=5, is_closed=True)
        started = make_application(db, job, 90, ApplicationStatus.ASSESSMENT)

        assert is_eligible(db, job, started) is False


class TestUpdateAssessmentScore:
    def _setup(self, db, employer, question_count=4, weight=50, compatibility=80):
        job = make_job(db, employer, assessment_weight=weight)
        application = make_application(db, job, compatibility)

        questions = [
            AssessmentQuestion(
                job_id=job.id,
                question_text=f"Question {index}",
                is_selected=True,
            )
            for index in range(question_count)
        ]
        db.add_all(questions)
        db.commit()

        return job, application, questions

    def _answer(self, db, application, question, score):
        db.add(
            AssessmentAnswer(
                application_id=application.id,
                question_id=question.id,
                answer_text="answer",
                is_correct=score >= 50,
                score=score,
            )
        )
        db.commit()

    def test_does_nothing_when_no_questions_selected(self, db, employer):
        job = make_job(db, employer)
        application = make_application(db, job, 80)

        update_assessment_score(db, application, job)

        assert application.assessment_score == 0.0

    def test_partial_answers_keep_compatibility_score(self, db, employer):
        job, application, questions = self._setup(db, employer, question_count=4)
        self._answer(db, application, questions[0], 100)

        update_assessment_score(db, application, job)

        assert application.assessment_score == 25.0
        assert application.total_score == 80.0
        assert application.status != ApplicationStatus.COMPLETED

    def test_completed_uses_weighted_formula(self, db, employer):
        job, application, questions = self._setup(
            db, employer, question_count=2, weight=50, compatibility=80
        )
        self._answer(db, application, questions[0], 100)
        self._answer(db, application, questions[1], 60)

        update_assessment_score(db, application, job)

        assert application.assessment_score == 80.0
        assert application.total_score == 80.0
        assert application.status == ApplicationStatus.COMPLETED

    def test_weight_changes_total(self, db, employer):
        job, application, questions = self._setup(
            db, employer, question_count=2, weight=20, compatibility=100
        )
        self._answer(db, application, questions[0], 50)
        self._answer(db, application, questions[1], 50)

        update_assessment_score(db, application, job)

        assert application.assessment_score == 50.0
        assert application.total_score == 90.0

    def test_denominator_is_selected_count_not_answered(self, db, employer):
        job, application, questions = self._setup(db, employer, question_count=4)
        self._answer(db, application, questions[0], 100)
        self._answer(db, application, questions[1], 100)

        update_assessment_score(db, application, job)

        assert application.assessment_score == 50.0