"""Global logging configuration for the project."""
import logging
import sys


def setup_logging():
    """
    Set up logging configuration.

    Returns:
        logger (logging.Logger): The logger object.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler("cookiecutter_setup.log"), logging.StreamHandler(sys.stdout)],
    )
    logger = logging.getLogger(__name__)
    return logger
