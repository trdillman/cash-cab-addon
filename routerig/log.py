from __future__ import annotations

import logging

LOGGER_NAME = "cashcab.routerig"


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)


def configure(level: int | None = None) -> None:
    logger = get_logger()
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter("[%(name)s] %(levelname)s: %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    
    logger.setLevel(logging.INFO if level is None else level)

