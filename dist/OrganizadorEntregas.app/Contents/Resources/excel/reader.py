"""
ExcelReader — leitura legada de planilhas Excel → objetos Delivery.

ATENÇÃO: com JSON como fonte de verdade, este módulo é usado apenas como
ferramenta de migração ou diagnóstico. NÃO deve ser chamado no fluxo normal.

Como funciona:
  - Varre a worksheet linha a linha.
  - Infere o período a partir dos cabeçalhos de seção (=== MANHÃ / TARDE ===).
  - Reconstrói objetos Delivery a partir das linhas de dados.
"""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Optional

import openpyxl

from models.delivery import Delivery
from utils.logger import get_logger

log = get_logger("excel.reader")


class ExcelReader:
    """Converte uma planilha Excel formatada em lista de Delivery."""

    def read(self, filepath: Path) -> list[Delivery]:
        if not filepath.exists():
            log.warning("ExcelReader: arquivo não encontrado: %s", filepath)
            return []

        try:
            wb = openpyxl.load_workbook(filepath, data_only=True)
        except Exception as exc:
            log.error("ExcelReader: falha ao abrir %s → %s", filepath.name, exc)
            return []

        ws = wb.active
        deliveries: list[Delivery] = []
        current_period: Optional[str] = None
        col_map: dict[int, str] = {}

        for row in ws.iter_rows():
            if not row:
                continue

            first_val = row[0].value
            if first_val is None:
                continue

            first_str = str(first_val).strip().upper()

            # Detecta cabeçalho de seção
            if "MANHÃ" in first_str or "MANHA" in first_str:
                current_period = "Manhã"
                col_map = {}
                continue
            if "TARDE" in first_str:
                current_period = "Tarde"
                col_map = {}
                continue

            # Detecta linha de cabeçalho de colunas
            if first_str == "DATA":
                col_map = {
                    i: str(cell.value).strip()
                    for i, cell in enumerate(row)
                    if cell.value is not None
                }
                continue

            # Linha de dados
            if not current_period or not col_map or not first_val:
                continue

            row_data: dict[str, object] = {
                col_map[i]: cell.value
                for i, cell in enumerate(row)
                if i in col_map and cell.value is not None
            }

            client = row_data.get("Cliente")
            if not client:
                continue

            try:
                raw_date = row_data.get("Data")
                if isinstance(raw_date, datetime):
                    d_date = raw_date.date()
                elif isinstance(raw_date, date):
                    d_date = raw_date
                else:
                    d_date = date.fromisoformat(str(raw_date))

                deliveries.append(
                    Delivery(
                        delivery_date=d_date,
                        client_name=str(client),
                        budget_number=str(row_data.get("Orçamento", "")),
                        plate_count=int(row_data.get("Nº Placas", 0)),
                        status=str(row_data.get("Status", "")),
                        period=current_period,
                        urgency=str(row_data.get("Urgência", "")),
                    )
                )
            except Exception as exc:
                log.warning("ExcelReader: linha ignorada (%s)", exc)

        log.info(
            "ExcelReader: %d entrega(s) lida(s) de %s",
            len(deliveries), filepath.name,
        )
        return deliveries
