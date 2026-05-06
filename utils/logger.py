"""Logging da aplicação — saída apenas no console (sem criar arquivos)."""
from __future__ import annotations

import logging

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_initialized = False


def setup_logging() -> None:
    """Inicializa o logger raiz. Chame uma vez em main.py."""
    global _initialized
    if _initialized:
        return

    root = logging.getLogger("organizador")
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
    root.addHandler(ch)

    _initialized = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"organizador.{name}")
