from tests.conftest import auth


def create_job(client, token) -> dict:
    response = client.post(
        "/api/jobs",
        json={
            "title": "Backend Developer",
            "company_name": "Test AS",
            "required_skills": ["Python"],
            "mandatory_skills": ["Python"],
            "skill_weights": {"Python": 3},
            "experience_years": 2,
            "education_level": "bachelor",
            "field": "software_development",
        },
        headers=auth(token),
    )
    return response.json()


class TestEmployerOnlyEndpoints:
    def test_candidate_cannot_create_job(self, client, candidate_token):
        response = client.post(
            "/api/jobs",
            json={"title": "Test", "company_name": "Test"},
            headers=auth(candidate_token),
        )

        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "EMPLOYER_ROLE_REQUIRED"

    def test_candidate_cannot_list_own_jobs(self, client, candidate_token):
        response = client.get("/api/jobs/mine", headers=auth(candidate_token))

        assert response.status_code == 403


class TestCandidateOnlyEndpoints:
    def test_employer_cannot_create_resume(self, client, employer_token):
        response = client.post(
            "/api/resumes",
            json={"skills": ["Python"], "experience_years": 2},
            headers=auth(employer_token),
        )

        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "CANDIDATE_ROLE_REQUIRED"

    def test_employer_cannot_apply(self, client, employer_token):
        response = client.post(
            "/api/applications",
            json={"job_id": 1},
            headers=auth(employer_token),
        )

        assert response.status_code == 403


class TestJobOwnership:
    def test_employer_cannot_modify_other_job(self, client, employer_token):
        job = create_job(client, employer_token)

        other = client.post(
            "/api/auth/register",
            json={
                "email": "other@test.com",
                "password": "password123",
                "full_name": "Other Employer",
                "role": "employer",
            },
        ).json()["access_token"]

        response = client.patch(
            f"/api/jobs/{job['id']}/status",
            json={"is_active": False},
            headers=auth(other),
        )

        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "JOB_ACCESS_DENIED"

    def test_employer_cannot_view_other_candidates(self, client, employer_token):
        job = create_job(client, employer_token)

        other = client.post(
            "/api/auth/register",
            json={
                "email": "other2@test.com",
                "password": "password123",
                "full_name": "Other Employer",
                "role": "employer",
            },
        ).json()["access_token"]

        response = client.get(
            f"/api/applications/job/{job['id']}", headers=auth(other)
        )

        assert response.status_code == 403


class TestPublicFiltering:
    def test_candidate_does_not_see_skill_requirements(self, client, employer_token, candidate_token):
        create_job(client, employer_token)

        jobs = client.get("/api/jobs", headers=auth(candidate_token)).json()

        assert len(jobs) == 1
        assert "required_skills" not in jobs[0]
        assert "mandatory_skills" not in jobs[0]
        assert "skill_weights" not in jobs[0]
        assert "assessment_slots" not in jobs[0]