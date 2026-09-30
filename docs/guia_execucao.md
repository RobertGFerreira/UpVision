# Guia de Execução e Troubleshooting — UpVision

Este documento fornece instruções passo a passo para configuração, inicialização e resolução de eventuais problemas operacionais no **UpVision**.

---

## 1. Pré-Requisitos de Ambiente

- **Sistema Operacional:** Windows 10/11 (64-bit) ou Linux x86_64.
- **Python:** **Python 3.12** obrigatório. *(Atenção: versões 3.13 e superiores não são homologadas devido a incompatibilidades upstream na biblioteca `basicsr 0.3.0`)*.
- **Hardware Recomendado:**
  - Placa de Vídeo NVIDIA GeForce RTX / GTX com suporte a CUDA 12.1+.
  - Drivers NVIDIA atualizados (versão 525.60 ou superior).
  - 8 GB+ de memória RAM física e 4 GB+ de memória VRAM dedicada.

---

## 2. Inicialização Automatizada (Recomendada)

O UpVision possui um script inteligente de bootstrap para Windows:

```cmd
run.bat
```

### O que o script realiza automaticamente:
1. Detecta a instalação do Python 3.12 na máquina (`py -3.12`).
2. Cria e ativa o ambiente virtual isolado `.venv312`.
3. Detecta a presença de GPU NVIDIA via utilitário `nvidia-smi`.
4. Instala PyTorch compilado com suporte a CUDA 12.1 (ou instala versão CPU caso nenhuma GPU seja encontrada).
5. Instala `setuptools>=68` (suprindo a remoção do `distutils` no Python 3.12).
6. Instala todas as dependências restantes de `requirements.txt`.
7. Executa o patch de compatibilidade `tools/patch_basicsr_torchvision.py`.
8. Realiza o download automatizado dos modelos oficiais em `models_realesrgan/`.
9. Executa a checagem de integridade com `tools/env_check.py`.
10. Inicializa a interface gráfica principal (`main.py`).

---

## 3. Inicialização Manual Passo a Passo

Caso deseje configurar manualmente o ambiente sem utilizar o `run.bat`:

```cmd
:: 1. Criar e ativar o ambiente virtual Python 3.12
py -3.12 -m venv .venv312
.venv312\Scripts\activate

:: 2. Atualizar instalador de pacotes e ferramentas de build
python -m pip install --upgrade pip setuptools wheel

:: 3. Instalar PyTorch com suporte CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

:: 4. Instalar as demais dependências
pip install -r requirements.txt

:: 5. Aplicar o patch de degradations do torchvision no basicsr
python tools\patch_basicsr_torchvision.py

:: 6. Baixar os checkpoints neurais canônicos
python tools\download_models.py

:: 7. Validar o diagnóstico de ambiente
python tools\env_check.py

:: 8. Executar a aplicação
python main.py
```

---

## 4. Diagnóstico de Ambiente (`env_check.py`)

Para inspecionar a saúde do ambiente local sem abrir a interface gráfica, execute:

```cmd
python tools\env_check.py
```

O script emitirá um relatório com:
- Versão do Python e integridade do interpretador.
- Disponibilidade de CUDA, contagem de GPUs, nome do hardware e VRAM livre.
- Presença e tamanho dos modelos `.pth` em `models_realesrgan/`.
- Status da aplicação do patch no pacote `basicsr`.

---

## 5. Resolução de Problemas Frequentes (Troubleshooting)

### A. Erro: `ModuleNotFoundError: No module named 'distutils'`
* **Causa:** O Python 3.12 removeu a biblioteca padrão legada `distutils`, exigida pelo instalador do `basicsr`.
* **Solução:** Instale o `setuptools>=68` explicitamente no seu ambiente virtual:
  ```cmd
  pip install "setuptools>=68"
  ```

### B. Erro: `cannot import name 'rgb_to_grayscale' from 'torchvision.transforms.functional_tensor'`
* **Causa:** Versões recentes do `torchvision` reorganizaram submódulos internos que o `basicsr 0.3.0` tenta importar.
* **Solução:** Execute o patch automático incluído no repositório:
  ```cmd
  python tools\patch_basicsr_torchvision.py
  ```

### C. Alerta: `CUDA não disponível! Aplicação executando em modo CPU`
* **Causa:** O driver NVIDIA está ausente, o PyTorch foi instalado via índice padrão (somente CPU) ou a placa não possui núcleos CUDA.
* **Solução:** 
  1. Atualize os drivers da placa em `nvidia.com/drivers`.
  2. Reinstale o PyTorch apontando para o repositório CUDA 12.1:
     ```cmd
     pip install --force-reinstall torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
     ```

### D. Falha: `CUDA out of memory` durante upscale
* **Causa:** A imagem original possui dimensões muito elevadas para a quantidade de memória VRAM disponível na placa.
* **Solução:**
  - Utilize o fator de escala 2x em vez de 4x.
  - Certifique-se de que nenhum outro processo ou jogo pesado esteja competindo por recursos da GPU.
  - O UpVision já opera em FP16 half precision em CUDA para mitigar o consumo de tensores.
