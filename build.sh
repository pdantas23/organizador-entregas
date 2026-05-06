#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# build.sh — Gera o executável macOS (.app) com PyInstaller
#
# Usa um venv isolado para garantir que APENAS as dependências reais do app
# sejam empacotadas (evita numpy, Pillow, lxml e outras libs do sistema).
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

APP_NAME="OrganizadorEntregas"
ENTRY="main.py"
VENV_DIR=".venv-build"

echo "▶  Criando ambiente virtual isolado..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "▶  Instalando apenas dependências necessárias..."
pip install --quiet --upgrade pip
pip install --quiet openpyxl pyinstaller

echo "▶  Limpando builds anteriores..."
rm -rf build dist "${APP_NAME}.spec"

echo "▶  Empacotando com PyInstaller..."
python -m PyInstaller \
  --name            "$APP_NAME" \
  --windowed \
  --onedir \
  --noconfirm \
  --add-data        "utils:utils" \
  --add-data        "models:models" \
  --add-data        "services:services" \
  --add-data        "excel:excel" \
  --add-data        "export:export" \
  --add-data        "ui:ui" \
  --hidden-import   openpyxl \
  --hidden-import   openpyxl.cell \
  --hidden-import   openpyxl.cell._writer \
  --hidden-import   openpyxl.styles \
  --hidden-import   openpyxl.utils \
  --hidden-import   openpyxl.writer.excel \
  --exclude-module  numpy \
  --exclude-module  PIL \
  --exclude-module  lxml \
  --exclude-module  matplotlib \
  --exclude-module  scipy \
  --exclude-module  pandas \
  "$ENTRY"

deactivate

echo "▶  Criando zip para distribuição..."
cd dist
zip -r "${APP_NAME}-macOS.zip" "${APP_NAME}.app"
cd ..

echo ""
echo "✅  Build concluído!"
du -sh dist/${APP_NAME}.app dist/${APP_NAME}-macOS.zip
