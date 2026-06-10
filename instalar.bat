@echo off
:: Forçar codificação ANSI para português do Brasil
chcp 1252 >nul
title Instalador - OverClocked CPFANI

:: Configurar variáveis
set "LOG_DIR=%~dp0logs"
set "LOG_FILE=%LOG_DIR%\instalacao.log"
set "PROJECT_DIR=%~dp0"

:: Criar diretório de logs se não existir
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: Função para logar mensagens
:log
echo [%date% %time%] %~1 >> "%LOG_FILE%"
echo %~1
goto :eof

:: Cabeçalho
cls
echo ========================================
echo   INSTALADOR - OVERCLOCKED CPFANI
echo ========================================
echo.

:log "========================================"
:log "INICIOU INSTALAÇÃO - OverClocked CPFANI"
:log "========================================"

:: ============================================
:: VERIFICAÇÃO E INSTALAÇÃO: Git
:: ============================================
:log "Verificando Git..."
git --version >nul 2>&1
if %errorlevel% equ 0 (
    :log "Git já está instalado."
    echo [OK] Git já está instalado.
) else (
    :log "Git não encontrado. Iniciando instalação via WinGet..."
    echo [AGUARDANDO] Instalando Git via WinGet...
    winget install -e --id Git.Git --silent --log "%LOG_DIR%\winget-git.log"
    if %errorlevel% equ 0 (
        :log "Git instalado com sucesso."
        echo [SUCESSO] Git instalado com sucesso.
    ) else (
        :log "ERRO ao instalar Git. Código: %errorlevel%"
        echo [ERRO] Falha ao instalar Git. Verifique %LOG_DIR%\winget-git.log
    )
)
echo.

:: ============================================
:: VERIFICAÇÃO E INSTALAÇÃO: Python 3.11
:: ============================================
:log "Verificando Python 3.11+..."
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
    echo %PY_VER% | findstr /r "^3\.1[1-9] ^3\.[2-9][0-9]" >nul
    if %errorlevel% equ 0 (
        :log "Python %PY_VER% já está instalado e compatível."
        echo [OK] Python %PY_VER% já está instalado.
    ) else (
        :log "Python %PY_VER% encontrado, mas versão incompatível. Instalando Python 3.11..."
        echo [ATENÇÃO] Python %PY_VER% incompatível. Instalando Python 3.11...
        winget install -e --id Python.Python.3.11 --silent --log "%LOG_DIR%\winget-python.log"
        if %errorlevel% equ 0 (
            :log "Python 3.11 instalado com sucesso."
            echo [SUCESSO] Python 3.11 instalado. Reinicie o terminal para aplicar.
        ) else (
            :log "ERRO ao instalar Python. Código: %errorlevel%"
            echo [ERRO] Falha ao instalar Python. Verifique %LOG_DIR%\winget-python.log
        )
    )
) else (
    :log "Python não encontrado. Instalando Python 3.11..."
    echo [AGUARDANDO] Instalando Python 3.11 via WinGet...
    winget install -e --id Python.Python.3.11 --silent --log "%LOG_DIR%\winget-python.log"
    if %errorlevel% equ 0 (
        :log "Python 3.11 instalado com sucesso."
        echo [SUCESSO] Python 3.11 instalado. Reinicie o terminal para aplicar.
    ) else (
        :log "ERRO ao instalar Python. Código: %errorlevel%"
        echo [ERRO] Falha ao instalar Python. Verifique %LOG_DIR%\winget-python.log
    )
)
echo.

:: ============================================
:: VERIFICAÇÃO E INSTALAÇÃO: pip (gerenciador de pacotes)
:: ============================================
:log "Verificando pip..."
python -m pip --version >nul 2>&1
if %errorlevel% equ 0 (
    :log "pip já está disponível."
    echo [OK] pip já está disponível.
) else (
    :log "pip não encontrado. Tentando instalar..."
    echo [ATENÇÃO] pip não detectado. Tentando reparar instalação do Python...
    python -m ensurepip --upgrade
    if %errorlevel% equ 0 (
        :log "pip instalado/reparado com sucesso."
        echo [SUCESSO] pip configurado.
    ) else (
        :log "ERRO ao configurar pip."
        echo [ERRO] Não foi possível configurar pip automaticamente.
    )
)
echo.

:: ============================================
:: INSTALAÇÃO DE DEPENDÊNCIAS DO PROJETO
:: ============================================
:log "Instalando dependências do projeto (requirements.txt)..."
if exist "%PROJECT_DIR%requirements.txt" (
    echo [AGUARDANDO] Instalando dependências Python...
    python -m pip install -r "%PROJECT_DIR%requirements.txt" --user --quiet
    if %errorlevel% equ 0 (
        :log "Dependências instaladas com sucesso."
        echo [SUCESSO] Dependências Python instaladas.
    ) else (
        :log "ERRO ao instalar dependências. Código: %errorlevel%"
        echo [ERRO] Falha ao instalar dependências. Verifique o log.
    )
) else (
    :log "requirements.txt não encontrado. Pulando instalação de dependências."
    echo [INFO] requirements.txt não encontrado. Pulando etapa.
)
echo.

:: ============================================
:: VERIFICAÇÃO FINAL
:: ============================================
:log "Executando verificação final..."
echo.
echo ========================================
echo   VERIFICAÇÃO FINAL
echo ========================================

git --version >nul 2>&1 && echo [OK] Git: instalado || echo [FALHA] Git: não detectado
python --version >nul 2>&1 && echo [OK] Python: instalado || echo [FALHA] Python: não detectado
python -m pip --version >nul 2>&1 && echo [OK] pip: disponível || echo [FALHA] pip: não disponível

:log "Verificação final concluída."
echo.

:: ============================================
:: ENCERRAMENTO
:: ============================================
:log "INSTALAÇÃO CONCLUÍDA."
echo ========================================
echo   INSTALAÇÃO CONCLUÍDA!
echo ========================================
echo.
echo Log completo salvo em: %LOG_FILE%
echo.
echo Próximo passo: Configure o banco de dados e inicie o servidor.
echo.
pause
exit /b 0