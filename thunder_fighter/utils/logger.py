import logging
import os
import sys

# Define log levels
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# Default log level (can be overridden by environment variable)
DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVEL_ENV_VAR = "THUNDER_FIGHTER_LOG_LEVEL"

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name="thunder_fighter", level=None):
    """Configures and returns a logger instance."""

    # Determine log level
    env_level = os.environ.get(LOG_LEVEL_ENV_VAR, DEFAULT_LOG_LEVEL).upper()
    log_level_str = level.upper() if level else env_level
    log_level = LOG_LEVELS.get(log_level_str, logging.INFO)

    # Get the logger
    logger = logging.getLogger(name)

    # Prevent adding multiple handlers if logger already exists
    if logger.hasHandlers():
        logger.setLevel(log_level)
        return logger

    logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional: Add file handler (e.g., log to 'game.log')
    # try:
    #     log_dir = 'logs'
    #     if not os.path.exists(log_dir):
    #         os.makedirs(log_dir)
    #     file_handler = logging.FileHandler(os.path.join(log_dir, 'game.log'))
    #     file_handler.setLevel(log_level)
    #     file_handler.setFormatter(formatter)
    #     logger.addHandler(file_handler)
    # except Exception as e:
    #     logger.warning(f"Could not setup file logging: {e}")

    logger.info(f"Logger '{name}' initialized with level {log_level_str}")
    return logger


# Create a default logger instance for easy import
logger = setup_logger()

if __name__ == "__main__":
    # Example usage
    print("Testing logger setup...")
    test_logger = setup_logger("test_module", level="DEBUG")
    test_logger.debug("This is a debug message.")
    test_logger.info("This is an info message.")
    test_logger.warning("This is a warning message.")
    test_logger.error("This is an error message.")
    test_logger.critical("This is a critical message.")

    # Test default logger
    logger.info("Testing the default logger instance.")
    print("Logger test complete.")
