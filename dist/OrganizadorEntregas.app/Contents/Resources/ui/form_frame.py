"""
FormFrame — painel de cadastro de entregas.

Responsabilidades:
  - Exibir campos de entrada para uma entrega.
  - Validar e normalizar antes de chamar on_add().
  - Limpar campos voláteis após uma adição bem-sucedida.

NÃO gerencia a lista nem persiste dados.
"""
from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk
from typing import Callable

from models.delivery import Delivery
from utils.constants import (
    BTN_ADD_BG, BTN_ADD_FG,
    PERIOD_OPTIONS, STATUS_OPTIONS, URGENCY_OPTIONS,
)
from utils.validators import normalize_fields, parse_date, validate_delivery_fields

_ENTRY_WIDTH = 28


class FormFrame(ttk.Frame):
    """
    Formulário de entrada de uma entrega.

    Parâmetros:
        on_add: callback(Delivery) chamado após validação bem-sucedida.
    """

    def __init__(self, parent, on_add: Callable[[Delivery], None], **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.configure(style="Panel.TFrame")
        self._on_add = on_add
        self._build()

    # ── Construção ────────────────────────────────────────────────────────────

    def _build(self) -> None:
        ttk.Label(
            self, text="Nova entrega",
            style="PanelTitle.TLabel",
        ).pack(side="top", anchor="w", padx=14, pady=(10, 8))

        inner = ttk.Frame(self, style="Panel.TFrame")
        inner.pack(fill="both", expand=True, padx=14)
        inner.columnconfigure(0, weight=1)

        # Data
        self._date_var = tk.StringVar(value=date.today().isoformat())
        self._add_entry(inner, "Data da entrega (AAAA-MM-DD)", self._date_var, row=0)

        # Cliente
        self._client_var = tk.StringVar()
        self._add_entry(inner, "Nome do cliente", self._client_var, row=1)

        # Orçamento
        self._budget_var = tk.StringVar()
        self._add_entry(inner, "Número do orçamento", self._budget_var, row=2)

        # Nº Placas (somente dígitos)
        self._plates_var = tk.StringVar()
        self._add_entry(inner, "Número de placas", self._plates_var, row=3, numeric=True)

        # Status
        self._status_var = tk.StringVar(value=STATUS_OPTIONS[0])
        self._add_combo(inner, "Status", self._status_var, STATUS_OPTIONS, row=4)

        # Período
        self._period_var = tk.StringVar(value=PERIOD_OPTIONS[0])
        self._add_combo(inner, "Período", self._period_var, PERIOD_OPTIONS, row=5)

        # Urgência
        self._urgency_var = tk.StringVar(value=URGENCY_OPTIONS[0])
        self._add_combo(inner, "Urgência", self._urgency_var, URGENCY_OPTIONS, row=6)

        # Botão
        btn_frame = ttk.Frame(self, style="Panel.TFrame")
        btn_frame.pack(fill="x", padx=14, pady=(14, 10))
        tk.Button(
            btn_frame,
            text="＋  Adicionar entrega",
            command=self._handle_add,
            bg=BTN_ADD_BG, fg=BTN_ADD_FG,
            font=("Helvetica", 11, "bold"),
            relief="flat", cursor="hand2",
            padx=12, pady=8,
        ).pack(fill="x")

        # Enter dispara adição
        self.bind_all("<Return>", lambda _: self._handle_add())

    # ── Helpers de layout ─────────────────────────────────────────────────────

    def _add_entry(
        self, parent, label: str, var: tk.StringVar,
        row: int, numeric: bool = False,
    ) -> None:
        ttk.Label(parent, text=label, style="FieldLabel.TLabel").grid(
            row=row * 2, column=0, sticky="w", pady=(8, 1),
        )
        vcmd = (self.register(self._only_digits), "%P") if numeric else None
        ttk.Entry(
            parent, textvariable=var, width=_ENTRY_WIDTH,
            validate="key" if numeric else "none",
            validatecommand=vcmd if numeric else None,
        ).grid(row=row * 2 + 1, column=0, sticky="ew", pady=(0, 2))

    def _add_combo(
        self, parent, label: str, var: tk.StringVar,
        options: list[str], row: int,
    ) -> None:
        ttk.Label(parent, text=label, style="FieldLabel.TLabel").grid(
            row=row * 2, column=0, sticky="w", pady=(8, 1),
        )
        ttk.Combobox(
            parent, textvariable=var, values=options,
            state="readonly", width=_ENTRY_WIDTH - 2,
        ).grid(row=row * 2 + 1, column=0, sticky="ew", pady=(0, 2))

    @staticmethod
    def _only_digits(value: str) -> bool:
        return value == "" or value.isdigit()

    # ── Handler ───────────────────────────────────────────────────────────────

    def _handle_add(self) -> None:
        date_str = self._date_var.get()
        client = self._client_var.get()
        budget = self._budget_var.get()
        plates = self._plates_var.get()
        status = self._status_var.get()
        period = self._period_var.get()
        urgency = self._urgency_var.get()

        errors = validate_delivery_fields(
            date_str, client, budget, plates, status, period, urgency,
        )
        if errors:
            messagebox.showerror(
                "Campos inválidos",
                "\n".join(f"• {e}" for e in errors),
            )
            return

        _, d_date, _ = parse_date(date_str)
        norm_client, norm_budget, norm_plates = normalize_fields(client, budget, plates)

        delivery = Delivery(
            delivery_date=d_date,
            client_name=norm_client,
            budget_number=norm_budget,
            plate_count=norm_plates,
            status=status,
            period=period,
            urgency=urgency,
        )

        self._on_add(delivery)

    def clear_volatile_fields(self) -> None:
        """Limpa campos que variam por entrega (preserva data e dropdowns)."""
        self._client_var.set("")
        self._budget_var.set("")
        self._plates_var.set("")
