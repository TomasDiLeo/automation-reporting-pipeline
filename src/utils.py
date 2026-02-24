from loguru import logger
import sys
from pathlib import Path


def setup_logging(log_dir: str):
    """
    Setups a logger that writes to both console and a file in the specified log directory.
     - Console logs are at INFO level.
     - File logs are at INFO level, rotated daily, and retained for 7 days.
     - Ensures the log directory exists.
     - Removes the default logger to prevent duplicate logs.
     - Logs are written to 'pipeline.log' in the specified log directory.
     - Logs include timestamps, log levels, and messages.
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    logger.remove()  # remove default logger

    logger.add(sys.stdout, level="INFO")

    logger.add(
        f"{log_dir}/pipeline.log",
        rotation="1 day",
        retention="7 days",
        level="INFO",
    )