"""
Widgets customizados para a UI.

FlatButton: botão colorido que funciona em macOS e Windows.

Problema: no macOS, o tema Aqua do Tkinter ignora bg/fg de tk.Button,
tornando os botões brancos. A solução é usar um Frame + Label, que
respeitam as cores em qualquer plataforma.
"""
from __future__ import annotations

import tkinter as tk
from typing import Callable


class FlatButton(tk.Frame):
    """
    Botão customizado baseado em Frame + Label.
    Funciona corretamente em macOS (Aqua) e Windows.

    Parâmetros:
        parent:   widget pai
        text:     texto do botão
        command:  função chamada ao clicar
        bg:       cor de fundo (hex, ex: '#2E86C1')
        fg:       cor do texto (hex, ex: '#FFFFFF')
        font:     tupla de fonte
        padx/pady: espaçamento interno
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

        self._command = command
        self._bg = bg
        self._hover_bg = self._darken(bg)

        self._label = tk.Label(
            self,
            text=text,
            bg=bg,
            fg=fg,
            font=font,
            padx=padx,
            pady=pady,
        )
        self._label.pack(fill="both", expand=True)

        for w in (self, self._label):
            w.bind("<Button-1>", self._on_click)
            w.bind("<Enter>",    self._on_enter)
            w.bind("<Leave>",    self._on_leave)

    # ── Eventos ───────────────────────────────────────────────────────────────

    def _on_click(self, _event=None) -> None:
        self._command()

    def _on_enter(self, _event=None) -> None:
        self._label.configure(bg=self._hover_bg)
        self.configure(bg=self._hover_bg)

    def _on_leave(self, _event=None) -> None:
        self._label.configure(bg=self._bg)
        self.configure(bg=self._bg)

    # ── Utilitário de cor ─────────────────────────────────────────────────────

    @staticmethod
    def _darken(hex_color: str, factor: float = 0.82) -> str:
        """Escurece uma cor hexadecimal para o efeito hover."""
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return "#{:02x}{:02x}{:02x}".format(
            max(0, int(r * factor)),
            max(0, int(g * factor)),
            max(0, int(b * factor)),
        )
