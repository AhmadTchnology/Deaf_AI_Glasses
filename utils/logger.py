import sys
from loguru import logger

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

logger.remove()

logger.add(
    sys.stderr,
    format=LOG_FORMAT,
    level="DEBUG",
    colorize=True,
)

logger.add(
    "logs/smart_glasses.log",
    format=LOG_FORMAT,
    level="DEBUG",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
)

__all__ = ["logger"]
