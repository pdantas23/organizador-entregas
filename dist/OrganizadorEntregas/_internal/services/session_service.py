"""
SessionService — estado da sessão atual da UI.

Responsabilidades:
  - Manter a lista em memória de entregas ainda não persistidas.
  - Impedir duplicatas na própria fila.
  - Expor a lista SEMPRE ordenada (via DeliveryService).
  - A UI nunca gerencia a lista diretamente.

NÃO persiste nem exporta: essas responsabilidades ficam em
PersistenceService e ExcelExporter, orquestrados pelo app.py.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date

from models.delivery import Delivery
from services.delivery_service import DeliveryService
from utils.logger import get_logger

log = get_logger("session")


class AddResult:
    """Resultado de uma tentativa de adição."""
    __slots__ = ("ok", "message")

    def __init__(self, ok: bool, message: str) -> None:
        self.ok = ok
        self.message = message

    def __bool__(self) -> bool:
        return self.ok


class SessionService:
    """Gerencia a fila de entregas da sessão atual."""

    def __init__(self, delivery_svc: DeliveryService | None = None) -> None:
        self._svc = delivery_svc or DeliveryService()
        self._deliveries: list[Delivery] = []

    # ── Mutação ───────────────────────────────────────────────────────────────

    def add(self, delivery: Delivery) -> AddResult:
        """
        Adiciona uma entrega à sessão.
        Rejeita se já existir uma com o mesmo id ou dedup_key.
        """
        duplicate = self._svc.find_duplicate(delivery, self._deliveries)
        if duplicate is not None:
            msg = (
                f"Entrega duplicada: '{duplicate.client_name}' "
                f"({duplicate.budget_number}) já está na lista."
            )
            log.warning("Tentativa de duplicata bloqueada: %s", delivery.dedup_key())
            return AddResult(ok=False, message=msg)

        self._deliveries.append(delivery)
        log.info("Adicionada à sessão: %s | %s", delivery.client_name, delivery.budget_number)
        return AddResult(ok=True, message="Entrega adicionada com sucesso.")

    def remove(self, delivery_id: str) -> bool:
        """Remove por id. Retorna True se algo foi removido."""
        before = len(self._deliveries)
        self._deliveries = [d for d in self._deliveries if d.id != delivery_id]
        removed = len(self._deliveries) < before
        if removed:
            log.info("Removida da sessão: id=%s", delivery_id)
        return removed

    def clear(self) -> None:
        count = len(self._deliveries)
        self._deliveries.clear()
        log.info("Sessão limpa (%d entrega(s) descartada(s))", count)

    # ── Leitura ───────────────────────────────────────────────────────────────

    def get_sorted(self) -> list[Delivery]:
        """Retorna todas as entregas da sessão ordenadas."""
        return self._svc.sort(self._deliveries)

    def get_by_date(self) -> dict[date, list[Delivery]]:
        """
        Agrupa entregas ordenadas por data.
        Útil para gerar um arquivo por data na exportação.
        """
        groups: dict[date, list[Delivery]] = defaultdict(list)
        for d in self.get_sorted():
            groups[d.delivery_date].append(d)
        return dict(sorted(groups.items()))

    def is_empty(self) -> bool:
        return len(self._deliveries) == 0

    def count(self) -> int:
        return len(self._deliveries)
