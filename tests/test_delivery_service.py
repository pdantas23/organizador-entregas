"""Testes para DeliveryService — ordenação e detecção de duplicatas."""
from __future__ import annotations

from datetime import date

import pytest

from models.delivery import Delivery
from services.delivery_service import DeliveryService


@pytest.fixture
def svc() -> DeliveryService:
    return DeliveryService()


# ── Ordenação ─────────────────────────────────────────────────────────────────

class TestSort:
    def test_periodo_manha_antes_tarde(self, svc, make_delivery):
        tarde = make_delivery(period="Tarde")
        manha = make_delivery(period="Manhã", budget_number="ORC-002")
        result = svc.sort([tarde, manha])
        assert result[0].period == "Manhã"
        assert result[1].period == "Tarde"

    def test_urgencia_dentro_do_periodo(self, svc, make_delivery):
        baixa = make_delivery(urgency="Baixa",  budget_number="ORC-A")
        alta  = make_delivery(urgency="Alta",   budget_number="ORC-B")
        media = make_delivery(urgency="Média",  budget_number="ORC-C")
        result = svc.sort([baixa, media, alta])
        assert [d.urgency for d in result] == ["Alta", "Média", "Baixa"]

    def test_data_antes_periodo(self, svc, make_delivery):
        d_tomorrow = make_delivery(
            delivery_date=date(2026, 5, 7),
            period="Manhã", urgency="Alta", budget_number="ORC-FUTURE",
        )
        d_today = make_delivery(
            delivery_date=date(2026, 5, 6),
            period="Tarde", urgency="Baixa", budget_number="ORC-TODAY",
        )
        result = svc.sort([d_tomorrow, d_today])
        assert result[0].delivery_date == date(2026, 5, 6)
        assert result[1].delivery_date == date(2026, 5, 7)

    def test_desempate_por_nome_cliente(self, svc, make_delivery):
        z = make_delivery(client_name="Zoológico", budget_number="ORC-Z")
        a = make_delivery(client_name="Academia",  budget_number="ORC-A")
        result = svc.sort([z, a])
        assert result[0].client_name == "Academia"
        assert result[1].client_name == "Zoológico"

    def test_lista_vazia_retorna_vazia(self, svc):
        assert svc.sort([]) == []

    def test_unico_elemento_permanece(self, svc, make_delivery):
        d = make_delivery()
        assert svc.sort([d]) == [d]

    def test_ordem_completa_hierarquica(self, svc, make_delivery):
        """Alta/Manhã deve vir antes de Média/Manhã, antes de Alta/Tarde."""
        alta_tarde  = make_delivery(period="Tarde",  urgency="Alta",  budget_number="ORC-1")
        media_manha = make_delivery(period="Manhã",  urgency="Média", budget_number="ORC-2")
        alta_manha  = make_delivery(period="Manhã",  urgency="Alta",  budget_number="ORC-3")
        result = svc.sort([alta_tarde, media_manha, alta_manha])
        assert result[0].urgency == "Alta"  and result[0].period == "Manhã"
        assert result[1].urgency == "Média" and result[1].period == "Manhã"
        assert result[2].urgency == "Alta"  and result[2].period == "Tarde"


# ── Detecção de duplicatas ────────────────────────────────────────────────────

class TestFindDuplicate:
    def test_sem_duplicata(self, svc, make_delivery):
        existing = [make_delivery(budget_number="ORC-001")]
        candidate = make_delivery(budget_number="ORC-002")
        assert svc.find_duplicate(candidate, existing) is None

    def test_duplicata_por_dedup_key(self, svc, make_delivery):
        d1 = make_delivery(client_name="Cliente A", budget_number="ORC-001")
        d2 = make_delivery(client_name="cliente a", budget_number="orc-001")  # mesmo conteúdo, case diferente
        assert svc.find_duplicate(d2, [d1]) is not None

    def test_duplicata_por_id(self, svc, make_delivery):
        d1 = make_delivery(budget_number="ORC-001")
        d2 = Delivery(
            delivery_date=d1.delivery_date,
            client_name="Outro Nome",
            budget_number="ORC-999",
            plate_count=99,
            status="Finalização",
            period="Tarde",
            urgency="Baixa",
            id=d1.id,  # mesmo id!
        )
        assert svc.find_duplicate(d2, [d1]) is d1

    def test_lista_vazia_nunca_duplica(self, svc, make_delivery):
        assert svc.find_duplicate(make_delivery(), []) is None
