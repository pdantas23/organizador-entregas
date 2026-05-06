"""Validação e normalização de campos de entrega."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional


# ── Normalização ──────────────────────────────────────────────────────────────

def normalize_client_name(value: str) -> str:
    return " ".join(value.split()).title()


def normalize_budget_number(value: str) -> str:
    return value.strip().upper()


def normalize_plate_count(value: str) -> str:
    return value.strip()


# ── Validação de data ─────────────────────────────────────────────────────────

def parse_date(value: str) -> tuple[bool, Optional[date], str]:
    """
    Aceita os formatos:
      - DD/MM/AAAA  (padrão brasileiro)
      - DD/MM/AA    (ano abreviado)
      - AAAA-MM-DD  (ISO, fallback)
    """
    raw = value.strip() if value else ""
    if not raw:
        return False, None, "Data da entrega é obrigatória."

    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
        try:
            return True, datetime.strptime(raw, fmt).date(), ""
        except ValueError:
            continue

    return False, None, f"Data inválida '{raw}'. Use o formato DD/MM/AAAA."


# ── Validação de campos ───────────────────────────────────────────────────────

def validate_delivery_fields(
    date_str: str,
    client_name: str,
    budget_number: str,
    plate_count_str: str,
    status: str,
    period: str,
    urgency: str,
) -> list[str]:
    errors: list[str] = []

    ok, _, err = parse_date(date_str)
    if not ok:
        errors.append(err)

    if not client_name or not client_name.strip():
        errors.append("Nome do cliente é obrigatório.")

    if not budget_number or not budget_number.strip():
        errors.append("Número do orçamento é obrigatório.")

    if not plate_count_str or not plate_count_str.strip():
        errors.append("Número de placas é obrigatório.")
    else:
        try:
            count = int(plate_count_str.strip())
            if count < 0:
                errors.append("Número de placas não pode ser negativo.")
        except ValueError:
            errors.append("Número de placas deve ser um número inteiro.")

    if not status:
        errors.append("Status é obrigatório.")
    if not period:
        errors.append("Período é obrigatório.")
    if not urgency:
        errors.append("Urgência é obrigatória.")

    return errors


def normalize_fields(
    client_name: str,
    budget_number: str,
    plate_count_str: str,
) -> tuple[str, str, int]:
    return (
        normalize_client_name(client_name),
        normalize_budget_number(budget_number),
        int(plate_count_str.strip()),
    )
