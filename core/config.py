from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    DATABASE_URL: str
    APP_ENV: str = "development"
    DEBUG: bool = False

    @property
    def is_dev(self) -> bool:
        return self.APP_ENV == "development"


settings = Settings()
