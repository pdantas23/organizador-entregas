"""Testes para validação e normalização de campos."""
from __future__ import annotations

import pytest

from utils.validators import (
    normalize_client_name,
    normalize_budget_number,
    normalize_fields,
    parse_date,
    validate_delivery_fields,
)


# ── parse_date ────────────────────────────────────────────────────────────────

class TestParseDate:
    def test_data_valida(self):
        ok, d, err = parse_date("2026-05-06")
        assert ok
        assert d.isoformat() == "2026-05-06"
        assert err == ""

    def test_vazia_retorna_erro(self):
        ok, d, _ = parse_date("")
        assert not ok
        assert d is None

    def test_formato_invalido(self):
        ok, _, err = parse_date("06/05/2026")
        assert not ok
        assert "inválida" in err.lower()

    def test_data_impossivel(self):
        ok, _, _ = parse_date("2026-13-99")
        assert not ok

    def test_espacos_sao_removidos(self):
        ok, d, _ = parse_date("  2026-05-06  ")
        assert ok
        assert d.isoformat() == "2026-05-06"


# ── Normalização ──────────────────────────────────────────────────────────────

class TestNormalization:
    def test_cliente_title_case(self):
        assert normalize_client_name("supermercado CENTRAL") == "Supermercado Central"

    def test_cliente_remove_espacos_extras(self):
        assert normalize_client_name("  Loja   do  João  ") == "Loja Do João"

    def test_orcamento_upper(self):
        assert normalize_budget_number("orc-001") == "ORC-001"

    def test_orcamento_strip(self):
        assert normalize_budget_number("  ORC-001  ") == "ORC-001"

    def test_normalize_fields_converte_placa(self):
        client, budget, plates = normalize_fields("cliente", "orc-1", "5")
        assert plates == 5
        assert isinstance(plates, int)


# ── validate_delivery_fields ──────────────────────────────────────────────────

class TestValidateDeliveryFields:
    def _valid_args(self) -> dict:
        return dict(
            date_str="2026-05-06",
            client_name="Cliente",
            budget_number="ORC-001",
            plate_count_str="5",
            status="Nova entrega",
            period="Manhã",
            urgency="Alta",
        )

    def test_campos_validos_sem_erros(self):
        assert validate_delivery_fields(**self._valid_args()) == []

    def test_data_vazia(self):
        args = self._valid_args()
        args["date_str"] = ""
        assert len(validate_delivery_fields(**args)) >= 1

    def test_cliente_vazio(self):
        args = self._valid_args()
        args["client_name"] = "   "
        errors = validate_delivery_fields(**args)
        assert any("cliente" in e.lower() for e in errors)

    def test_placas_nao_numerico(self):
        args = self._valid_args()
        args["plate_count_str"] = "abc"
        errors = validate_delivery_fields(**args)
        assert any("inteiro" in e.lower() for e in errors)

    def test_placas_negativas(self):
        args = self._valid_args()
        args["plate_count_str"] = "-3"
        errors = validate_delivery_fields(**args)
        assert any("negativo" in e.lower() for e in errors)

    def test_todos_campos_vazios_retorna_multiplos_erros(self):
        errors = validate_delivery_fields("", "", "", "", "", "", "")
        assert len(errors) >= 5
