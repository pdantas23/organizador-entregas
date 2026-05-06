"""FormFrame — painel de cadastro de entregas."""
from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk
from typing import Callable

from models.delivery import Delivery
from ui.widgets import FlatButton
from utils.constants import (
    BTN_ADD_BG, BTN_ADD_FG,
    PERIOD_OPTIONS, STATUS_OPTIONS, URGENCY_OPTIONS,
)
from utils.validators import normalize_fields, parse_date, validate_delivery_fields

_ENTRY_WIDTH = 28


class FormFrame(ttk.Frame):
    def __init__(self, parent, on_add: Callable[[Delivery], None], **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.configure(style="Panel.TFrame")
        self._on_add = on_add
        self._build()

    def _build(self) -> None:
        ttk.Label(self, text="Nova entrega", style="PanelTitle.TLabel").pack(
            side="top", anchor="w", padx=14, pady=(10, 8)
        )

        inner = ttk.Frame(self, style="Panel.TFrame")
        inner.pack(fill="both", expand=True, padx=14)
        inner.columnconfigure(0, weight=1)

        self._date_var = tk.StringVar(value=date.today().isoformat())
        self._add_entry(inner, "Data da entrega (AAAA-MM-DD)", self._date_var, row=0)

        self._client_var = tk.StringVar()
        self._add_entry(inner, "Nome do cliente", self._client_var, row=1)

        self._budget_var = tk.StringVar()
        self._add_entry(inner, "Número do orçamento", self._budget_var, row=2)

        self._plates_var = tk.StringVar()
        self._add_entry(inner, "Número de placas", self._plates_var, row=3, numeric=True)

        self._status_var = tk.StringVar(value=STATUS_OPTIONS[0])
        self._add_combo(inner, "Status", self._status_var, STATUS_OPTIONS, row=4)

        self._period_var = tk.StringVar(value=PERIOD_OPTIONS[0])
        self._add_combo(inner, "Período", self._period_var, PERIOD_OPTIONS, row=5)

        self._urgency_var = tk.StringVar(value=URGENCY_OPTIONS[0])
        self._add_combo(inner, "Urgência", self._urgency_var, URGENCY_OPTIONS, row=6)

        btn_frame = ttk.Frame(self, style="Panel.TFrame")
        btn_frame.pack(fill="x", padx=14, pady=(14, 10))

        FlatButton(
            btn_frame,
            text="＋  Adicionar entrega",
            command=self._handle_add,
            bg=BTN_ADD_BG,
            fg=BTN_ADD_FG,
            font=("Helvetica", 11, "bold"),
            padx=12,
            pady=9,
        ).pack(fill="x")

        self.bind_all("<Return>", lambda _: self._handle_add())

    def _add_entry(self, parent, label, var, row, numeric=False):
        ttk.Label(parent, text=label, style="FieldLabel.TLabel").grid(
            row=row * 2, column=0, sticky="w", pady=(8, 1)
        )
        vcmd = (self.register(lambda v: v == "" or v.isdigit()), "%P") if numeric else None
        ttk.Entry(
            parent, textvariable=var, width=_ENTRY_WIDTH,
            validate="key" if numeric else "none",
            validatecommand=vcmd if numeric else None,
        ).grid(row=row * 2 + 1, column=0, sticky="ew", pady=(0, 2))

    def _add_combo(self, parent, label, var, options, row):
        ttk.Label(parent, text=label, style="FieldLabel.TLabel").grid(
            row=row * 2, column=0, sticky="w", pady=(8, 1)
        )
        ttk.Combobox(
            parent, textvariable=var, values=options,
            state="readonly", width=_ENTRY_WIDTH - 2,
        ).grid(row=row * 2 + 1, column=0, sticky="ew", pady=(0, 2))

    def _handle_add(self) -> None:
        date_str  = self._date_var.get()
        client    = self._client_var.get()
        budget    = self._budget_var.get()
        plates    = self._plates_var.get()
        status    = self._status_var.get()
        period    = self._period_var.get()
        urgency   = self._urgency_var.get()

        errors = validate_delivery_fields(date_str, client, budget, plates, status, period, urgency)
        if errors:
            messagebox.showerror("Campos inválidos", "\n".join(f"• {e}" for e in errors))
            return

        _, d_date, _ = parse_date(date_str)
        norm_client, norm_budget, norm_plates = normalize_fields(client, budget, plates)

        self._on_add(Delivery(
            delivery_date=d_date,
            client_name=norm_client,
            budget_number=norm_budget,
            plate_count=norm_plates,
            status=status,
            period=period,
            urgency=urgency,
        ))

    def clear_volatile_fields(self) -> None:
        self._client_var.set("")
        self._budget_var.set("")
        self._plates_var.set("")
