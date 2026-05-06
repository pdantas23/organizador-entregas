"""Validação e normalização de campos de entrega."""
from __future__ import annotations

from datetime import date
from typing import Optional


# ── Normalização ──────────────────────────────────────────────────────────────

def normalize_client_name(value: str) -> str:
    """Remove espaços extras e aplica Title Case."""
    return " ".join(value.split()).title()


def normalize_budget_number(value: str) -> str:
    """Remove espaços extras e converte para maiúsculas."""
    return value.strip().upper()


def normalize_plate_count(value: str) -> str:
    return value.strip()


# ── Validação de data ─────────────────────────────────────────────────────────

def parse_date(value: str) -> tuple[bool, Optional[date], str]:
    """
    Valida e converte uma string ISO (YYYY-MM-DD) para date.

    Returns:
        (ok, parsed_date, error_message)
    """
    raw = value.strip() if value else ""
    if not raw:
        return False, None, "Data da entrega é obrigatória."
    try:
        return True, date.fromisoformat(raw), ""
    except ValueError:
        return False, None, f"Data inválida '{raw}'. Use o formato AAAA-MM-DD."


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
    """
    Valida todos os campos de uma entrega.
    Retorna lista de mensagens de erro (vazia = tudo válido).
    """
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
    """
    Normaliza e converte os campos de texto.
    Presume que validate_delivery_fields() já foi chamado sem erros.
    """
    return (
        normalize_client_name(client_name),
        normalize_budget_number(budget_number),
        int(plate_count_str.strip()),
    )
