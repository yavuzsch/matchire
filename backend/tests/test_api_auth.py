from tests.conftest import auth


class TestRegister:
    def test_creates_user_and_returns_token(self, client):
        response = client.post(
            "/api/auth/register",
            json={
                "email": "new@test.com",
                "password": "password123",
                "full_name": "New User",
                "role": "candidate",
            },
        )

        assert response.status_code == 201
        assert "access_token" in response.json()

    def test_rejects_duplicate_email(self, client, candidate_token):
        response = client.post(
            "/api/auth/register",
            json={
                "email": "candidate@test.com",
                "password": "password123",
                "full_name": "Another",
                "role": "candidate",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "EMAIL_ALREADY_REGISTERED"

    def test_rejects_short_password(self, client):
        response = client.post(
            "/api/auth/register",
            json={
                "email": "short@test.com",
                "password": "1234567",
                "full_name": "Short",
                "role": "candidate",
            },
        )

        assert response.status_code == 422

    def test_rejects_admin_role(self, client):
        response = client.post(
            "/api/auth/register",
            json={
                "email": "admin@test.com",
                "password": "password123",
                "full_name": "Admin",
                "role": "admin",
            },
        )

        assert response.status_code == 422


class TestLogin:
    def test_returns_token_for_valid_credentials(self, client, candidate_token):
        response = client.post(
            "/api/auth/login",
            json={
                "email": "candidate@test.com",
                "password": "password123",
                "role": "candidate",
            },
        )

        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_rejects_wrong_password(self, client, candidate_token):
        response = client.post(
            "/api/auth/login",
            json={
                "email": "candidate@test.com",
                "password": "wrongpassword",
                "role": "candidate",
            },
        )

        assert response.status_code == 401
        assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"

    def test_rejects_role_mismatch(self, client, candidate_token):
        response = client.post(
            "/api/auth/login",
            json={
                "email": "candidate@test.com",
                "password": "password123",
                "role": "employer",
            },
        )

        assert response.status_code == 401
        assert response.json()["detail"]["code"] == "ROLE_MISMATCH"

    def test_wrong_password_takes_priority_over_role_mismatch(
        self, client, candidate_token
    ):
        response = client.post(
            "/api/auth/login",
            json={
                "email": "candidate@test.com",
                "password": "wrongpassword",
                "role": "employer",
            },
        )

        assert response.status_code == 401
        assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"


class TestMe:
    def test_returns_current_user(self, client, candidate_token):
        response = client.get("/api/auth/me", headers=auth(candidate_token))

        assert response.status_code == 200
        assert response.json()["email"] == "candidate@test.com"

    def test_rejects_missing_token(self, client):
        assert client.get("/api/auth/me").status_code == 401


class TestUpdateProfile:
    def test_updates_full_name(self, client, candidate_token):
        response = client.put(
            "/api/auth/me",
            json={"full_name": "New Name"},
            headers=auth(candidate_token),
        )

        assert response.status_code == 200
        assert response.json()["full_name"] == "New Name"

    def test_requires_authentication(self, client):
        response = client.put("/api/auth/me", json={"full_name": "New Name"})

        assert response.status_code == 401

    def test_rejects_short_name(self, client, candidate_token):
        response = client.put(
            "/api/auth/me",
            json={"full_name": "A"},
            headers=auth(candidate_token),
        )

        assert response.status_code == 422


class TestChangePassword:
    def test_changes_password_with_correct_current(self, client, candidate_token):
        response = client.put(
            "/api/auth/me/password",
            json={
                "current_password": "password123",
                "new_password": "newpassword456",
            },
            headers=auth(candidate_token),
        )

        assert response.status_code == 204

    def test_new_password_works_for_login(self, client, candidate_token):
        client.put(
            "/api/auth/me/password",
            json={
                "current_password": "password123",
                "new_password": "newpassword456",
            },
            headers=auth(candidate_token),
        )

        response = client.post(
            "/api/auth/login",
            json={
                "email": "candidate@test.com",
                "password": "newpassword456",
                "role": "candidate",
            },
        )

        assert response.status_code == 200

    def test_rejects_wrong_current_password(self, client, candidate_token):
        response = client.put(
            "/api/auth/me/password",
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword456",
            },
            headers=auth(candidate_token),
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INCORRECT_PASSWORD"

    def test_requires_authentication(self, client):
        response = client.put(
            "/api/auth/me/password",
            json={"current_password": "x", "new_password": "newpassword456"},
        )

        assert response.status_code == 401

    def test_rejects_short_new_password(self, client, candidate_token):
        response = client.put(
            "/api/auth/me/password",
            json={"current_password": "password123", "new_password": "short"},
            headers=auth(candidate_token),
        )

        assert response.status_code == 422