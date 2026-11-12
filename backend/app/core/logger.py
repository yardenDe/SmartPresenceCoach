import logging
from logging.config import dictConfig

from core.settings import get_settings


def setup_logging() -> None:
    settings = get_settings()
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    }
    if settings.LOG_FILE_PATH:
        handlers["file"] = {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": settings.LOG_FILE_PATH,
            "encoding": "utf-8",
        }

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                    "datefmt": "%Y-%m-%dT%H:%M:%S%z",
                }
            },
            "handlers": handlers,
            "root": {
                "level": settings.LOG_LEVEL,
                "handlers": settings.HANDLERS,
            },
        }
    )
     
    logging.getLogger("groq").setLevel(logging.WARNING)
    logging.getLogger("numba").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
