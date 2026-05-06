"""Testes para SessionService — gerenciamento do estado da sessão."""
from __future__ import annotations

import pytest

from services.session_service import SessionService


@pytest.fixture
def session() -> SessionService:
    return SessionService()


class TestAdd:
    def test_adiciona_entrega_valida(self, session, make_delivery):
        result = session.add(make_delivery())
        assert result.ok
        assert session.count() == 1

    def test_rejeita_duplicata_por_dedup_key(self, session, make_delivery):
        d1 = make_delivery(client_name="Empresa X", budget_number="ORC-001")
        d2 = make_delivery(client_name="empresa x", budget_number="orc-001")
        session.add(d1)
        result = session.add(d2)
        assert not result.ok
        assert session.count() == 1

    def test_aceita_mesmo_cliente_orcamento_diferente(self, session, make_delivery):
        session.add(make_delivery(budget_number="ORC-001"))
        result = session.add(make_delivery(budget_number="ORC-002"))
        assert result.ok
        assert session.count() == 2

    def test_mensagem_de_erro_informativa(self, session, make_delivery):
        d = make_delivery()
        session.add(d)
        result = session.add(make_delivery())
        assert not result.ok
        assert len(result.message) > 0


class TestRemove:
    def test_remove_por_id(self, session, make_delivery):
        d = make_delivery()
        session.add(d)
        removed = session.remove(d.id)
        assert removed
        assert session.count() == 0

    def test_remove_id_inexistente_retorna_false(self, session):
        assert not session.remove("id-que-nao-existe")

    def test_remove_correto_quando_multiplas(self, session, make_delivery):
        d1 = make_delivery(budget_number="ORC-001")
        d2 = make_delivery(budget_number="ORC-002")
        session.add(d1)
        session.add(d2)
        session.remove(d1.id)
        assert session.count() == 1
        assert session.get_sorted()[0].budget_number == "ORC-002"


class TestGetSorted:
    def test_retorna_lista_ordenada(self, session, make_delivery):
        session.add(make_delivery(period="Tarde",  urgency="Alta",  budget_number="ORC-1"))
        session.add(make_delivery(period="Manhã",  urgency="Baixa", budget_number="ORC-2"))
        session.add(make_delivery(period="Manhã",  urgency="Alta",  budget_number="ORC-3"))
        sorted_list = session.get_sorted()
        # Primeiro deve ser Manhã/Alta
        assert sorted_list[0].period == "Manhã" and sorted_list[0].urgency == "Alta"
        # Último deve ser Tarde/Alta
        assert sorted_list[-1].period == "Tarde"

    def test_vazio_retorna_lista_vazia(self, session):
        assert session.get_sorted() == []


class TestGetByDate:
    def test_agrupa_por_data(self, session, make_delivery):
        from datetime import date
        d1 = make_delivery(delivery_date=date(2026, 5, 6), budget_number="ORC-1")
        d2 = make_delivery(delivery_date=date(2026, 5, 7), budget_number="ORC-2")
        session.add(d1)
        session.add(d2)
        by_date = session.get_by_date()
        assert len(by_date) == 2
        assert date(2026, 5, 6) in by_date
        assert date(2026, 5, 7) in by_date


class TestClear:
    def test_limpa_tudo(self, session, make_delivery):
        session.add(make_delivery(budget_number="ORC-1"))
        session.add(make_delivery(budget_number="ORC-2"))
        session.clear()
        assert session.is_empty()
        assert session.count() == 0
