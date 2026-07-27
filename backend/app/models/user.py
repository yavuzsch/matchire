import enum

from sqlalchemy import Column, Integer, String, Enum as SAEnum

from app.core.database import Base


class UserRole(str, enum.Enum):
    EMPLOYER = "employer"
    CANDIDATE = "candidate"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), nullable=False)