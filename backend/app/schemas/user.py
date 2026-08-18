from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import UserRole


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=2, max_length=100)
    role: UserRole

    @field_validator("role")
    @classmethod
    def block_admin(cls, value: UserRole) -> UserRole:
        if value == UserRole.ADMIN:
            raise ValueError("invalid role")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"