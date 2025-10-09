@echo off
REM UpVision - Script de configuração e execução para Windows
REM Este script cria o venv, instala dependências e roda o teste automático

echo === UpVision Setup para Windows ===

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python não encontrado. Instale Python 3.10 de https://www.python.org/
    pause
    exit /b 1
)

echo Python encontrado.

# Criar venv se não existir
if exist .venv310 (
    echo Removendo ambiente virtual antigo...
    rmdir /s /q .venv310
)
echo Criando ambiente virtual .venv310...
python -m venv .venv310
if %errorlevel% neq 0 (
    echo ERRO: Falha ao criar venv.
    pause
    exit /b 1
)

REM Ativar venv
echo Ativando ambiente virtual...
call .venv310\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERRO: Falha ao ativar venv.
    pause
    exit /b 1
)

REM Atualizar pip
echo Atualizando pip...
python -m pip install --upgrade pip setuptools wheel
if %errorlevel% neq 0 (
    echo AVISO: Falha ao atualizar pip, continuando...
)

REM Instalar PyTorch (CPU por padrão, ajuste para GPU se necessário)
echo Instalando PyTorch (CPU)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar PyTorch.
    pause
    exit /b 1
)

REM Instalar dependências
echo Instalando dependências do projeto...
if exist temp_basicsr (
    pip install ./temp_basicsr
) else (
    pip install git+https://github.com/XPixelGroup/BasicSR.git
)
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependências.
    pause
    exit /b 1
)

REM Aplicar patch se necessário
echo Aplicando patch do basicsr...
python tools\patch_basicsr_torchvision.py

REM Executar teste
echo Executando teste automático...
python tools\diagnostico_realesrgan.py
if %errorlevel% neq 0 (
    echo AVISO: Teste falhou, mas ambiente pode estar OK.
)

echo.
echo === Setup concluído! ===
echo Para executar o aplicativo: python main.py
echo Ou rode novamente este script para reconfigurar.
pause