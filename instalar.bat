@echo off
chcp 1252 >nul
title Instalador - OverClocked CPFANI
setlocal EnableDelayedExpansion

set "LOG_DIR=%~dp0logs"
set "LOG_FILE=%LOG_DIR%\instalacao.log"
set "PROJECT_DIR=%~dp0"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

call :log "========================================"
call :log "INICIOU INSTALAÇÃO - OverClocked CPFANI"
call :log "========================================"

:: ============================================
:: GIT
:: ============================================
call :log "Verificando Git..."
git --version >nul 2>&1
if !errorlevel! equ 0 (
    call :log "Git já está instalado."
    echo [OK] Git já está instalado.
) else (
    call :log "Git não encontrado. Instalando via WinGet..."
    echo [AGUARDANDO] Instalando Git...
    winget install -e --id Git.Git --silent
    if !errorlevel! equ 0 (
        call :log "Git instalado com sucesso."
        echo [SUCESSO] Git instalado.
    ) else (
        call :log "ERRO ao instalar Git. Código: !errorlevel!"
        echo [ERRO] Falha ao instalar Git. Verifique se o WinGet está atualizado.
    )
)
echo.

:: ============================================
:: PYTHON
:: ============================================
call :log "Verificando Python..."
python --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
    call :log "Python !PY_VER! detectado."
    echo [OK] Python !PY_VER! já está instalado.
) else (
    call :log "Python não encontrado. Instalando Python 3.11..."
    echo [AGUARDANDO] Instalando Python 3.11 via WinGet...
    winget install -e --id Python.Python.3.11 --silent
    if !errorlevel! equ 0 (
        call :log "Python 3.11 instalado com sucesso."
        echo [SUCESSO] Python 3.11 instalado. REINICIE O TERMINAL para aplicar.
    ) else (
        call :log "ERRO ao instalar Python. Código: !errorlevel!"
        echo [ERRO] Falha ao instalar Python. Instale manualmente via python.org se necessário.
    )
)
echo.

:: ============================================
:: PIP
:: ============================================
call :log "Verificando pip..."
python -m pip --version >nul 2>&1
if !errorlevel! equ 0 (
    call :log "pip já está disponível."
    echo [OK] pip já está disponível.
) else (
    call :log "pip não encontrado. Tentando reparar..."
    echo [ATENÇÃO] Configurando pip...
    python -m ensurepip --upgrade >nul 2>&1
    if !errorlevel! equ 0 (
        call :log "pip configurado com sucesso."
        echo [SUCESSO] pip configurado.
    ) else (
        call :log "ERRO ao configurar pip."
        echo [ERRO] Não foi possível configurar pip automaticamente.
    )
)
echo.

:: ============================================
:: DEPENDÊNCIAS DO PROJETO
:: ============================================
call :log "Instalando dependências do projeto..."
if exist "%PROJECT_DIR%requirements.txt" (
    echo [AGUARDANDO] Instalando pacotes Python...
    python -m pip install -r "%PROJECT_DIR%requirements.txt" --user
    if !errorlevel! equ 0 (
        call :log "Dependências instaladas com sucesso."
        echo [SUCESSO] Dependências Python instaladas.
    ) else (
        call :log "ERRO ao instalar dependências. Código: !errorlevel!"
        echo [ERRO] Falha ao instalar dependências. Verifique o log.
    )
) else (
    call :log "requirements.txt não encontrado. Pulando..."
    echo [INFO] requirements.txt não encontrado. Pulando etapa.
)
echo.

:: ============================================
:: VERIFICAÇÃO FINAL
:: ============================================
call :log "Executando verificação final..."
echo.
echo ========================================
echo   VERIFICAÇÃO FINAL
echo ========================================
git --version >nul 2>&1 && echo [OK] Git: instalado || echo [FALHA] Git: não detectado
python --version >nul 2>&1 && echo [OK] Python: instalado || echo [FALHA] Python: não detectado
python -m pip --version >nul 2>&1 && echo [OK] pip: disponível || echo [FALHA] pip: não disponível

call :log "INSTALAÇÃO CONCLUÍDA."
echo.
echo ========================================
echo   INSTALAÇÃO CONCLUÍDA!
echo ========================================
echo.
echo Log completo salvo em: %LOG_FILE%
echo.
pause
exit /b 0

:log
echo [%date% %time%] %~1 >> "%LOG_FILE%"
echo %~1
goto :eof