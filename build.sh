#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# build.sh — Gera o executável macOS com PyInstaller
#
# Uso:
#   chmod +x build.sh
#   ./build.sh
#
# Saída:
#   dist/OrganizadorEntregas  (binário único; arraste para /Applications)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

APP_NAME="OrganizadorEntregas"
ENTRY="main.py"

echo "▶  Instalando dependências..."
pip3 install -r requirements-dev.txt --quiet

echo "▶  Limpando builds anteriores..."
rm -rf build dist "${APP_NAME}.spec"

echo "▶  Empacotando com PyInstaller..."
# Usa 'python3 -m PyInstaller' para garantir que o módulo seja encontrado
# independentemente de o diretório de scripts estar no PATH ou não.
python3 -m PyInstaller \
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
  --hidden-import   "openpyxl" \
  --hidden-import   "openpyxl.cell" \
  --hidden-import   "openpyxl.cell._writer" \
  --hidden-import   "openpyxl.styles" \
  --hidden-import   "openpyxl.utils" \
  --hidden-import   "openpyxl.writer.excel" \
  "$ENTRY"

echo ""
echo "▶  Criando zip para distribuição..."
cd dist
zip -r "${APP_NAME}-macOS.zip" "${APP_NAME}.app"
cd ..

echo ""
echo "✅  Build concluído!"
echo "   App:  dist/${APP_NAME}.app"
echo "   Zip:  dist/${APP_NAME}-macOS.zip  ← envie este arquivo"
