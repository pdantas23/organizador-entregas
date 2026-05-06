"""Ponto de entrada da aplicação."""
from __future__ import annotations

import sys
from pathlib import Path

# Garante que os pacotes do projeto sejam encontrados quando rodando como
# executável PyInstaller (sys._MEIPASS) ou em desenvolvimento.
if getattr(sys, "frozen", False):
    _root = Path(sys._MEIPASS)  # type: ignore[attr-defined]
else:
    _root = Path(__file__).resolve().parent

sys.path.insert(0, str(_root))

# Inicializa logging antes de qualquer import que use get_logger()
from utils.logger import setup_logging
setup_logging()

from ui.app import App


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
