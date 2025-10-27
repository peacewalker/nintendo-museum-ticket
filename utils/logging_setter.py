import logging
import os
from typing import Optional

def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Creates a configured logger for a specific monitor.

    Args:
        name: Logger/Monitor name
        log_file: Optional log file name.
                 If None, uses {name.lower()}_monitor.log

    Returns:
        logging.Logger: Configured logger
    """
    # Ensure the "logs" folder exists
    log_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_folder, exist_ok=True)

    # Create logger with the given name
    logger = logging.getLogger(name)

    # If logger already has handlers, return it
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File Handler
    if log_file is None:
        log_file = f"{name.lower()}_monitor.log"
    fh = logging.FileHandler(
        os.path.join(log_folder, log_file),
        encoding="utf-8"
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console Handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger