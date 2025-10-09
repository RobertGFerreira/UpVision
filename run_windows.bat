@echo off
echo === UpVision Setup and Run Script (Windows) ===

REM Criar ambiente virtual se não existir
if not exist venv310 (
    echo Criando ambiente virtual com Python 3.10...
    py -3.10 -m venv venv310
    if errorlevel 1 (
        echo Erro ao criar venv. Certifique-se de que Python 3.10 está instalado.
        pause
        exit /b 1
    )
)

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
call venv310\Scripts\activate.bat
if errorlevel 1 (
    echo Erro ao ativar venv.
    pause
    exit /b 1
)

REM Instalar PyTorch se não estiver instalado
python -c "import torch" >nul 2>&1
if errorlevel 1 (
    echo Instalando PyTorch...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    if errorlevel 1 (
        echo Erro ao instalar PyTorch.
        pause
        exit /b 1
    )
)

REM Instalar dependências
echo Instalando dependências...
pip install -r requirements.txt
if errorlevel 1 (
    echo Erro ao instalar dependências.
    pause
    exit /b 1
)

REM Aplicar patch no basicsr se necessário
python tools\patch_basicsr_torchvision.py
if errorlevel 1 (
    echo Erro ao aplicar patch.
    pause
    exit /b 1
)

REM Executar o aplicativo
echo Iniciando UpVision...
python main.py

pause