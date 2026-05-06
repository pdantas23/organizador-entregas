"""
ExcelExporter — orquestra JSON → Excel.

Hierarquia de exportadores:
  BaseExporter (ABC)
    └── ExcelExporter

O padrão BaseExporter permite adicionar CsvExporter, PdfExporter etc.
no futuro sem alterar o código existente.

Fluxo:
  1. Recebe lista de Delivery já ordenada (vinda do JSON).
  2. Agrupa por período.
  3. Usa ExcelWriter para escrever seções, cabeçalhos e linhas.
  4. Salva o workbook no caminho definido por get_excel_path().
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path

import openpyxl

from excel.writer import ExcelWriter
from models.delivery import Delivery
from utils.constants import PERIOD_ORDER
from utils.logger import get_logger
from utils.paths import get_excel_path

log = get_logger("export.excel")


# ── Contrato base ─────────────────────────────────────────────────────────────

class BaseExporter(ABC):
    """
    Interface comum para todos os formatos de exportação.
    Para adicionar CSV ou PDF: crie uma subclasse e implemente `export()`.
    """

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Nome legível do formato (ex.: 'Excel', 'CSV', 'PDF')."""
        ...

    @abstractmethod
    def export(self, delivery_date: date, deliveries: list[Delivery]) -> Path:
        """
        Exporta as entregas para o formato alvo.

        Args:
            delivery_date: data do arquivo de destino.
            deliveries:    lista ORDENADA de entregas (responsabilidade do chamador).

        Returns:
            Caminho completo do arquivo gerado.
        """
        ...


# ── Implementação Excel ───────────────────────────────────────────────────────

class ExcelExporter(BaseExporter):
    """Exporta entregas para .xlsx com seções MANHÃ / TARDE e estilos visuais."""

    @property
    def format_name(self) -> str:
        return "Excel"

    def export(self, delivery_date: date, deliveries: list[Delivery]) -> Path:
        filepath = get_excel_path(delivery_date)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Entregas"

        writer = ExcelWriter(ws)

        # Itera pelos períodos na ordem canônica
        for period in sorted(PERIOD_ORDER, key=PERIOD_ORDER.get):
            period_deliveries = [d for d in deliveries if d.period == period]

            writer.write_section_header(period)
            writer.write_column_headers()

            if not period_deliveries:
                writer.write_empty_period_notice()
            else:
                for delivery in period_deliveries:
                    writer.write_delivery_row(delivery)

            writer.write_blank_row()

        writer.finalize()
        wb.save(filepath)

        log.info(
            "Excel gerado: %s (%d entrega(s))",
            filepath.name, len(deliveries),
        )
        return filepath
