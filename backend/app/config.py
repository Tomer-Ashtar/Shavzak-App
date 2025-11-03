from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Workers Jobs Manager API"
    environment: str = "development"
    database_url: str = "sqlite:///./backend/app.db"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        env_file = ".env"
        env_prefix = "WJM_"
        case_sensitive = False


settings = Settings()

