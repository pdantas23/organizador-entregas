"""
PersistenceService — JSON como fonte de verdade.

Responsabilidades:
  - Ler entregas de um arquivo JSON por data.
  - Salvar/atualizar entregas com deduplicação.
  - Proteger escrita com lock de arquivo (segurança contra dupla instância).
"""
from __future__ import annotations

import json
import os
import time
from datetime import date
from pathlib import Path

from models.delivery import Delivery
from services.delivery_service import DeliveryService
from utils.logger import get_logger
from utils.paths import get_json_path

log = get_logger("persistence")


# ── Lock de arquivo simples e portátil ───────────────────────────────────────

class _FileLock:
    """
    Lock exclusivo baseado em arquivo-sentinela (O_CREAT | O_EXCL).
    Funciona em macOS e Windows sem dependências externas.
    """

    def __init__(self, target: Path, timeout: float = 5.0) -> None:
        self._lock_path = target.with_suffix(".lock")
        self._timeout = timeout

    def __enter__(self) -> "_FileLock":
        deadline = time.monotonic() + self._timeout
        while True:
            try:
                fd = os.open(
                    str(self._lock_path),
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                )
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                return self
            except FileExistsError:
                if time.monotonic() > deadline:
                    log.warning("Lock expirado — removendo sentinela: %s", self._lock_path)
                    self._lock_path.unlink(missing_ok=True)
                time.sleep(0.05)

    def __exit__(self, *_) -> None:
        self._lock_path.unlink(missing_ok=True)


# ── PersistenceService ────────────────────────────────────────────────────────

class PersistenceService:
    """Leitura e escrita de entregas em JSON com lock de arquivo."""

    def __init__(self, delivery_svc: DeliveryService | None = None) -> None:
        self._svc = delivery_svc or DeliveryService()

    # ── Leitura ───────────────────────────────────────────────────────────────

    def load(self, delivery_date: date) -> list[Delivery]:
        """
        Carrega todas as entregas do JSON da data.
        Retorna lista vazia se o arquivo não existir ou estiver corrompido.
        """
        path = get_json_path(delivery_date)
        if not path.exists():
            log.debug("JSON não encontrado: %s", path)
            return []

        with _FileLock(path):
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                deliveries = [Delivery.from_dict(d) for d in raw]
                log.info("Carregadas %d entrega(s) de %s", len(deliveries), path.name)
                return deliveries
            except (json.JSONDecodeError, KeyError, TypeError) as exc:
                log.error("Falha ao ler %s: %s", path.name, exc)
                return []

    # ── Escrita ───────────────────────────────────────────────────────────────

    def save(self, delivery_date: date, deliveries: list[Delivery]) -> None:
        """
        Salva a lista completa de entregas no JSON (sobrescreve).
        A lista é SEMPRE ordenada antes de salvar.
        """
        path = get_json_path(delivery_date)
        sorted_deliveries = self._svc.sort(deliveries)
        payload = json.dumps(
            [d.to_dict() for d in sorted_deliveries],
            ensure_ascii=False,
            indent=2,
        )
        with _FileLock(path):
            path.write_text(payload, encoding="utf-8")
        log.info("Salvas %d entrega(s) em %s", len(sorted_deliveries), path.name)

    # ── Merge + deduplicação ──────────────────────────────────────────────────

    def merge_and_save(
        self,
        delivery_date: date,
        incoming: list[Delivery],
    ) -> tuple[int, int]:
        """
        Carrega o JSON existente, mescla com `incoming` (deduplicando por id e
        dedup_key) e salva o resultado ordenado.

        Returns:
            (adicionadas, ignoradas_duplicatas)
        """
        existing = self.load(delivery_date)
        seen_ids: set[str] = {d.id for d in existing}
        seen_keys: set[tuple] = {d.dedup_key() for d in existing}

        merged = list(existing)
        added = skipped = 0

        for d in incoming:
            if d.id in seen_ids or d.dedup_key() in seen_keys:
                log.warning("Duplicata ignorada: %s | %s", d.client_name, d.budget_number)
                skipped += 1
            else:
                merged.append(d)
                seen_ids.add(d.id)
                seen_keys.add(d.dedup_key())
                added += 1

        self.save(delivery_date, merged)
        log.info(
            "Merge %s → adicionadas=%d, ignoradas=%d",
            delivery_date.isoformat(), added, skipped,
        )
        return added, skipped
