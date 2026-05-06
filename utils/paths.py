"""Gerenciamento centralizado de caminhos multiplataforma."""
from __future__ import annotations

from datetime import date
from pathlib import Path

MONTHS_PT: dict[int, str] = {
    1: "janeiro", 2: "fevereiro", 3: "março",    4: "abril",
    5: "maio",    6: "junho",     7: "julho",     8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro",
}


def _hidden_app_dir() -> Path:
    """Pasta de dados da aplicação, oculta no home do usuário."""
    p = Path.home() / ".organizador"
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_data_dir() -> Path:
    p = _hidden_app_dir() / "data"
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_export_dir(delivery_date: date) -> Path:
    """~/Desktop/entregas/YYYY/nome-do-mês/"""
    month_name = MONTHS_PT[delivery_date.month]
    p = Path.home() / "Desktop" / "entregas" / str(delivery_date.year) / month_name
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_json_path(delivery_date: date) -> Path:
    return get_data_dir() / f"entregas-{delivery_date.isoformat()}.json"


def get_excel_path(delivery_date: date) -> Path:
    """Nome do arquivo no padrão brasileiro: entregas-DD-MM-AA.xlsx"""
    filename = f"entregas-{delivery_date.strftime('%d-%m-%y')}.xlsx"
    return get_export_dir(delivery_date) / filename
