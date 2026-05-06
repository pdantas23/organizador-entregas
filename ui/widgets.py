"""Widgets customizados para a UI."""
from __future__ import annotations

import tkinter as tk
from typing import Callable


class FlatButton(tk.Frame):
    """
    Botão colorido baseado em Frame + Label.
    Funciona corretamente em macOS (Aqua) e Windows, onde tk.Button
    ignora as cores bg/fg.
    """

    def __init__(
        self,
        parent,
        text: str,
        command: Callable,
        bg: str,
        fg: str,
        font: tuple = ("Helvetica", 10, "bold"),
        padx: int = 12,
        pady: int = 8,
        **kwargs,
    ) -> None:
        super().__init__(parent, bg=bg, cursor="hand2", **kwargs)

        self._command   = command
        self._bg        = bg
        self._fg        = fg
        self._hover_bg  = self._darken(bg)
        self._disabled  = False

        self._label = tk.Label(
            self, text=text, bg=bg, fg=fg,
            font=font, padx=padx, pady=pady,
        )
        self._label.pack(fill="both", expand=True)

        for w in (self, self._label):
            w.bind("<Button-1>", self._on_click)
            w.bind("<Enter>",    self._on_enter)
            w.bind("<Leave>",    self._on_leave)

    # ── Estado ────────────────────────────────────────────────────────────────

    def enable(self) -> None:
        self._disabled = False
        self._label.configure(bg=self._bg, fg=self._fg)
        self.configure(bg=self._bg, cursor="hand2")

    def disable(self) -> None:
        self._disabled = True
        disabled_bg = "#CCCCCC"
        self._label.configure(bg=disabled_bg, fg="#999999")
        self.configure(bg=disabled_bg, cursor="")

    def set_text(self, text: str) -> None:
        self._label.configure(text=text)

    # ── Eventos ───────────────────────────────────────────────────────────────

    def _on_click(self, _event=None) -> None:
        if not self._disabled:
            self._command()

    def _on_enter(self, _event=None) -> None:
        if not self._disabled:
            self._label.configure(bg=self._hover_bg)
            self.configure(bg=self._hover_bg)

    def _on_leave(self, _event=None) -> None:
        if not self._disabled:
            self._label.configure(bg=self._bg)
            self.configure(bg=self._bg)

    # ── Cor ───────────────────────────────────────────────────────────────────

    @staticmethod
    def _darken(hex_color: str, factor: float = 0.82) -> str:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return "#{:02x}{:02x}{:02x}".format(
            max(0, int(r * factor)),
            max(0, int(g * factor)),
            max(0, int(b * factor)),
        )
