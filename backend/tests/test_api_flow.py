from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from tests.conftest import auth


def create_job(client, token, skills, **overrides) -> dict:
    payload = {
        "title": "Backend Developer",
        "company_name": "Test AS",
        "skills": [
            {"skill_id": skills["Python"], "requirement": "mandatory", "weight": 3},
            {"skill_id": skills["FastAPI"], "requirement": "required", "weight": 2},
            {"skill_id": skills["Docker"], "requirement": "optional", "weight": 1},
        ],
        "experience_years": 2,
        "education_level": "bachelor",
        "field": "software_development",
        "assessment_slots": 5,
        "assessment_weight": 50,
    }
    payload.update(overrides)
    return client.post("/api/jobs", json=payload, headers=auth(token)).json()


def create_resume(client, token, skills, **overrides) -> dict:
    payload = {
        "skill_ids": [skills["Python"], skills["FastAPI"], skills["Docker"]],
        "experience_years": 2,
        "education_level": "bachelor",
        "field": "software_development",
    }
    payload.update(overrides)
    return client.post("/api/resumes", json=payload, headers=auth(token)).json()


class TestApplicationFlow:
    def test_full_flow(self, client, employer_token, candidate_token, skills):
        job = create_job(client, employer_token, skills)
        create_resume(client, candidate_token, skills)

        response = client.post(
            "/api/applications",
            json={"job_id": job["id"]},
            headers=auth(candidate_token),
        )

        assert response.status_code == 201
        application = response.json()
        assert application["status"] == "pending"
        assert application["assessment_eligible"] is True
        assert application["compatibility_score"] is not None

    def test_rejects_without_resume(self, client, employer_token, candidate_token, skills):
        job = create_job(client, employer_token, skills)

        response = client.post(
            "/api/applications",
            json={"job_id": job["id"]},
            headers=auth(candidate_token),
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "RESUME_REQUIRED"

    def test_rejects_missing_mandatory_skills(
        self, client, employer_token, candidate_token, skills
    ):
        job = create_job(client, employer_token, skills)
        create_resume(client, candidate_token, skills, skill_ids=[skills["Java"]])

        response = client.post(
            "/api/applications",
            json={"job_id": job["id"]},
            headers=auth(candidate_token),
        )

        assert response.status_code == 400
        detail = response.json()["detail"]
        assert detail["code"] == "MISSING_MANDATORY_SKILLS"
        assert "skills" not in detail

    def test_rejects_duplicate_application(
        self, client, employer_token, candidate_token, skills
    ):
        job = create_job(client, employer_token, skills)
        create_resume(client, candidate_token, skills)
        client.post(
            "/api/applications",
            json={"job_id": job["id"]},
            headers=auth(candidate_token),
        )

        response = client.post(
            "/api/applications",
            json={"job_id": job["id"]},
            headers=auth(candidate_token),
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "ALREADY_APPLIED"


class TestAssessmentFlow:
    def _prepare(self, client, employer_token, candidate_token, skills):
        job = create_job(client, employer_token, skills)
        create_resume(client, candidate_token, skills)
        application = client.post(
            "/api/applications",
            json={"job_id": job["id"]},
            headers=auth(candidate_token),
        ).json()
        return job, application

    def test_full_assessment_flow(self, client, employer_token, candidate_token, skills):
        job, application = self._prepare(
            client, employer_token, candidate_token, skills
        )

        with patch(
            "app.services.question_service.generate_json",
            return_value=["Question 1", "Question 2"],
        ):
            questions = client.post(
                f"/api/assessments/jobs/{job['id']}/questions",
                json={},
                headers=auth(employer_token),
            ).json()

        assert len(questions) == 2

        client.put(
            f"/api/assessments/jobs/{job['id']}/questions",
            json={"question_ids": [q["id"] for q in questions]},
            headers=auth(employer_token),
        )

        client.post(
            f"/api/assessments/applications/{application['id']}/start",
            headers=auth(candidate_token),
        )

        candidate_view = client.get(
            f"/api/assessments/applications/{application['id']}/questions",
            headers=auth(candidate_token),
        ).json()["questions"]

        assert len(candidate_view) == 2
        assert "is_selected" not in candidate_view[0]

        with patch(
            "app.services.evaluation_service.generate_json",
            return_value={"score": 80},
        ):
            for question in candidate_view:
                answer = client.post(
                    f"/api/assessments/applications/{application['id']}/answers",
                    json={"question_id": question["id"], "answer_text": "An answer"},
                    headers=auth(candidate_token),
                ).json()

        assert "score" not in answer
        assert "is_correct" not in answer

        candidates = client.get(
            f"/api/applications/job/{job['id']}", headers=auth(employer_token)
        ).json()

        assert candidates[0]["assessment_score"] == 80.0
        assert candidates[0]["status"] == "completed"
        assert "project_summary" in candidates[0]

    def test_blocks_assessment_when_no_questions_selected(
        self, client, employer_token, candidate_token, skills
    ):
        job, application = self._prepare(
            client, employer_token, candidate_token, skills
        )

        response = client.get(
            f"/api/assessments/applications/{application['id']}/questions",
            headers=auth(candidate_token),
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "NO_QUESTIONS_SELECTED"

    def test_locks_questions_after_first_answer(
        self, client, employer_token, candidate_token, skills
    ):
        job, application = self._prepare(
            client, employer_token, candidate_token, skills
        )

        with patch(
            "app.services.question_service.generate_json",
            return_value=["Question 1"],
        ):
            questions = client.post(
                f"/api/assessments/jobs/{job['id']}/questions",
                json={},
                headers=auth(employer_token),
            ).json()

        client.put(
            f"/api/assessments/jobs/{job['id']}/questions",
            json={"question_ids": [questions[0]["id"]]},
            headers=auth(employer_token),
        )

        client.post(
            f"/api/assessments/applications/{application['id']}/start",
            headers=auth(candidate_token),
        )

        with patch(
            "app.services.evaluation_service.generate_json",
            return_value={"score": 80},
        ):
            client.post(
                f"/api/assessments/applications/{application['id']}/answers",
                json={"question_id": questions[0]["id"], "answer_text": "An answer"},
                headers=auth(candidate_token),
            )

        response = client.put(
            f"/api/assessments/jobs/{job['id']}/questions",
            json={"question_ids": []},
            headers=auth(employer_token),
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "ASSESSMENT_ALREADY_STARTED"


class TestJobLifecycle:
    def test_archived_job_hidden_from_candidates(
        self, client, employer_token, candidate_token, skills
    ):
        job = create_job(client, employer_token, skills)

        client.patch(
            f"/api/jobs/{job['id']}/settings",
            json={"is_active": False},
            headers=auth(employer_token),
        )

        assert client.get("/api/jobs", headers=auth(candidate_token)).json() == []

    def test_closed_job_blocks_assessment(
        self, client, employer_token, candidate_token, skills
    ):
        job = create_job(client, employer_token, skills)
        create_resume(client, candidate_token, skills)
        application = client.post(
            "/api/applications",
            json={"job_id": job["id"]},
            headers=auth(candidate_token),
        ).json()

        client.patch(
            f"/api/jobs/{job['id']}/settings",
            json={"is_closed": True},
            headers=auth(employer_token),
        )

        response = client.get(
            f"/api/assessments/applications/{application['id']}/questions",
            headers=auth(candidate_token),
        )

        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "ASSESSMENT_NOT_ELIGIBLE"

    def test_cannot_delete_job_with_applications(
        self, client, employer_token, candidate_token, skills
    ):
        job = create_job(client, employer_token, skills)
        create_resume(client, candidate_token, skills)
        client.post(
            "/api/applications",
            json={"job_id": job["id"]},
            headers=auth(candidate_token),
        )

        response = client.delete(f"/api/jobs/{job['id']}", headers=auth(employer_token))

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "JOB_HAS_ACTIVITY"

    def test_can_delete_empty_job(self, client, employer_token, skills):
        job = create_job(client, employer_token, skills)

        response = client.delete(f"/api/jobs/{job['id']}", headers=auth(employer_token))

        assert response.status_code == 204


class TestJobParsing:
    def test_parses_job_text(self, client, employer_token, skills):
        with patch(
            "app.services.job_parser.generate_json",
            return_value={
                "title": "Backend Developer",
                "company_name": "Test AS",
                "skills": [{"name": "Python", "requirement": "mandatory"}],
                "experience_years": 3,
                "education_level": "bachelor",
                "field": "software_development",
            },
        ):
            response = client.post(
                "/api/jobs/parse",
                json={"text": "We are hiring a backend developer with Python"},
                headers=auth(employer_token),
            )

        assert response.status_code == 200
        parsed = response.json()
        assert parsed["title"] == "Backend Developer"
        assert len(parsed["skills"]) == 1
        assert parsed["skills"][0]["requirement"] == "mandatory"
        assert parsed["skills"][0]["weight"] == 3

    def test_reports_unmatched_skills(self, client, employer_token, skills):
        with patch(
            "app.services.job_parser.generate_json",
            return_value={
                "title": "Backend Developer",
                "skills": [
                    {"name": "Python", "requirement": "required"},
                    {"name": "Svelte", "requirement": "required"},
                ],
            },
        ):
            response = client.post(
                "/api/jobs/parse",
                json={"text": "job text"},
                headers=auth(employer_token),
            )

        assert response.json()["unmatched_skills"] == ["Svelte"]

    def test_candidate_cannot_parse_job(self, client, candidate_token):
        response = client.post(
            "/api/jobs/parse",
            json={"text": "job text"},
            headers=auth(candidate_token),
        )

        assert response.status_code == 403


class TestApplicationStatus:
    def _prepare(self, client, employer_token, candidate_token, skills):
        job = create_job(client, employer_token, skills)
        create_resume(client, candidate_token, skills)
        application = client.post(
            "/api/applications",
            json={"job_id": job["id"]},
            headers=auth(candidate_token),
        ).json()
        return job, application

    def test_employer_can_reject(
        self, client, employer_token, candidate_token, skills
    ):
        job, application = self._prepare(
            client, employer_token, candidate_token, skills
        )

        response = client.patch(
            f"/api/applications/{application['id']}/status",
            json={"status": "rejected"},
            headers=auth(employer_token),
        )

        assert response.status_code == 200
        assert response.json()["status"] == "rejected"

    def test_rejected_candidate_loses_assessment_access(
        self, client, employer_token, candidate_token, skills
    ):
        job, application = self._prepare(
            client, employer_token, candidate_token, skills
        )

        client.patch(
            f"/api/applications/{application['id']}/status",
            json={"status": "rejected"},
            headers=auth(employer_token),
        )

        applications = client.get(
            "/api/applications/mine", headers=auth(candidate_token)
        ).json()

        assert applications[0]["status"] == "rejected"
        assert applications[0]["assessment_eligible"] is False

    def test_employer_can_undo_rejection(
        self, client, employer_token, candidate_token, skills
    ):
        job, application = self._prepare(
            client, employer_token, candidate_token, skills
        )

        client.patch(
            f"/api/applications/{application['id']}/status",
            json={"status": "rejected"},
            headers=auth(employer_token),
        )

        response = client.patch(
            f"/api/applications/{application['id']}/status",
            json={"status": "pending"},
            headers=auth(employer_token),
        )

        assert response.json()["status"] == "pending"

    def test_rejects_invalid_status_change(
        self, client, employer_token, candidate_token, skills
    ):
        job, application = self._prepare(
            client, employer_token, candidate_token, skills
        )

        response = client.patch(
            f"/api/applications/{application['id']}/status",
            json={"status": "completed"},
            headers=auth(employer_token),
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_STATUS_CHANGE"

    def test_candidate_cannot_change_status(
        self, client, employer_token, candidate_token, skills
    ):
        job, application = self._prepare(
            client, employer_token, candidate_token, skills
        )

        response = client.patch(
            f"/api/applications/{application['id']}/status",
            json={"status": "rejected"},
            headers=auth(candidate_token),
        )

        assert response.status_code == 403

    def test_cannot_accept_before_completion(
        self, client, employer_token, candidate_token, skills
    ):
        job, application = self._prepare(
            client, employer_token, candidate_token, skills
        )

        response = client.patch(
            f"/api/applications/{application['id']}/status",
            json={"status": "accepted"},
            headers=auth(employer_token),
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_STATUS_CHANGE"

    def test_can_accept_after_completion(
        self, client, employer_token, candidate_token, skills
    ):
        job, application = self._prepare(
            client, employer_token, candidate_token, skills
        )

        with patch(
            "app.services.question_service.generate_json",
            return_value=["Question 1"],
        ):
            questions = client.post(
                f"/api/assessments/jobs/{job['id']}/questions",
                json={},
                headers=auth(employer_token),
            ).json()

        client.put(
            f"/api/assessments/jobs/{job['id']}/questions",
            json={"question_ids": [questions[0]["id"]]},
            headers=auth(employer_token),
        )

        client.post(
            f"/api/assessments/applications/{application['id']}/start",
            headers=auth(candidate_token),
        )

        with patch(
            "app.services.evaluation_service.generate_json",
            return_value={"score": 80},
        ):
            client.post(
                f"/api/assessments/applications/{application['id']}/answers",
                json={"question_id": questions[0]["id"], "answer_text": "An answer"},
                headers=auth(candidate_token),
            )

        response = client.patch(
            f"/api/applications/{application['id']}/status",
            json={"status": "accepted"},
            headers=auth(employer_token),
        )

        assert response.status_code == 200
        assert response.json()["status"] == "accepted"

    def test_accepted_candidate_cannot_start_assessment_again(
        self, client, employer_token, candidate_token, skills
    ):
        job, application = self._prepare(
            client, employer_token, candidate_token, skills
        )

        with patch(
            "app.services.question_service.generate_json",
            return_value=["Question 1"],
        ):
            questions = client.post(
                f"/api/assessments/jobs/{job['id']}/questions",
                json={},
                headers=auth(employer_token),
            ).json()

        client.put(
            f"/api/assessments/jobs/{job['id']}/questions",
            json={"question_ids": [questions[0]["id"]]},
            headers=auth(employer_token),
        )

        client.post(
            f"/api/assessments/applications/{application['id']}/start",
            headers=auth(candidate_token),
        )

        with patch(
            "app.services.evaluation_service.generate_json",
            return_value={"score": 80},
        ):
            client.post(
                f"/api/assessments/applications/{application['id']}/answers",
                json={"question_id": questions[0]["id"], "answer_text": "An answer"},
                headers=auth(candidate_token),
            )

        client.patch(
            f"/api/applications/{application['id']}/status",
            json={"status": "accepted"},
            headers=auth(employer_token),
        )

        response = client.get(
            f"/api/assessments/applications/{application['id']}/questions",
            headers=auth(candidate_token),
        )

        assert response.status_code == 403

    def test_can_undo_acceptance(
        self, client, employer_token, candidate_token, skills
    ):
        job, application = self._prepare(
            client, employer_token, candidate_token, skills
        )

        with patch(
            "app.services.question_service.generate_json",
            return_value=["Question 1"],
        ):
            questions = client.post(
                f"/api/assessments/jobs/{job['id']}/questions",
                json={},
                headers=auth(employer_token),
            ).json()

        client.put(
            f"/api/assessments/jobs/{job['id']}/questions",
            json={"question_ids": [questions[0]["id"]]},
            headers=auth(employer_token),
        )

        client.post(
            f"/api/assessments/applications/{application['id']}/start",
            headers=auth(candidate_token),
        )

        with patch(
            "app.services.evaluation_service.generate_json",
            return_value={"score": 80},
        ):
            client.post(
                f"/api/assessments/applications/{application['id']}/answers",
                json={"question_id": questions[0]["id"], "answer_text": "An answer"},
                headers=auth(candidate_token),
            )

        client.patch(
            f"/api/applications/{application['id']}/status",
            json={"status": "accepted"},
            headers=auth(employer_token),
        )

        response = client.patch(
            f"/api/applications/{application['id']}/status",
            json={"status": "pending"},
            headers=auth(employer_token),
        )

        assert response.status_code == 200
        assert response.json()["status"] == "pending"


class TestAssessmentTimeLimit:
    def _prepare_with_time_limit(
        self, client, employer_token, candidate_token, skills, minutes
    ):
        job = create_job(client, employer_token, skills)

        if minutes is not None:
            client.patch(
                f"/api/jobs/{job['id']}/settings",
                json={"assessment_time_limit_minutes": minutes},
                headers=auth(employer_token),
            )

        create_resume(client, candidate_token, skills)
        application = client.post(
            "/api/applications",
            json={"job_id": job["id"]},
            headers=auth(candidate_token),
        ).json()

        with patch(
            "app.services.question_service.generate_json",
            return_value=["Question 1"],
        ):
            questions = client.post(
                f"/api/assessments/jobs/{job['id']}/questions",
                json={},
                headers=auth(employer_token),
            ).json()

        client.put(
            f"/api/assessments/jobs/{job['id']}/questions",
            json={"question_ids": [questions[0]["id"]]},
            headers=auth(employer_token),
        )

        return job, application, questions

    def test_session_includes_time_limit(
        self, client, employer_token, candidate_token, skills
    ):
        job, application, questions = self._prepare_with_time_limit(
            client, employer_token, candidate_token, skills, 30
        )

        response = client.post(
            f"/api/assessments/applications/{application['id']}/start",
            headers=auth(candidate_token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["time_limit_minutes"] == 30
        assert data["started_at"] is not None
        assert len(data["questions"]) == 1

    def test_no_time_limit_by_default(
        self, client, employer_token, candidate_token, skills
    ):
        job, application, questions = self._prepare_with_time_limit(
            client, employer_token, candidate_token, skills, None
        )

        response = client.post(
            f"/api/assessments/applications/{application['id']}/start",
            headers=auth(candidate_token),
        )

        assert response.json()["time_limit_minutes"] is None

    def test_started_at_does_not_change_on_second_start(
        self, client, employer_token, candidate_token, skills
    ):
        job, application, questions = self._prepare_with_time_limit(
            client, employer_token, candidate_token, skills, 30
        )

        first = client.post(
            f"/api/assessments/applications/{application['id']}/start",
            headers=auth(candidate_token),
        ).json()

        second = client.post(
            f"/api/assessments/applications/{application['id']}/start",
            headers=auth(candidate_token),
        ).json()

        assert first["started_at"] == second["started_at"]

    def test_expired_time_blocks_question_access(
        self, client, employer_token, candidate_token, skills, db
    ):
        job, application, questions = self._prepare_with_time_limit(
            client, employer_token, candidate_token, skills, 10
        )

        client.post(
            f"/api/assessments/applications/{application['id']}/start",
            headers=auth(candidate_token),
        )

        from app.models import Application as ApplicationModel

        record = (
            db.query(ApplicationModel)
            .filter(ApplicationModel.id == application["id"])
            .first()
        )
        record.assessment_started_at = datetime.now(timezone.utc) - timedelta(
            minutes=20
        )
        db.commit()

        response = client.get(
            f"/api/assessments/applications/{application['id']}/questions",
            headers=auth(candidate_token),
        )

        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "ASSESSMENT_TIME_EXPIRED"

    def test_expired_time_blocks_answer_submission(
        self, client, employer_token, candidate_token, skills, db
    ):
        job, application, questions = self._prepare_with_time_limit(
            client, employer_token, candidate_token, skills, 10
        )

        client.post(
            f"/api/assessments/applications/{application['id']}/start",
            headers=auth(candidate_token),
        )

        from app.models import Application as ApplicationModel

        record = (
            db.query(ApplicationModel)
            .filter(ApplicationModel.id == application["id"])
            .first()
        )
        record.assessment_started_at = datetime.now(timezone.utc) - timedelta(
            minutes=20
        )
        db.commit()

        response = client.post(
            f"/api/assessments/applications/{application['id']}/answers",
            json={"question_id": questions[0]["id"], "answer_text": "An answer"},
            headers=auth(candidate_token),
        )

        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "ASSESSMENT_TIME_EXPIRED"

    def test_answer_within_time_limit_succeeds(
        self, client, employer_token, candidate_token, skills
    ):
        job, application, questions = self._prepare_with_time_limit(
            client, employer_token, candidate_token, skills, 30
        )

        client.post(
            f"/api/assessments/applications/{application['id']}/start",
            headers=auth(candidate_token),
        )

        with patch(
            "app.services.evaluation_service.generate_json",
            return_value={"score": 80},
        ):
            response = client.post(
                f"/api/assessments/applications/{application['id']}/answers",
                json={"question_id": questions[0]["id"], "answer_text": "An answer"},
                headers=auth(candidate_token),
            )

        assert response.status_code == 200

    def test_questions_endpoint_shows_not_started_before_start(
        self, client, employer_token, candidate_token, skills
    ):
        job, application, questions = self._prepare_with_time_limit(
            client, employer_token, candidate_token, skills, 30
        )

        response = client.get(
            f"/api/assessments/applications/{application['id']}/questions",
            headers=auth(candidate_token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["started_at"] is None
        assert data["questions"] == []

    def test_questions_endpoint_shows_questions_after_start(
        self, client, employer_token, candidate_token, skills
    ):
        job, application, questions = self._prepare_with_time_limit(
            client, employer_token, candidate_token, skills, 30
        )

        client.post(
            f"/api/assessments/applications/{application['id']}/start",
            headers=auth(candidate_token),
        )

        response = client.get(
            f"/api/assessments/applications/{application['id']}/questions",
            headers=auth(candidate_token),
        )

        data = response.json()
        assert data["started_at"] is not None
        assert len(data["questions"]) == 1


class TestJobSettingsLock:
    def _start_assessment(
        self, client, employer_token, candidate_token, skills
    ):
        job = create_job(client, employer_token, skills)

        client.patch(
            f"/api/jobs/{job['id']}/settings",
            json={"assessment_time_limit_minutes": 30},
            headers=auth(employer_token),
        )

        create_resume(client, candidate_token, skills)
        application = client.post(
            "/api/applications",
            json={"job_id": job["id"]},
            headers=auth(candidate_token),
        ).json()

        with patch(
            "app.services.question_service.generate_json",
            return_value=["Question 1"],
        ):
            questions = client.post(
                f"/api/assessments/jobs/{job['id']}/questions",
                json={},
                headers=auth(employer_token),
            ).json()

        client.put(
            f"/api/assessments/jobs/{job['id']}/questions",
            json={"question_ids": [questions[0]["id"]]},
            headers=auth(employer_token),
        )

        client.post(
            f"/api/assessments/applications/{application['id']}/start",
            headers=auth(candidate_token),
        )

        return job, application

    def test_cannot_change_time_limit_after_started(
        self, client, employer_token, candidate_token, skills
    ):
        job, application = self._start_assessment(
            client, employer_token, candidate_token, skills
        )

        response = client.patch(
            f"/api/jobs/{job['id']}/settings",
            json={"assessment_time_limit_minutes": 60},
            headers=auth(employer_token),
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "ASSESSMENT_TIME_LOCKED"

    def test_can_change_other_settings_after_started(
        self, client, employer_token, candidate_token, skills
    ):
        job, application = self._start_assessment(
            client, employer_token, candidate_token, skills
        )

        response = client.patch(
            f"/api/jobs/{job['id']}/settings",
            json={"is_closed": True},
            headers=auth(employer_token),
        )

        assert response.status_code == 200

    def test_can_set_time_limit_before_anyone_started(
        self, client, employer_token, skills
    ):
        job = create_job(client, employer_token, skills)

        response = client.patch(
            f"/api/jobs/{job['id']}/settings",
            json={"assessment_time_limit_minutes": 45},
            headers=auth(employer_token),
        )

        assert response.status_code == 200
        assert response.json()["assessment_time_limit_minutes"] == 45


class TestApplicationWithdrawal:
    def test_candidate_can_withdraw_pending_application(
        self, client, employer_token, candidate_token, skills
    ):
        job = create_job(client, employer_token, skills)
        create_resume(client, candidate_token, skills)
        application = client.post(
            "/api/applications",
            json={"job_id": job["id"]},
            headers=auth(candidate_token),
        ).json()

        response = client.delete(
            f"/api/applications/{application['id']}",
            headers=auth(candidate_token),
        )

        assert response.status_code == 204

    def test_withdrawn_application_hidden_from_list(
        self, client, employer_token, candidate_token, skills
    ):
        job = create_job(client, employer_token, skills)
        create_resume(client, candidate_token, skills)
        application = client.post(
            "/api/applications",
            json={"job_id": job["id"]},
            headers=auth(candidate_token),
        ).json()

        client.delete(
            f"/api/applications/{application['id']}",
            headers=auth(candidate_token),
        )

        applications = client.get(
            "/api/applications/mine", headers=auth(candidate_token)
        ).json()

        assert applications == []

    def test_cannot_withdraw_accepted_application(
        self, client, employer_token, candidate_token, skills
    ):
        job = create_job(client, employer_token, skills)
        create_resume(client, candidate_token, skills)
        application = client.post(
            "/api/applications",
            json={"job_id": job["id"]},
            headers=auth(candidate_token),
        ).json()

        with patch(
            "app.services.question_service.generate_json",
            return_value=["Question 1"],
        ):
            questions = client.post(
                f"/api/assessments/jobs/{job['id']}/questions",
                json={},
                headers=auth(employer_token),
            ).json()

        client.put(
            f"/api/assessments/jobs/{job['id']}/questions",
            json={"question_ids": [questions[0]["id"]]},
            headers=auth(employer_token),
        )

        client.post(
            f"/api/assessments/applications/{application['id']}/start",
            headers=auth(candidate_token),
        )

        with patch(
            "app.services.evaluation_service.generate_json",
            return_value={"score": 80},
        ):
            client.post(
                f"/api/assessments/applications/{application['id']}/answers",
                json={"question_id": questions[0]["id"], "answer_text": "An answer"},
                headers=auth(candidate_token),
            )

        client.patch(
            f"/api/applications/{application['id']}/status",
            json={"status": "accepted"},
            headers=auth(employer_token),
        )

        response = client.delete(
            f"/api/applications/{application['id']}",
            headers=auth(candidate_token),
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "CANNOT_WITHDRAW_ACCEPTED"

    def test_cannot_withdraw_others_application(
        self, client, employer_token, candidate_token, skills
    ):
        job = create_job(client, employer_token, skills)
        create_resume(client, candidate_token, skills)
        application = client.post(
            "/api/applications",
            json={"job_id": job["id"]},
            headers=auth(candidate_token),
        ).json()

        other_candidate = client.post(
            "/api/auth/register",
            json={
                "email": "other_candidate@test.com",
                "password": "password123",
                "full_name": "Other Candidate",
                "role": "candidate",
            },
        ).json()["access_token"]

        response = client.delete(
            f"/api/applications/{application['id']}",
            headers=auth(other_candidate),
        )

        assert response.status_code == 404

    def test_application_list_includes_compatibility_score(
        self, client, employer_token, candidate_token, skills
    ):
        job = create_job(client, employer_token, skills)
        create_resume(client, candidate_token, skills)
        client.post(
            "/api/applications",
            json={"job_id": job["id"]},
            headers=auth(candidate_token),
        )

        applications = client.get(
            "/api/applications/mine", headers=auth(candidate_token)
        ).json()

        assert applications[0]["compatibility_score"] is not None