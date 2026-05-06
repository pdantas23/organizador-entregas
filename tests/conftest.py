"""Fixtures compartilhadas entre os testes."""
from __future__ import annotations

from datetime import date

import pytest

from models.delivery import Delivery


@pytest.fixture
def base_date() -> date:
    return date(2026, 5, 6)


@pytest.fixture
def make_delivery(base_date):
    """
    Factory de Delivery com valores padrão sobrescrevíveis.

    Uso:
        def test_foo(make_delivery):
            d = make_delivery(urgency="Baixa", period="Tarde")
    """
    def _factory(**overrides) -> Delivery:
        defaults = dict(
            delivery_date=base_date,
            client_name="Cliente Teste",
            budget_number="ORC-001",
            plate_count=1,
            status="Nova entrega",
            period="Manhã",
            urgency="Alta",
        )
        defaults.update(overrides)
        return Delivery(**defaults)

    return _factory
