from tests.conftest import auth


def create_job(client, token, skills, **overrides) -> dict:
    payload = {
        "title": "Backend Developer",
        "company_name": "Test AS",
        "skills": [
            {
                "skill_id": skills["Python"],
                "requirement": "mandatory",
                "weight": 3,
            }
        ],
        "experience_years": 2,
        "education_level": "bachelor",
        "field": "software_development",
    }
    payload.update(overrides)
    return client.post("/api/jobs", json=payload, headers=auth(token)).json()


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
    def test_employer_cannot_create_resume(self, client, employer_token, skills):
        response = client.post(
            "/api/resumes",
            json={"skill_ids": [skills["Python"]], "experience_years": 2},
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


class TestSkillValidation:
    def test_rejects_unknown_skill_id(self, client, employer_token):
        response = client.post(
            "/api/jobs",
            json={
                "title": "Backend Developer",
                "company_name": "Test AS",
                "skills": [
                    {"skill_id": 9999, "requirement": "required", "weight": 1}
                ],
            },
            headers=auth(employer_token),
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "SKILL_NOT_FOUND"

    def test_rejects_duplicate_skill(self, client, employer_token, skills):
        response = client.post(
            "/api/jobs",
            json={
                "title": "Backend Developer",
                "company_name": "Test AS",
                "skills": [
                    {
                        "skill_id": skills["Python"],
                        "requirement": "required",
                        "weight": 1,
                    },
                    {
                        "skill_id": skills["Python"],
                        "requirement": "optional",
                        "weight": 1,
                    },
                ],
            },
            headers=auth(employer_token),
        )

        assert response.status_code == 422


class TestJobOwnership:
    def test_employer_cannot_modify_other_job(self, client, employer_token, skills):
        job = create_job(client, employer_token, skills)

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

    def test_employer_cannot_view_other_candidates(self, client, employer_token, skills):
        job = create_job(client, employer_token, skills)

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
    def test_candidate_does_not_see_skill_requirements(
        self, client, employer_token, candidate_token, skills
    ):
        create_job(client, employer_token, skills)

        jobs = client.get("/api/jobs", headers=auth(candidate_token)).json()

        assert len(jobs) == 1
        assert "skills" not in jobs[0]
        assert "assessment_slots" not in jobs[0]
        assert "assessment_weight" not in jobs[0]

    def test_candidate_does_not_see_raw_description(
        self, client, employer_token, candidate_token, skills
    ):
        create_job(
            client,
            employer_token,
            skills,
            description_raw="Python bilmek zorunludur, Docker tercihen",
        )

        jobs = client.get("/api/jobs", headers=auth(candidate_token)).json()

        assert "description_raw" not in jobs[0]