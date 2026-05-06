"""ListFrame — preview ordenado e agrupado das entregas da sessão."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional

from models.delivery import Delivery
from ui.widgets import FlatButton
from utils.constants import (
    BTN_REMOVE_BG, BTN_REMOVE_FG,
    PERIOD_ICONS, PERIOD_ORDER,
    TREE_TAG_COLORS, TREE_TAG_FG,
    URGENCY_ORDER,
)

_COLUMNS  = ("data", "cliente", "orcamento", "placas", "status", "urgencia")
_HEADINGS = ("Data", "Cliente", "Orçamento", "Placas", "Status", "Urgência")
_WIDTHS   = (95, 210, 115, 60, 135, 80)


class ListFrame(ttk.Frame):
    """
    Callbacks:
      on_remove(delivery_id)         chamado ao remover uma entrega
      on_select(delivery_id | None)  chamado ao clicar numa entrega (ou desselecionar)
    """

    def __init__(
        self,
        parent,
        on_remove: Callable[[str], None],
        on_select: Callable[[Optional[str]], None],
        **kwargs,
    ) -> None:
        super().__init__(parent, **kwargs)
        self.configure(style="Panel.TFrame")
        self._on_remove = on_remove
        self._on_select = on_select
        self._build()

    # ── Construção ────────────────────────────────────────────────────────────

    def _build(self) -> None:
        ttk.Label(self, text="Preview (igual ao Excel)", style="PanelTitle.TLabel").pack(
            side="top", anchor="w", padx=12, pady=(10, 2)
        )
        self._count_var = tk.StringVar(value="0 entrega(s)")
        ttk.Label(self, textvariable=self._count_var, style="Count.TLabel").pack(
            side="top", anchor="w", padx=12, pady=(0, 4)
        )

        tree_frame = ttk.Frame(self, style="Panel.TFrame")
        tree_frame.pack(fill="both", expand=True, padx=12)

        self._tree = ttk.Treeview(
            tree_frame, columns=_COLUMNS, show="tree headings",
            selectmode="browse", height=18,
        )
        self._tree.column("#0", width=160, anchor="w", stretch=False)
        self._tree.heading("#0", text="Período", anchor="w")

        for col, heading, width in zip(_COLUMNS, _HEADINGS, _WIDTHS):
            self._tree.heading(col, text=heading, anchor="center")
            anchor = "w" if col == "cliente" else "center"
            self._tree.column(col, width=width, anchor=anchor, stretch=False)

        for tag, bg in TREE_TAG_COLORS.items():
            self._tree.tag_configure(tag, background=bg, foreground=TREE_TAG_FG.get(tag, "#000000"))

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",   command=self._tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self._tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        # Evento de seleção
        self._tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        btn_bar = ttk.Frame(self, style="Panel.TFrame")
        btn_bar.pack(fill="x", padx=12, pady=(6, 10))

        FlatButton(
            btn_bar,
            text="✕  Remover selecionada",
            command=self._handle_remove,
            bg=BTN_REMOVE_BG, fg=BTN_REMOVE_FG,
            font=("Helvetica", 10, "bold"),
            padx=10, pady=7,
        ).pack(side="left")

    # ── API pública ───────────────────────────────────────────────────────────

    def refresh(self, deliveries: list[Delivery]) -> None:
        """Reconstrói o Treeview com a lista ordenada."""
        selected_before = self._get_selected_delivery_id()
        self._clear_tree()

        groups: dict[str, list[Delivery]] = {
            p: [] for p in sorted(PERIOD_ORDER, key=PERIOD_ORDER.get)
        }
        for d in deliveries:
            if d.period in groups:
                groups[d.period].append(d)

        total = 0
        for period, items in groups.items():
            icon = PERIOD_ICONS.get(period, "")
            period_id = f"__period__{period}"
            self._tree.insert(
                "", "end", iid=period_id,
                text=f"  {icon}  {period}  ({len(items)})",
                tags=("period_header",),
                open=True,
            )
            for d in sorted(items, key=lambda x: URGENCY_ORDER.get(x.urgency, 99)):
                self._tree.insert(
                    period_id, "end", iid=d.id, text="",
                    values=d.to_display_tuple(), tags=(d.urgency,),
                )
                total += 1

        # Restaura seleção se o item ainda existir
        if selected_before and self._tree.exists(selected_before):
            self._tree.selection_set(selected_before)

        plural = "entrega" if total == 1 else "entregas"
        self._count_var.set(f"{total} {plural} na fila")

    def clear(self) -> None:
        self._clear_tree()
        self._count_var.set("0 entregas na fila")

    def clear_selection(self) -> None:
        self._tree.selection_remove(self._tree.selection())

    # ── Handlers internos ─────────────────────────────────────────────────────

    def _handle_remove(self) -> None:
        iid = self._get_selected_delivery_id()
        if iid:
            self._on_remove(iid)

    def _on_tree_select(self, _event=None) -> None:
        iid = self._get_selected_delivery_id()
        self._on_select(iid)  # None se cabeçalho ou sem seleção

    def _get_selected_delivery_id(self) -> Optional[str]:
        selected = self._tree.selection()
        if not selected:
            return None
        iid = selected[0]
        return None if iid.startswith("__period__") else iid

    def _clear_tree(self) -> None:
        for item in self._tree.get_children():
            self._tree.delete(item)
