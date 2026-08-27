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
            json={"email": "candidate@test.com", "password": "password123"},
        )

        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_rejects_wrong_password(self, client, candidate_token):
        response = client.post(
            "/api/auth/login",
            json={"email": "candidate@test.com", "password": "wrongpassword"},
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