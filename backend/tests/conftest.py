import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

TEST_SCHEMA = "test"

engine = create_engine(settings.DATABASE_URL).execution_options(
    schema_translate_map={None: TEST_SCHEMA}
)
TestSession = sessionmaker(bind=engine)


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def db():
    with engine.begin() as conn:
        conn.execute(text(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE"))
        conn.execute(text(f"CREATE SCHEMA {TEST_SCHEMA}"))

    Base.metadata.create_all(bind=engine)
    session = TestSession()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def employer_token(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "employer@test.com",
            "password": "password123",
            "full_name": "Test Employer",
            "role": "employer",
        },
    )
    return response.json()["access_token"]


@pytest.fixture
def candidate_token(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "candidate@test.com",
            "password": "password123",
            "full_name": "Test Candidate",
            "role": "candidate",
        },
    )
    return response.json()["access_token"]