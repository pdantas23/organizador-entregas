#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# build.sh — Gera o instalador DMG para macOS
#
# Saída:  dist/OrganizadorEntregas.dmg
#         Ao abrir, exibe o app e a pasta Applications para arrastar.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

APP_NAME="OrganizadorEntregas"
ENTRY="main.py"
VENV_DIR=".venv-build"
STAGING="/tmp/${APP_NAME}-dmg-staging"

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

echo "▶  Criando DMG instalador..."
rm -rf "$STAGING"
mkdir -p "$STAGING"
cp -r "dist/${APP_NAME}.app" "$STAGING/"
# Symlink para /Applications — permite arrastar na janela do DMG
ln -s /Applications "$STAGING/Applications"

hdiutil create \
  -volname  "$APP_NAME" \
  -srcfolder "$STAGING" \
  -ov \
  -format   UDZO \
  "dist/${APP_NAME}.dmg"

rm -rf "$STAGING"

echo ""
echo "✅  Build concluído!"
du -sh "dist/${APP_NAME}.app" "dist/${APP_NAME}.dmg"
echo ""
echo "   Distribuição:  dist/${APP_NAME}.dmg"
echo ""
echo "   Como instalar (macOS):"
echo "   1. Abra o .dmg"
echo "   2. Arraste o app para a pasta Applications"
echo "   3. Se aparecer aviso de segurança:"
echo "      Preferências → Segurança e Privacidade → Abrir assim mesmo"
echo "      ou: xattr -dr com.apple.quarantine /Applications/${APP_NAME}.app"
