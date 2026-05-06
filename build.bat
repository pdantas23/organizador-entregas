@echo off
REM ─────────────────────────────────────────────────────────────────────────────
REM build.bat — Gera o executável Windows (.exe) com PyInstaller
REM
REM Uso: build.bat
REM
REM Saída: dist\OrganizadorEntregas.exe
REM ─────────────────────────────────────────────────────────────────────────────

set APP_NAME=OrganizadorEntregas
set ENTRY=main.py

echo [1/4] Instalando dependencias...
pip install -r requirements-dev.txt --quiet
if errorlevel 1 (echo ERRO: falha ao instalar dependencias & pause & exit /b 1)

echo [2/4] Limpando builds anteriores...
if exist build   rmdir /s /q build
if exist dist    rmdir /s /q dist
if exist "%APP_NAME%.spec" del /q "%APP_NAME%.spec"

echo [3/4] Empacotando com PyInstaller...
pyinstaller ^
  --name            %APP_NAME% ^
  --windowed ^
  --onefile ^
  --noconfirm ^
  --add-data        "utils;utils" ^
  --add-data        "models;models" ^
  --add-data        "services;services" ^
  --add-data        "excel;excel" ^
  --add-data        "export;export" ^
  --add-data        "ui;ui" ^
  --hidden-import   openpyxl ^
  --hidden-import   openpyxl.cell ^
  --hidden-import   openpyxl.cell._writer ^
  --hidden-import   openpyxl.styles ^
  --hidden-import   openpyxl.utils ^
  --hidden-import   openpyxl.writer.excel ^
  %ENTRY%

if errorlevel 1 (echo ERRO: PyInstaller falhou & pause & exit /b 1)

echo.
echo [4/4] Concluido!
echo    Executavel: dist\%APP_NAME%.exe
pause
