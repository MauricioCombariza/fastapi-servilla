import logging
from logging.config import dictConfig
from app.config import config, DevConfig
from logging import Filter

def obfuscated(email: str, obfuscated_length: int) -> str:
    characters = email[:obfuscated_length]
    first, last = characters.split("@")
    return characters + ("*" * (len(first) - obfuscated_length)) + "@" + last

class EmailObfuscationFilter(logging.Filter):
    def __init__(self, name:str = "", obfuscated_length: int = 2) -> None:
        super().__init__()
        self.obfuscated_length = obfuscated_length
        
    def filter(self, record: logging.LogRecord) -> bool:
        if "email" in record.__dict__:
            record.email = obfuscated(record.email, self.obfuscated_length)
        return True
    
handlers = ["default", "rotating_file"]
if isinstance(config, DevConfig):
    handlers = ["default", "rotating_file", "logtail"]
    
def configure_logging() -> None:
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "email_obfuscation": {
                "()": EmailObfuscationFilter,
                "obfuscated_length": 2 if isinstance(config, DevConfig) else 0
            }
        },
        "formatters": {
            "console": {
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "format": "%(name)s - %(levelname)s - %(message)s"
            },
            "file": {
                "class": "logging.Formatter",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "format": "%(asctime)s%(msecs)03dz %(levelname)-8s %(name)s:%(lineno)d %(message)s"
            }
        },
        "handlers": {
            "default": {
                "class": "rich.logging.RichHandler",
                "formatter": "console",
                "level": "DEBUG",
                "filters": ["email_obfuscation"]
            },
            "rotating_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "file",
                "filename": "app.log",
                "level": "DEBUG",
                "maxBytes": 1024*1024,
                "backupCount": 5,
                "encoding": "utf8",
                "filters": ["email_obfuscation"]
            },
            "logtail": {
                "class": "logtail.LogtailHandler",
                "source_token": config.LOGTAIL_API_KEY,
                "level": "DEBUG",
                "formatter": "console",
                "filters": ["email_obfuscation"]
            }
        },
        "loggers": {
            "uvicorn": {
                "level": "INFO",
                "handlers": ["default", "rotating_file"],
            },
            "app": {
                "level": "DEBUG" if isinstance(config, dict) else "INFO",
                "handlers": handlers,
                "propagate": False,
            },
            "databases": {
                "level": "WARNING",
                "handlers": ["default"],
        },
        "aiosqlite": {
            "level": "WARNING",
            "handlers": ["default"],
        }
        }
    })