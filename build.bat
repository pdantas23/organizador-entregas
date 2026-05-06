@echo off
REM ─────────────────────────────────────────────────────────────────────────────
REM build.bat — Gera o executável Windows (.exe) com PyInstaller
REM Usa venv isolado para não empacotar numpy/PIL/lxml do sistema.
REM ─────────────────────────────────────────────────────────────────────────────

set APP_NAME=OrganizadorEntregas
set ENTRY=main.py
set VENV_DIR=.venv-build

echo [1/5] Criando ambiente virtual isolado...
python -m venv %VENV_DIR%
call %VENV_DIR%\Scripts\activate.bat

echo [2/5] Instalando apenas dependencias necessarias...
pip install --quiet --upgrade pip
pip install --quiet openpyxl pyinstaller
if errorlevel 1 (echo ERRO: falha ao instalar dependencias & pause & exit /b 1)

echo [3/5] Limpando builds anteriores...
if exist build        rmdir /s /q build
if exist dist         rmdir /s /q dist
if exist "%APP_NAME%.spec" del /q "%APP_NAME%.spec"

echo [4/5] Empacotando com PyInstaller...
python -m PyInstaller ^
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
  --exclude-module  numpy ^
  --exclude-module  PIL ^
  --exclude-module  lxml ^
  --exclude-module  matplotlib ^
  --exclude-module  scipy ^
  --exclude-module  pandas ^
  %ENTRY%

if errorlevel 1 (echo ERRO: PyInstaller falhou & call deactivate & pause & exit /b 1)

call deactivate

echo.
echo [5/5] Concluido!
echo    Executavel: dist\%APP_NAME%.exe
pause
