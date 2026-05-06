"""SessionService — estado da sessão atual da UI."""
from __future__ import annotations

import dataclasses
from collections import defaultdict
from datetime import date
from typing import Optional

from models.delivery import Delivery
from services.delivery_service import DeliveryService
from utils.logger import get_logger

log = get_logger("session")


class AddResult:
    __slots__ = ("ok", "message")

    def __init__(self, ok: bool, message: str) -> None:
        self.ok = ok
        self.message = message

    def __bool__(self) -> bool:
        return self.ok


class SessionService:
    def __init__(self, delivery_svc: DeliveryService | None = None) -> None:
        self._svc = delivery_svc or DeliveryService()
        self._deliveries: list[Delivery] = []

    # ── Mutação ───────────────────────────────────────────────────────────────

    def add(self, delivery: Delivery) -> AddResult:
        duplicate = self._svc.find_duplicate(delivery, self._deliveries)
        if duplicate is not None:
            msg = (
                f"Entrega duplicada: '{duplicate.client_name}' "
                f"({duplicate.budget_number}) já está na lista."
            )
            log.warning("Duplicata bloqueada: %s", delivery.dedup_key())
            return AddResult(ok=False, message=msg)

        self._deliveries.append(delivery)
        log.info("Adicionada: %s | %s", delivery.client_name, delivery.budget_number)
        return AddResult(ok=True, message="Entrega adicionada com sucesso.")

    def update(self, delivery_id: str, updated: Delivery) -> AddResult:
        """
        Substitui a entrega com `delivery_id` pelos novos dados.
        O ID original é preservado; verifica conflitos com as demais.
        """
        if self.get_by_id(delivery_id) is None:
            return AddResult(ok=False, message="Entrega não encontrada.")

        others = [d for d in self._deliveries if d.id != delivery_id]
        duplicate = self._svc.find_duplicate(updated, others)
        if duplicate is not None:
            return AddResult(
                ok=False,
                message=f"Conflito: '{duplicate.client_name}' ({duplicate.budget_number}) já existe.",
            )

        # Preserva o ID original usando dataclasses.replace
        updated_with_id = dataclasses.replace(updated, id=delivery_id)
        self._deliveries = [
            updated_with_id if d.id == delivery_id else d
            for d in self._deliveries
        ]
        log.info("Atualizada: id=%s → %s | %s", delivery_id, updated.client_name, updated.budget_number)
        return AddResult(ok=True, message="Entrega atualizada com sucesso.")

    def remove(self, delivery_id: str) -> bool:
        before = len(self._deliveries)
        self._deliveries = [d for d in self._deliveries if d.id != delivery_id]
        removed = len(self._deliveries) < before
        if removed:
            log.info("Removida: id=%s", delivery_id)
        return removed

    def clear(self) -> None:
        count = len(self._deliveries)
        self._deliveries.clear()
        log.info("Sessão limpa (%d entrega(s))", count)

    # ── Leitura ───────────────────────────────────────────────────────────────

    def get_by_id(self, delivery_id: str) -> Optional[Delivery]:
        for d in self._deliveries:
            if d.id == delivery_id:
                return d
        return None

    def get_sorted(self) -> list[Delivery]:
        return self._svc.sort(self._deliveries)

    def get_by_date(self) -> dict[date, list[Delivery]]:
        groups: dict[date, list[Delivery]] = defaultdict(list)
        for d in self.get_sorted():
            groups[d.delivery_date].append(d)
        return dict(sorted(groups.items()))

    def is_empty(self) -> bool:
        return len(self._deliveries) == 0

    def count(self) -> int:
        return len(self._deliveries)
