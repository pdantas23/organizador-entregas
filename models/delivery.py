"""Entidade de domínio: Delivery."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date


@dataclass
class Delivery:
    delivery_date: date
    client_name: str
    budget_number: str
    plate_count: int
    status: str    # "Nova entrega" | "Finalização"
    period: str    # "Manhã" | "Tarde"
    urgency: str   # "Alta" | "Média" | "Baixa"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # ── Serialização / deserialização ─────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "id":            self.id,
            "delivery_date": self.delivery_date.isoformat(),
            "client_name":   self.client_name,
            "budget_number": self.budget_number,
            "plate_count":   self.plate_count,
            "status":        self.status,
            "period":        self.period,
            "urgency":       self.urgency,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Delivery:
        return cls(
            id=data["id"],
            delivery_date=date.fromisoformat(data["delivery_date"]),
            client_name=data["client_name"],
            budget_number=data["budget_number"],
            plate_count=int(data["plate_count"]),
            status=data["status"],
            period=data["period"],
            urgency=data["urgency"],
        )

    # ── Chave de deduplicação ─────────────────────────────────────────────────

    def dedup_key(self) -> tuple:
        """
        Chave para detectar duplicatas por conteúdo de negócio.
        Dois registros com o mesmo cliente+orçamento+data+período são duplicatas,
        independentemente do id.
        """
        return (
            self.client_name.strip().lower(),
            self.budget_number.strip().lower(),
            self.delivery_date.isoformat(),
            self.period,
        )

    # ── Conversão para exibição / exportação ──────────────────────────────────

    def to_excel_row(self) -> list:
        """Valores na ordem de OUTPUT_COLUMNS."""
        return [
            self.delivery_date,
            self.client_name,
            self.budget_number,
            self.plate_count,
            self.status,
            self.urgency,
        ]

    def to_display_tuple(self) -> tuple:
        """Tupla para o Treeview da UI."""
        return (
            self.delivery_date.strftime("%d/%m/%Y"),
            self.client_name,
            self.budget_number,
            str(self.plate_count),
            self.status,
            self.urgency,
        )
