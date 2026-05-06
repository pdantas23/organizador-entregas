"""App — janela principal e controlador da aplicação."""
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from excel.reader import ExcelReader
from export.excel_exporter import ExcelExporter
from models.delivery import Delivery
from services.persistence_service import PersistenceService
from services.session_service import SessionService
from ui.form_frame import FormFrame
from ui.list_frame import ListFrame
from ui.widgets import FlatButton
from utils.constants import (
    BTN_GENERATE_BG, BTN_GENERATE_FG,
    UI_BG, UI_HEADER_BG, UI_HEADER_FG, UI_PANEL_BG,
)
from utils.logger import get_logger

log = get_logger("ui.app")

APP_TITLE = "Gerador de Planilhas de Entregas"
MIN_W, MIN_H = 1_060, 660


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.minsize(MIN_W, MIN_H)
        self.configure(bg=UI_BG)

        self._session    = SessionService()
        self._persistence = PersistenceService()
        self._exporter   = ExcelExporter()
        self._reader     = ExcelReader()

        self._setup_styles()
        self._build()
        self._center_window()
        log.info("Aplicação iniciada")

    # ── Estilos ───────────────────────────────────────────────────────────────

    def _setup_styles(self) -> None:
        style = ttk.Style(self)

        # Força tema 'clam' para que cores de widgets ttk funcionem em macOS.
        # O tema 'aqua' (padrão no macOS) ignora bg/fg de botões tk.
        available = style.theme_names()
        for theme in ("clam", "alt", "default"):
            if theme in available:
                style.theme_use(theme)
                break

        style.configure("TFrame",       background=UI_BG)
        style.configure("Panel.TFrame", background=UI_PANEL_BG)

        style.configure("PanelTitle.TLabel",
            background=UI_PANEL_BG, foreground="#1A3A5C",
            font=("Helvetica", 13, "bold"),
        )
        style.configure("FieldLabel.TLabel",
            background=UI_PANEL_BG, foreground="#555555",
            font=("Helvetica", 9),
        )
        style.configure("Count.TLabel",
            background=UI_PANEL_BG, foreground="#888888",
            font=("Helvetica", 9),
        )
        style.configure("Status.TLabel",
            background=UI_BG, foreground="#333333",
            font=("Helvetica", 10),
        )
        style.configure("TEntry",    fieldbackground="#FAFAFA", padding=(4, 4))
        style.configure("TCombobox", padding=(4, 4))
        style.configure("Treeview",  rowheight=22, font=("Helvetica", 10))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        self._build_header()
        self._build_body()
        self._build_footer()

    def _build_header(self) -> None:
        header = tk.Frame(self, bg=UI_HEADER_BG, height=52)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(header, text="📋", bg=UI_HEADER_BG,
                 font=("Helvetica", 18), fg=UI_HEADER_FG,
                 ).pack(side="left", padx=(16, 6), pady=10)
        tk.Label(header, text=APP_TITLE, bg=UI_HEADER_BG,
                 fg=UI_HEADER_FG, font=("Helvetica", 14, "bold"),
                 ).pack(side="left", pady=10)

    def _build_body(self) -> None:
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=12, pady=10)
        body.columnconfigure(0, weight=0)
        body.columnconfigure(1, weight=0, minsize=8)
        body.columnconfigure(2, weight=1)
        body.rowconfigure(0, weight=1)

        form_panel = tk.Frame(body, bg=UI_PANEL_BG)
        form_panel.grid(row=0, column=0, sticky="nsew")
        self._form = FormFrame(
            form_panel,
            on_add=self._handle_add,
            on_update=self._handle_update,
            style="Panel.TFrame",
        )
        self._form.pack(fill="both", expand=True)

        list_panel = tk.Frame(body, bg=UI_PANEL_BG)
        list_panel.grid(row=0, column=2, sticky="nsew")
        self._list = ListFrame(
            list_panel,
            on_remove=self._handle_remove,
            on_select=self._handle_select,
            style="Panel.TFrame",
        )
        self._list.pack(fill="both", expand=True)

    def _build_footer(self) -> None:
        footer = tk.Frame(self, bg=UI_BG)
        footer.pack(fill="x", side="bottom", padx=12, pady=(0, 12))

        FlatButton(
            footer,
            text="  ⬇  Gerar / Atualizar Planilha  ",
            command=self._handle_generate,
            bg=BTN_GENERATE_BG,
            fg=BTN_GENERATE_FG,
            font=("Helvetica", 12, "bold"),
            padx=16,
            pady=10,
        ).pack(side="left")

        FlatButton(
            footer,
            text="  📂  Carregar Planilha  ",
            command=self._handle_load,
            bg="#5D6D7E",
            fg="#FFFFFF",
            font=("Helvetica", 12, "bold"),
            padx=16,
            pady=10,
        ).pack(side="left", padx=(8, 0))

        self._status_var = tk.StringVar(value="Adicione entregas e clique em Gerar.")
        ttk.Label(footer, textvariable=self._status_var, style="Status.TLabel").pack(
            side="left", padx=16
        )

    # ── Handlers ─────────────────────────────────────────────────────────────

    def _handle_add(self, delivery: Delivery) -> None:
        result = self._session.add(delivery)
        if not result:
            messagebox.showwarning("Duplicata detectada", result.message)
            return
        self._form.clear_volatile_fields()
        self._refresh_list()
        self._status_var.set(
            f"Adicionada: {delivery.client_name} ({delivery.period} · {delivery.urgency})"
        )

    def _handle_remove(self, delivery_id: str) -> None:
        self._session.remove(delivery_id)
        self._form.set_add_mode()
        self._refresh_list()
        self._status_var.set("Entrega removida.")

    def _handle_select(self, delivery_id: Optional[str]) -> None:
        if delivery_id is None:
            self._form.set_add_mode()
            return
        delivery = self._session.get_by_id(delivery_id)
        if delivery:
            self._form.set_edit_mode(delivery)

    def _handle_update(self, old_id: str, delivery: Delivery) -> None:
        result = self._session.update(old_id, delivery)
        if not result:
            messagebox.showwarning("Conflito", result.message)
            return
        self._form.set_add_mode()
        self._list.clear_selection()
        self._refresh_list()
        self._status_var.set(
            f"Atualizada: {delivery.client_name} ({delivery.period} · {delivery.urgency})"
        )

    def _handle_generate(self) -> None:
        if self._session.is_empty():
            messagebox.showwarning("Sem entregas", "Adicione ao menos uma entrega antes de gerar.")
            return

        if not messagebox.askyesno(
            "Confirmar geração",
            f"Gerar / atualizar planilha com {self._session.count()} entrega(s)?",
        ):
            return

        results: list[str] = []
        errors:  list[str] = []

        for d_date, d_list in self._session.get_by_date().items():
            try:
                added, skipped = self._persistence.merge_and_save(d_date, d_list)
                all_saved      = self._persistence.load(d_date)
                filepath       = self._exporter.export(d_date, all_saved)

                msg = f"• {filepath.name}: {added} adicionada(s)"
                if skipped:
                    msg += f", {skipped} duplicata(s) ignorada(s)"
                results.append(msg)
            except Exception as exc:
                errors.append(f"• {d_date}: {exc}")
                log.error("Erro ao exportar %s: %s", d_date, exc)

        if errors:
            messagebox.showerror("Erro ao gerar planilha", "\n".join(errors))
        else:
            messagebox.showinfo(
                "Planilha gerada ✓",
                f"Salvo em:\n  ~/Desktop/entregas/\n\n" + "\n".join(results),
            )
            self._session.clear()
            self._form.set_add_mode()
            self._refresh_list()
            self._status_var.set("Planilha gerada com sucesso.")

    def _handle_load(self) -> None:
        filepath = filedialog.askopenfilename(
            title="Selecionar planilha",
            filetypes=[("Planilhas Excel", "*.xlsx *.xls"), ("Todos os arquivos", "*.*")],
        )
        if not filepath:
            return

        deliveries = self._reader.read(Path(filepath))
        if not deliveries:
            messagebox.showwarning(
                "Planilha vazia",
                "Nenhuma entrega encontrada na planilha selecionada.",
            )
            return

        added = skipped = 0
        for d in deliveries:
            result = self._session.add(d)
            if result:
                added += 1
            else:
                skipped += 1

        self._refresh_list()
        msg = f"{added} entrega(s) carregada(s)"
        if skipped:
            msg += f", {skipped} duplicata(s) ignorada(s)"
        self._status_var.set(msg)
        log.info("Planilha carregada: %s → %s", filepath, msg)

    # ── Utilitários ───────────────────────────────────────────────────────────

    def _refresh_list(self) -> None:
        self._list.refresh(self._session.get_sorted())

    def _center_window(self) -> None:
        self.update_idletasks()
        w = max(self.winfo_reqwidth(), MIN_W)
        h = max(self.winfo_reqheight(), MIN_H)
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
