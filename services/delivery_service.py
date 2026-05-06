"""
DeliveryService — única fonte de ordenação da aplicação.

REGRA: nenhuma outra camada (UI, exportador, persistência) deve ordenar
entregas por conta própria. Toda ordenação passa por aqui.
"""
from __future__ import annotations

from models.delivery import Delivery
from utils.constants import PERIOD_ORDER, URGENCY_ORDER


class DeliveryService:
    """Regras de negócio para classificação e busca de duplicatas."""

    def sort(self, deliveries: list[Delivery]) -> list[Delivery]:
        """
        Ordena entregas pela hierarquia obrigatória:
          1. data (ascendente)
          2. período  (Manhã < Tarde)
          3. urgência (Alta < Média < Baixa)
          4. nome do cliente (alfabético, desempate)
        """
        def _key(d: Delivery) -> tuple:
            return (
                d.delivery_date,
                PERIOD_ORDER.get(d.period, 99),
                URGENCY_ORDER.get(d.urgency, 99),
                d.client_name.lower(),
            )

        return sorted(deliveries, key=_key)

    def find_duplicate(
        self,
        candidate: Delivery,
        existing: list[Delivery],
    ) -> Delivery | None:
        """
        Verifica se `candidate` duplica algo em `existing`.
        Prioridade: mesmo id → mesmo dedup_key.
        Retorna a entrega conflitante ou None.
        """
        for d in existing:
            if d.id == candidate.id:
                return d
            if d.dedup_key() == candidate.dedup_key():
                return d
        return None
