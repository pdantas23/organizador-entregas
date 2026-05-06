"""
ListFrame — preview ordenado e agrupado das entregas da sessão.

Exibe a lista exatamente como ficará no Excel:
  ▼ ☀ MANHÃ
      Cliente A | ORC-001 | ...  [Alta]
      Cliente B | ORC-002 | ...  [Média]
  ▼ ◑ TARDE
      Cliente C | ORC-003 | ...  [Baixa]

O preview é reconstruído inteiro a cada mudança de sessão (método refresh()).
A UI nunca manipula a lista diretamente — só lê o estado do SessionService.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional

from models.delivery import Delivery
from utils.constants import (
    BTN_REMOVE_BG, BTN_REMOVE_FG,
    PERIOD_ICONS, PERIOD_ORDER,
    TREE_TAG_COLORS, TREE_TAG_FG,
    URGENCY_ORDER,
)

# Colunas da tabela (sem "data" — está no nó pai de período se necessário)
_COLUMNS = ("data", "cliente", "orcamento", "placas", "status", "urgencia")
_HEADINGS = ("Data", "Cliente", "Orçamento", "Placas", "Status", "Urgência")
_WIDTHS = (95, 210, 115, 60, 135, 80)


class ListFrame(ttk.Frame):
    """
    Painel que exibe o preview agrupado por período.

    Parâmetros:
        on_remove: callback(delivery_id) chamado quando o usuário remove uma entrega.
    """

    def __init__(
        self,
        parent,
        on_remove: Callable[[str], None],
        **kwargs,
    ) -> None:
        super().__init__(parent, **kwargs)
        self.configure(style="Panel.TFrame")
        self._on_remove = on_remove
        self._build()

    # ── Construção ────────────────────────────────────────────────────────────

    def _build(self) -> None:
        # Título
        ttk.Label(
            self, text="Preview (igual ao Excel)",
            style="PanelTitle.TLabel",
        ).pack(side="top", anchor="w", padx=12, pady=(10, 2))

        # Contador
        self._count_var = tk.StringVar(value="0 entrega(s)")
        ttk.Label(
            self, textvariable=self._count_var,
            style="Count.TLabel",
        ).pack(side="top", anchor="w", padx=12, pady=(0, 4))

        # Treeview + scrollbars
        tree_frame = ttk.Frame(self, style="Panel.TFrame")
        tree_frame.pack(fill="both", expand=True, padx=12)

        self._tree = ttk.Treeview(
            tree_frame,
            columns=_COLUMNS,
            show="tree headings",
            selectmode="browse",
            height=18,
        )

        # Coluna-árvore (período)
        self._tree.column("#0", width=160, anchor="w", stretch=False)
        self._tree.heading("#0", text="Período", anchor="w")

        for col, heading, width in zip(_COLUMNS, _HEADINGS, _WIDTHS):
            self._tree.heading(col, text=heading, anchor="center")
            anchor = "w" if col == "cliente" else "center"
            self._tree.column(col, width=width, anchor=anchor, stretch=False)

        # Tags de cor
        for tag, bg in TREE_TAG_COLORS.items():
            fg = TREE_TAG_FG.get(tag, "#000000")
            self._tree.tag_configure(tag, background=bg, foreground=fg)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self._tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self._tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        # Botão remover
        btn_bar = ttk.Frame(self, style="Panel.TFrame")
        btn_bar.pack(fill="x", padx=12, pady=(6, 10))

        tk.Button(
            btn_bar,
            text="✕  Remover selecionada",
            command=self._handle_remove,
            bg=BTN_REMOVE_BG, fg=BTN_REMOVE_FG,
            font=("Helvetica", 10, "bold"),
            relief="flat", cursor="hand2",
            padx=10, pady=6,
        ).pack(side="left")

    # ── API pública ───────────────────────────────────────────────────────────

    def refresh(self, deliveries: list[Delivery]) -> None:
        """
        Reconstrói o Treeview com a lista de entregas já ordenada.
        Deve ser chamado sempre que o SessionService mudar.
        """
        self._clear_tree()

        # Agrupa por período (na ordem canônica)
        groups: dict[str, list[Delivery]] = {p: [] for p in sorted(PERIOD_ORDER, key=PERIOD_ORDER.get)}
        for d in deliveries:
            if d.period in groups:
                groups[d.period].append(d)

        total = 0
        for period, items in groups.items():
            icon = PERIOD_ICONS.get(period, "")
            count_str = f"({len(items)})" if items else "(vazio)"
            period_id = f"__period__{period}"

            self._tree.insert(
                "", "end",
                iid=period_id,
                text=f"  {icon}  {period}  {count_str}",
                tags=("period_header",),
                open=True,
            )

            for d in sorted(items, key=lambda x: URGENCY_ORDER.get(x.urgency, 99)):
                self._tree.insert(
                    period_id, "end",
                    iid=d.id,
                    text="",
                    values=d.to_display_tuple(),
                    tags=(d.urgency,),
                )
                total += 1

        self._update_count(total)

    def clear(self) -> None:
        self._clear_tree()
        self._update_count(0)

    # ── Handlers internos ─────────────────────────────────────────────────────

    def _handle_remove(self) -> None:
        selected = self._tree.selection()
        if not selected:
            return
        iid = selected[0]
        if iid.startswith("__period__"):
            messagebox.showinfo(
                "Seleção inválida",
                "Selecione uma entrega específica, não um cabeçalho de período.",
            )
            return
        self._on_remove(iid)

    def _clear_tree(self) -> None:
        for item in self._tree.get_children():
            self._tree.delete(item)

    def _update_count(self, total: int) -> None:
        plural = "entrega" if total == 1 else "entregas"
        self._count_var.set(f"{total} {plural} na fila")
