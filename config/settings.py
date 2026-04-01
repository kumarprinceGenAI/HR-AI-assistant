from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    PRIMARY_MODEL: str = "models/gemini-2.5-flash"
    FALLBACK_MODEL: str = "models/gemini-2.0-flash-lite"
    
    # Auth
    JWT_SECRET: str = "super_secret_hr_key"
    
    # Optional parameters for future use
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()