@echo off
REM ===================================================================
REM UpVision - Script de configuração e execução para Windows
REM Cria venv com Python 3.12, instala dependências (GPU ou CPU),
REM aplica patch do basicsr, baixa modelos e executa validação.
REM ===================================================================

echo.
echo ===== UpVision Setup para Windows =====
echo.

REM ------------------------------------------------------------------
REM 1. Verificar se Python 3.12 está disponível via py launcher
REM ------------------------------------------------------------------
py -3.12 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python 3.12 não encontrado.
    echo        Instale Python 3.12 de https://www.python.org/downloads/release/python-3120/
    echo        Certifique-se de que o py launcher está habilitado na instalação.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('py -3.12 --version') do echo [OK] %%v encontrado.

REM ------------------------------------------------------------------
REM 2. Criar ambiente virtual .venv312
REM ------------------------------------------------------------------
if not exist .venv312 (
    echo Criando ambiente virtual .venv312...
    py -3.12 -m venv .venv312
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao criar venv.
        pause
        exit /b 1
    )
) else (
    echo [OK] Ambiente virtual .venv312 já existe.
)

REM Ativar venv
echo Ativando ambiente virtual...
call .venv312\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao ativar venv.
    pause
    exit /b 1
)

REM ------------------------------------------------------------------
REM 3. Atualizar pip e ferramentas básicas
REM ------------------------------------------------------------------
echo Atualizando pip, setuptools e wheel...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] Falha ao atualizar pip, continuando...
)

REM ------------------------------------------------------------------
REM 4. Detectar GPU e instalar PyTorch adequado
REM ------------------------------------------------------------------
echo Detectando GPU...

nvidia-smi >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] NVIDIA GPU detectada. Instalando PyTorch com CUDA 12.1...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
) else (
    echo [AVISO] nvidia-smi não encontrado. Instalando PyTorch CPU...
    echo         Para usar GPU, instale os drivers NVIDIA e execute novamente.
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
)

if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar PyTorch.
    pause
    exit /b 1
)

REM ------------------------------------------------------------------
REM 5. Instalar BasicSR (local ou via git)
REM ------------------------------------------------------------------
echo Instalando BasicSR...
if exist temp_basicsr (
    echo   Usando cópia local em temp_basicsr/...
    pip install ./temp_basicsr
) else (
    echo   Instalando via git...
    pip install git+https://github.com/XPixelGroup/BasicSR.git
)

REM ------------------------------------------------------------------
REM 6. Instalar demais dependências
REM ------------------------------------------------------------------
echo Instalando dependências do projeto...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependências.
    pause
    exit /b 1
)

REM ------------------------------------------------------------------
REM 7. Aplicar patch do basicsr (compatibilidade torchvision)
REM ------------------------------------------------------------------
echo Aplicando patch do basicsr...
python tools\patch_basicsr_torchvision.py

REM ------------------------------------------------------------------
REM 8. Baixar modelos Real-ESRGAN
REM ------------------------------------------------------------------
echo Baixando modelos Real-ESRGAN...
python tools\download_models.py
if %errorlevel% neq 0 (
    echo [AVISO] Falha no download de modelos. Tente novamente ou baixe manualmente.
)

REM ------------------------------------------------------------------
REM 9. Validação do ambiente
REM ------------------------------------------------------------------
echo Executando validação do ambiente...
python tools\env_check.py
if %errorlevel% neq 0 (
    echo [AVISO] Validação reportou problemas, mas o ambiente pode funcionar.
)

REM ------------------------------------------------------------------
REM 10. Concluído
REM ------------------------------------------------------------------
echo.
echo ===== Setup concluído! =====
echo.
echo Para executar o aplicativo:
echo   .venv312\Scripts\activate.bat
echo   python main.py
echo.
echo Ou rode novamente este script para reconfigurar.
pause