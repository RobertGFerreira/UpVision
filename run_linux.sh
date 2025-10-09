#!/bin/bash
echo "=== UpVision Setup and Run Script (Linux) ==="

# Criar ambiente virtual se não existir
if [ ! -d "venv310" ]; then
    echo "Criando ambiente virtual com Python 3.10..."
    python3.10 -m venv venv310
    if [ $? -ne 0 ]; then
        echo "Erro ao criar venv. Certifique-se de que Python 3.10 está instalado."
        exit 1
    fi
fi

# Ativar ambiente virtual
echo "Ativando ambiente virtual..."
source venv310/bin/activate
if [ $? -ne 0 ]; then
    echo "Erro ao ativar venv."
    exit 1
fi

# Instalar PyTorch se não estiver instalado
python -c "import torch" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Instalando PyTorch..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    if [ $? -ne 0 ]; then
        echo "Erro ao instalar PyTorch."
        exit 1
    fi
fi

# Instalar dependências
echo "Instalando dependências..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Erro ao instalar dependências."
    exit 1
fi

# Aplicar patch no basicsr se necessário
python tools/patch_basicsr_torchvision.py
if [ $? -ne 0 ]; then
    echo "Erro ao aplicar patch."
    exit 1
fi

# Executar o aplicativo
echo "Iniciando UpVision..."
python main.py