from app.models import User, UserRole


def test_database_works(db):
    user = User(
        email="test@test.com",
        hashed_password="x",
        full_name="Test",
        role=UserRole.CANDIDATE,
    )
    db.add(user)
    db.commit()

    assert db.query(User).count() == 1