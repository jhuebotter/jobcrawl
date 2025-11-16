import logging
import sys

def setup_logging():
    """
    Sets up structured logging for the application.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("server.log", mode="a")
        ]
    )

def get_logger(name: str):
    """
    Returns a logger instance.
    """
    return logging.getLogger(name)
