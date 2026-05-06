"""Configuração centralizada de logging."""
from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

from utils.paths import get_logs_dir

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_MAX_BYTES = 5 * 1024 * 1024   # 5 MB por arquivo
_BACKUP_COUNT = 3               # mantém 3 arquivos de backup

_initialized = False


def setup_logging() -> None:
    """
    Configura o logger raiz da aplicação.
    Deve ser chamado UMA VEZ ao iniciar o processo (em main.py).
    """
    global _initialized
    if _initialized:
        return

    log_file: Path = get_logs_dir() / "app.log"
    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    root = logging.getLogger("organizador")
    root.setLevel(logging.DEBUG)

    # Arquivo com rotação automática
    fh = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    root.addHandler(fh)

    # Console (apenas INFO+ em desenvolvimento)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    _initialized = True
    root.info("Logging inicializado → %s", log_file)


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger filho do namespace 'organizador'."""
    return logging.getLogger(f"organizador.{name}")
