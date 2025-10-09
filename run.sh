#!/bin/bash
# UpVision - Script de configuração e execução para Linux/Mac
# Este script cria o venv, instala dependências e roda o teste automático

echo "=== UpVision Setup para Linux/Mac ==="

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python3 não encontrado. Instale Python 3.10 de https://www.python.org/"
    exit 1
fi

echo "Python encontrado."

# Criar venv se não existir
if [ ! -d ".venv310" ]; then
    echo "Criando ambiente virtual .venv310..."
    python3 -m venv .venv310
    if [ $? -ne 0 ]; then
        echo "ERRO: Falha ao criar venv."
        exit 1
    fi
else
    echo "Ambiente virtual .venv310 já existe."
fi

# Ativar venv
echo "Ativando ambiente virtual..."
source .venv310/bin/activate
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao ativar venv."
    exit 1
fi

# Atualizar pip
echo "Atualizando pip..."
python -m pip install --upgrade pip setuptools wheel
if [ $? -ne 0 ]; then
    echo "AVISO: Falha ao atualizar pip, continuando..."
fi

# Instalar PyTorch (CPU por padrão, ajuste para GPU se necessário)
echo "Instalando PyTorch (CPU)..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao instalar PyTorch."
    exit 1
fi

# Instalar dependências
echo "Instalando dependências do projeto..."
pip install git+https://github.com/XPixelGroup/BasicSR.git
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao instalar dependências."
    exit 1
fi

# Aplicar patch se necessário
echo "Aplicando patch do basicsr..."
python tools/patch_basicsr_torchvision.py

# Executar teste
echo "Executando teste automático..."
python tools/diagnostico_realesrgan.py
if [ $? -ne 0 ]; then
    echo "AVISO: Teste falhou, mas ambiente pode estar OK."
fi

echo ""
echo "=== Setup concluído! ==="
echo "Para executar o aplicativo: python main.py"
echo "Ou rode novamente este script para reconfigurar."