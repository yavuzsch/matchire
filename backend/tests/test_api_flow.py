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
        assert "compatibility_score" not in application

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

        candidate_view = client.get(
            f"/api/assessments/applications/{application['id']}/questions",
            headers=auth(candidate_token),
        ).json()

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
            f"/api/jobs/{job['id']}/status",
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
            f"/api/jobs/{job['id']}/status",
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