# app/utils/logger.py

import logging
import os

def setup_logger(name: str, log_file: str = "app.log", level=logging.INFO):
    """
    Sets up a logger for the application.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    # Also print logs to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Example usage
if __name__ == "__main__":
    log = setup_logger("webscraper", "logs/webscraper.log")
    log.info("Logger initialized successfully!")
