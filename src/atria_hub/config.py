from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "atria"

    ATRIAX_URL: str
    ATRIAX_STORAGE_URL: str
    ATRIAX_ANON_KEY: str

    LOG_FORMAT: str = "%(message)s"
    DATE_FORMAT: str = "[%X]"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()  # type: ignore
