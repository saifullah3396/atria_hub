import logging

from atria_hub.config import settings


def get_logger(name: str) -> logging.Logger:
    logger = (
        logging.getLogger(name) if name else logging.getLogger(settings.SERVICE_NAME)
    )

    logging.basicConfig(
        level=logging.INFO, format=settings.LOG_FORMAT, datefmt=settings.DATE_FORMAT
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("lakefs-spec").setLevel(logging.WARNING)

    return logger
