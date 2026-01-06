import logging.config
from pathlib import Path

LOG_DIR = Path("/var/log/app")
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,  # important!
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s [%(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(asctime)s [%(client_addr)s] '
                   '"%(request_line)s" %(status_code)s',
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": str(LOG_FILE),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
        },
        "access_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "access",
            "filename": str(LOG_DIR / "access.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
        },
    },
    "loggers": {
        # Your application logs
        "app": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },

        # Uvicorn internal logs
        "uvicorn": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },

        # Uvicorn access logs
        "uvicorn.access": {
            "handlers": ["console", "access_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}
