@echo off
chcp 1252 >nul
title Instalador - OverClocked CPFANI
setlocal EnableDelayedExpansion

set "LOG_DIR=%~dp0logs"
set "LOG_FILE=%LOG_DIR%\instalacao.log"
set "PROJECT_DIR=%~dp0"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

call :log "========================================"
call :log "INICIOU INSTALACAO - OverClocked CPFANI"
call :log "========================================"

:: ============================================
:: GIT
:: ============================================
call :log "Verificando Git..."
git --version >nul 2>&1
if !errorlevel! equ 0 (
    call :log "Git ja esta instalado."
    echo [OK] Git ja esta instalado.
) else (
    call :log "Git nao encontrado. Instalando via WinGet..."
    echo [AGUARDANDO] Instalando Git...
    winget install -e --id Git.Git --silent
    if !errorlevel! equ 0 (
        call :log "Git instalado com sucesso."
        echo [SUCESSO] Git instalado.
    ) else (
        call :log "ERRO ao instalar Git. Codigo: !errorlevel!"
        echo [ERRO] Falha ao instalar Git. Verifique se o WinGet esta atualizado.
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
    echo [OK] Python !PY_VER! ja esta instalado.
) else (
    call :log "Python nao encontrado. Instalando Python 3.11..."
    echo [AGUARDANDO] Instalando Python 3.11 via WinGet...
    winget install -e --id Python.Python.3.11 --silent
    if !errorlevel! equ 0 (
        call :log "Python 3.11 instalado com sucesso."
        echo [SUCESSO] Python 3.11 instalado. REINICIE O TERMINAL para aplicar.
    ) else (
        call :log "ERRO ao instalar Python. Codigo: !errorlevel!"
        echo [ERRO] Falha ao instalar Python. Instale manualmente via python.org se necessario.
    )
)
echo.

:: ============================================
:: PIP
:: ============================================
call :log "Verificando pip..."
python -m pip --version >nul 2>&1
if !errorlevel! equ 0 (
    call :log "pip ja esta disponivel."
    echo [OK] pip ja esta disponivel.
) else (
    call :log "pip nao encontrado. Tentando reparar..."
    echo [ATENCAO] Configurando pip...
    python -m ensurepip --upgrade >nul 2>&1
    if !errorlevel! equ 0 (
        call :log "pip configurado com sucesso."
        echo [SUCESSO] pip configurado.
    ) else (
        call :log "ERRO ao configurar pip."
        echo [ERRO] Nao foi possivel configurar pip automaticamente.
    )
)
echo.

:: ============================================
:: C++ BUILD TOOLS (PARA PYTHON > 3.12)
:: ============================================
call :log "Analisando necessidade de compilador C++..."
set "NEEDS_CPP=0"
set "PY_MAJOR=0"
set "PY_MINOR=0"

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PY_VER_FULL=%%v"
for /f "tokens=1,2 delims=." %%a in ("!PY_VER_FULL!") do (
    set "PY_MAJOR=%%a"
    set "PY_MINOR=%%b"
)

if !PY_MAJOR! gtr 3 set "NEEDS_CPP=1"
if !PY_MAJOR! equ 3 if !PY_MINOR! gtr 12 set "NEEDS_CPP=1"

if !NEEDS_CPP! equ 1 (
    call :log "Python !PY_VER_FULL! (>3.12) requer compilador C++."
    echo [ATENCAO] Python !PY_VER_FULL! detectado. Verificando C++ Build Tools...
    
    :: Verifica se o compilador ja esta no PATH
    where cl.exe >nul 2>&1
    if !errorlevel! equ 0 (
        call :log "Compilador C++ ja disponivel no sistema."
        echo [OK] C++ Build Tools ja instalado.
    ) else (
        call :log "C++ Build Tools nao encontrado. Iniciando instalacao via WinGet..."
        echo [AGUARDANDO] Instalando Microsoft Visual C++ Build Tools...
        echo [INFO] Este processo pode demorar varios minutos. Nao feche a janela.
        winget install -e --id Microsoft.VisualStudio.2022.BuildTools --override "--passive --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended --norestart" >> "%LOG_FILE%" 2>&1
        if !errorlevel! equ 0 (
            call :log "C++ Build Tools instalado/verificado com sucesso."
            echo [SUCESSO] Ambiente C++ configurado.
        ) else (
            call :log "ATENCAO: Nao foi possivel instalar C++ Build Tools automaticamente."
            echo [AVISO] Se a instalacao de pacotes falhar, instale os Build Tools manualmente.
        )
    )
) else (
    call :log "Python !PY_VER_FULL! detectado. Compilador C++ nao necessario para instalacao basica."
    echo [OK] Python !PY_VER_FULL! nao requer C++ Build Tools obrigatorios.
)
echo.

:: ============================================
:: DEPENDENCIAS DO PROJETO
:: ============================================
call :log "Atualizando gerenciadores de pacotes Python..."
echo [AGUARDANDO] Atualizando pip, setuptools e wheel...
powershell -NoProfile -ExecutionPolicy Bypass -Command "python -m pip install --upgrade pip setuptools wheel; exit $LASTEXITCODE" >nul 2>&1
set "UPDATE_EXIT=!errorlevel!"
if !UPDATE_EXIT! equ 0 (
    call :log "Gerenciadores de pacotes atualizados com sucesso."
    echo [SUCESSO] pip, setuptools e wheel atualizados.
) else (
    call :log "ATENCAO: Falha ao atualizar gerenciadores. Continuando mesmo assim..."
    echo [ATENCAO] Nao foi possivel atualizar o pip. Tentando continuar...
)
echo.

call :log "Instalando dependencias do projeto (requirements.txt)..."
if exist "%PROJECT_DIR%requirements.txt" (
    echo [AGUARDANDO] Instalando pacotes Python via PowerShell...
    echo [INFO] Processo pode demorar. Aguarde a mensagem de conclusao.
    powershell -NoProfile -ExecutionPolicy Bypass -Command "python -m pip install -r '%PROJECT_DIR%requirements.txt' --prefer-binary --user; exit $LASTEXITCODE" >> "%LOG_FILE%" 2>&1
    set "PIP_EXIT=!errorlevel!"
    if !PIP_EXIT! equ 0 (
        call :log "Dependencias instaladas com sucesso."
        echo [SUCESSO] Todas as dependencias foram instaladas.
    ) else (
        call :log "ERRO ao instalar dependencias. Codigo: !PIP_EXIT!"
        echo [ERRO] Falha ao instalar dependencias. Verifique o log ou tente com Python 3.11/3.12.
    )
) else (
    call :log "requirements.txt nao encontrado. Pulando..."
    echo [INFO] requirements.txt nao encontrado. Pulando etapa.
)
echo.

:: ============================================
:: VERIFICACAO FINAL
:: ============================================
call :log "Executando verificacao final..."
echo.
echo ========================================
echo   VERIFICACAO FINAL
echo ========================================
git --version >nul 2>&1 && echo [OK] Git: instalado || echo [FALHA] Git: nao detectado
python --version >nul 2>&1 && echo [OK] Python: instalado || echo [FALHA] Python: nao detectado
python -m pip --version >nul 2>&1 && echo [OK] pip: disponivel || echo [FALHA] pip: nao disponivel

call :log "INSTALACAO CONCLUIDA."
echo.
echo ========================================
echo   INSTALACAO CONCLUIDA!
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