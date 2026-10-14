from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ClauseIQ"
    API_V1_STR: str = "/api/v1"
    
    # Backend CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    # Database
    DATABASE_URL: str = "sqlite:///./test.db"

    # Gemini
    GEMINI_API_KEY: str = "YOUR_GEMINI_API_KEY"

    # JWT Settings
    JWT_SECRET_KEY: str = "9a4a43b8760240f9a74476eee2a0ab1d0f852b7c6a51d9607db715206c9a8f4c"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()

