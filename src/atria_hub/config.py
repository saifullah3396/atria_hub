from atria_core.utilities.imports import _get_package_base_path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "atria"

    ATRIAX_URL: str
    ATRIAX_STORAGE_URL: str
    ATRIAX_ANON_KEY: str

    LOG_FORMAT: str = "%(message)s"
    DATE_FORMAT: str = "[%X]"

    class Config:
        env_file = _get_package_base_path("atria_hub") + "/.env"
        extra = "ignore"


settings = Settings()  # type: ignore
