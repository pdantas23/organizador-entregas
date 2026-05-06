"""
Gerenciamento centralizado de caminhos multiplataforma.

  - Dados internos (JSON)  →  ~/.organizador/data/       (pasta oculta)
  - Logs                   →  ~/.organizador/logs/        (pasta oculta)
  - Exportações Excel      →  ~/Desktop/entregas/YYYY/MM/ (visível ao usuário)
"""
from __future__ import annotations

from datetime import date
from pathlib import Path


def _hidden_app_dir() -> Path:
    """Pasta de dados da aplicação, oculta no home do usuário."""
    p = Path.home() / ".organizador"
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_data_dir() -> Path:
    p = _hidden_app_dir() / "data"
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_logs_dir() -> Path:
    p = _hidden_app_dir() / "logs"
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_export_dir(delivery_date: date) -> Path:
    """Retorna (e cria) a pasta ano/mês dentro de ~/Desktop/entregas/."""
    p = Path.home() / "Desktop" / "entregas" / str(delivery_date.year) / f"{delivery_date.month:02d}"
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_json_path(delivery_date: date) -> Path:
    return get_data_dir() / f"entregas-{delivery_date.isoformat()}.json"


def get_excel_path(delivery_date: date) -> Path:
    return get_export_dir(delivery_date) / f"entregas-{delivery_date.isoformat()}.xlsx"
