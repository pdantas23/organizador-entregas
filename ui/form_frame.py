"""FormFrame — formulário de cadastro e edição de entregas."""
from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk
from typing import Callable, Optional

from models.delivery import Delivery
from ui.widgets import FlatButton
from utils.constants import (
    BTN_ADD_BG, BTN_ADD_FG,
    PERIOD_OPTIONS, STATUS_OPTIONS, URGENCY_OPTIONS,
    UI_PANEL_BG,
)
from utils.validators import normalize_fields, parse_date, validate_delivery_fields

_ENTRY_WIDTH = 28
_BTN_CANCEL_BG = "#757575"
_BTN_UPDATE_BG = "#E67E22"
_BTN_UPDATE_FG = "#FFFFFF"


class FormFrame(ttk.Frame):
    """
    Dois modos:
      - Adicionar (padrão): botão [+ Adicionar], campos limpos.
      - Editar: campos preenchidos com a entrega selecionada,
                botões [↻ Atualizar] e [✕ Cancelar edição].

    Callbacks:
      on_add(delivery)            chamado ao adicionar nova entrega
      on_update(old_id, delivery) chamado ao atualizar entrega existente
    """

    def __init__(
        self,
        parent,
        on_add: Callable[[Delivery], None],
        on_update: Callable[[str, Delivery], None],
        **kwargs,
    ) -> None:
        super().__init__(parent, **kwargs)
        self.configure(style="Panel.TFrame")
        self._on_add    = on_add
        self._on_update = on_update
        self._editing_id: Optional[str] = None
        self._date_guard = False          # evita recursão no auto-formato
        self._build()

    # ── Construção ────────────────────────────────────────────────────────────

    def _build(self) -> None:
        # Título dinâmico
        self._title_var = tk.StringVar(value="Nova entrega")
        ttk.Label(self, textvariable=self._title_var, style="PanelTitle.TLabel").pack(
            side="top", anchor="w", padx=14, pady=(10, 8)
        )

        inner = ttk.Frame(self, style="Panel.TFrame")
        inner.pack(fill="both", expand=True, padx=14)
        inner.columnconfigure(0, weight=1)

        # Data — auto-formato DD/MM/AAAA
        today_br = date.today().strftime("%d/%m/%Y")
        self._date_var = tk.StringVar(value=today_br)
        self._date_var.trace("w", self._auto_format_date)
        ttk.Label(inner, text="Data da entrega (DD/MM/AAAA)", style="FieldLabel.TLabel").grid(
            row=0, column=0, sticky="w", pady=(8, 1)
        )
        vcmd = (self.register(lambda v: all(c.isdigit() or c == "/" for c in v) and len(v) <= 10), "%P")
        ttk.Entry(inner, textvariable=self._date_var, width=_ENTRY_WIDTH,
                  validate="key", validatecommand=vcmd,
                  ).grid(row=1, column=0, sticky="ew", pady=(0, 2))

        # Demais campos
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

        # ── Botão Adicionar (sempre visível) ──────────────────────────────────
        self._btn_add_frame = ttk.Frame(self, style="Panel.TFrame")
        self._btn_add_frame.pack(fill="x", padx=14, pady=(14, 2))

        FlatButton(
            self._btn_add_frame,
            text="＋  Adicionar entrega",
            command=self._handle_add,
            bg=BTN_ADD_BG, fg=BTN_ADD_FG,
            font=("Helvetica", 11, "bold"),
            padx=12, pady=9,
        ).pack(fill="x")

        # ── Botões Atualizar + Cancelar (somente modo edição) ─────────────────
        self._btn_edit_frame = ttk.Frame(self, style="Panel.TFrame")
        # (não é empacotado agora — aparece em set_edit_mode)

        self._btn_update = FlatButton(
            self._btn_edit_frame,
            text="↻  Atualizar entrega",
            command=self._handle_update,
            bg=_BTN_UPDATE_BG, fg=_BTN_UPDATE_FG,
            font=("Helvetica", 11, "bold"),
            padx=12, pady=9,
        )
        self._btn_update.pack(side="left", fill="x", expand=True, padx=(0, 4))

        FlatButton(
            self._btn_edit_frame,
            text="✕  Cancelar",
            command=self.set_add_mode,
            bg=_BTN_CANCEL_BG, fg="#FFFFFF",
            font=("Helvetica", 11, "bold"),
            padx=12, pady=9,
        ).pack(side="left")

        ttk.Frame(self, style="Panel.TFrame").pack(pady=4)  # espaço inferior

    # ── Helpers de layout ─────────────────────────────────────────────────────

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

    # ── Auto-formato da data ──────────────────────────────────────────────────

    def _auto_format_date(self, *_args) -> None:
        if self._date_guard:
            return
        self._date_guard = True
        try:
            raw    = self._date_var.get()
            digits = "".join(c for c in raw if c.isdigit())[:8]
            if len(digits) <= 2:
                formatted = digits
            elif len(digits) <= 4:
                formatted = f"{digits[:2]}/{digits[2:]}"
            else:
                formatted = f"{digits[:2]}/{digits[2:4]}/{digits[4:]}"
            if formatted != raw:
                self._date_var.set(formatted)
        finally:
            self._date_guard = False

    # ── Modos: adicionar / editar ─────────────────────────────────────────────

    def set_edit_mode(self, delivery: Delivery) -> None:
        """Carrega os dados da entrega e ativa o modo edição."""
        self._editing_id = delivery.id
        self._title_var.set(f"Editando:  {delivery.client_name}")

        self._date_var.set(delivery.delivery_date.strftime("%d/%m/%Y"))
        self._client_var.set(delivery.client_name)
        self._budget_var.set(delivery.budget_number)
        self._plates_var.set(str(delivery.plate_count))
        self._status_var.set(delivery.status)
        self._period_var.set(delivery.period)
        self._urgency_var.set(delivery.urgency)

        self._btn_edit_frame.pack(fill="x", padx=14, pady=(2, 8))

    def set_add_mode(self) -> None:
        """Volta ao modo de adição e limpa seleção."""
        self._editing_id = None
        self._title_var.set("Nova entrega")
        self._btn_edit_frame.pack_forget()
        self.clear_volatile_fields()

    def clear_volatile_fields(self) -> None:
        self._client_var.set("")
        self._budget_var.set("")
        self._plates_var.set("")
        self._date_var.set(date.today().strftime("%d/%m/%Y"))

    # ── Handlers ─────────────────────────────────────────────────────────────

    def _build_delivery(self) -> Optional[Delivery]:
        """Valida os campos e retorna um Delivery, ou None se inválido."""
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
            return None

        _, d_date, _ = parse_date(date_str)
        norm_client, norm_budget, norm_plates = normalize_fields(client, budget, plates)

        return Delivery(
            delivery_date=d_date,
            client_name=norm_client,
            budget_number=norm_budget,
            plate_count=norm_plates,
            status=status,
            period=period,
            urgency=urgency,
        )

    def _handle_add(self) -> None:
        delivery = self._build_delivery()
        if delivery:
            self._on_add(delivery)

    def _handle_update(self) -> None:
        if self._editing_id is None:
            return
        delivery = self._build_delivery()
        if delivery:
            self._on_update(self._editing_id, delivery)
