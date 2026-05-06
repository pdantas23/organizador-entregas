"""
Gerenciamento centralizado de caminhos multiplataforma.

Regras:
  - Em desenvolvimento (não frozen): usa o diretório raiz do projeto.
  - Em produção (frozen/PyInstaller):  usa ~/Desktop/entregas/ como base.
  - Exportações Excel:  SEMPRE em ~/Desktop/entregas/
  - JSON (fonte de verdade): base/data/
  - Logs:                    base/logs/
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path


def _app_base() -> Path:
    """Diretório-base para dados e logs."""
    if getattr(sys, "frozen", False):
        # Executável PyInstaller: persiste dados próximos ao Desktop, não no
        # diretório temporário de extração (sys._MEIPASS).
        return Path.home() / "Desktop" / "entregas"
    # Desenvolvimento: usa a raiz do projeto (dois níveis acima de utils/).
    return Path(__file__).resolve().parent.parent


def get_data_dir() -> Path:
    p = _app_base() / "data"
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_logs_dir() -> Path:
    p = _app_base() / "logs"
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_export_dir() -> Path:
    """Destino dos arquivos Excel — sempre no Desktop do usuário."""
    p = Path.home() / "Desktop" / "entregas"
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_json_path(delivery_date: date) -> Path:
    return get_data_dir() / f"entregas-{delivery_date.isoformat()}.json"


def get_excel_path(delivery_date: date) -> Path:
    return get_export_dir() / f"entregas-{delivery_date.isoformat()}.xlsx"
