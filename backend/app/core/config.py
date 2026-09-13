from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DATABASE_URL: str
    SECRET_KEY: str
    LLM_API_KEY: str
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemini-3.1-flash-lite"
    CORS_ORIGINS: str = "http://localhost:5173"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    DEFAULT_LANGUAGE: str = "tr"


settings = Settings()