"""Constantes globais: opções de domínio, ordens e paleta de cores."""

# ── Opções de domínio ─────────────────────────────────────────────────────────
URGENCY_OPTIONS: list[str] = ["Alta", "Média", "Baixa"]
PERIOD_OPTIONS: list[str] = ["Manhã", "Tarde"]
STATUS_OPTIONS: list[str] = ["Nova entrega", "Finalização"]

# ── Ordem de classificação (menor = maior prioridade) ─────────────────────────
URGENCY_ORDER: dict[str, int] = {"Alta": 0, "Média": 1, "Baixa": 2}
PERIOD_ORDER: dict[str, int] = {"Manhã": 0, "Tarde": 1}

# ── Colunas da planilha Excel ─────────────────────────────────────────────────
OUTPUT_COLUMNS: list[str] = ["Data", "Cliente", "Orçamento", "Nº Placas", "Status", "Urgência"]
COL_WIDTHS: list[int] = [13, 32, 16, 12, 22, 15]  # larguras em caracteres

# ── Paleta de cores Excel (hex sem '#') ───────────────────────────────────────
SECTION_BG = "1F5C8B"       # azul escuro — cabeçalho de seção
SECTION_FG = "FFFFFF"

COL_HEADER_BG = "2E86C1"    # azul médio — cabeçalho de colunas
COL_HEADER_FG = "FFFFFF"

# Fundo leve por linha (urgência)
ROW_URGENCY_BG: dict[str, str] = {
    "Alta":  "FFF0F0",
    "Média": "FFFDE7",
    "Baixa": "F0FFF4",
}

# Célula de urgência (mais saturada)
URGENCY_CELL_BG: dict[str, str] = {
    "Alta":  "FF8080",
    "Média": "FFD740",
    "Baixa": "69DB8F",
}

# Célula de status
STATUS_CELL_BG: dict[str, str] = {
    "Nova entrega": "90CAF9",
    "Finalização":  "CFD8DC",
}

# ── Paleta de cores UI (Tkinter) ──────────────────────────────────────────────
UI_BG = "#F4F6F9"
UI_PANEL_BG = "#FFFFFF"
UI_HEADER_BG = "#1F5C8B"
UI_HEADER_FG = "#FFFFFF"

BTN_ADD_BG = "#2E86C1"
BTN_ADD_FG = "#FFFFFF"
BTN_REMOVE_BG = "#E74C3C"
BTN_REMOVE_FG = "#FFFFFF"
BTN_GENERATE_BG = "#27AE60"
BTN_GENERATE_FG = "#FFFFFF"

# Tags de cor para o Treeview (preview)
TREE_TAG_COLORS: dict[str, str] = {
    "Alta":           "#FFCDD2",
    "Média":          "#FFF9C4",
    "Baixa":          "#C8E6C9",
    "period_header":  "#1F5C8B",
}
TREE_TAG_FG: dict[str, str] = {
    "period_header": "#FFFFFF",
}

# Ícones de período
PERIOD_ICONS: dict[str, str] = {
    "Manhã": "☀",
    "Tarde": "◑",
}
