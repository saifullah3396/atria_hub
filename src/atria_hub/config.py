from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME = "atria"

    ATRIAX_URL: str
    ATRIAX_ANON_KEY: str

    LOG_FORMAT = "%(message)s"
    DATE_FORMAT = "[%X]"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()  # type: ignore
