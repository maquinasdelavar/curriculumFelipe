from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Autopeças API"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 480
    database_url: str = "sqlite+aiosqlite:///./app.db"
    debug: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()