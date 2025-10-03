# UpVision – Real-ESRGAN GUI

UpVision é uma aplicação desktop simples (Tkinter) para realizar upscale de imagens usando os modelos **Real-ESRGAN** já existentes no projeto.

## Recursos

- Seleção múltipla de arquivos de imagem (PNG, JPG, TIFF, WebP etc.).
- Escolha da pasta de destino para salvar os resultados.
- Seleção do checkpoint `.pth` localizado em `models_realesrgan/`.
- Definição se o processamento deve ocorrer em CPU ou GPU (CUDA), quando disponível.
- Execução em thread separada com barra de progresso e log em tempo real.
- Scripts auxiliares para diagnóstico do ambiente e patch do `basicsr`.

## Guia completo: do download ao primeiro uso

1. **Instalar o Python 3.10 (64 bits)**

    - Acesse <https://www.python.org/downloads/release/python-31010/>.
    - Baixe o instalador Windows x64 (Executável).
    - Ao executar, marque a opção **Add Python to PATH** antes de clicar em *Install Now*.

1. **Verificar a instalação**

    ```powershell
    python --version
    ```

    O comando deve retornar algo como `Python 3.10.x`.

1. **Preparar a pasta do aplicativo**

    - Copie a pasta do UpVision para o local onde deseja rodar o sistema.
    - Dentro dela, garanta que existam os diretórios:
        - `models_realesrgan/` com pelo menos um checkpoint (ex.: `RealESRGAN_x2plus.pth`, disponível em <https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.0/RealESRGAN_x2plus.pth>).
        - `assets/` (opcional) contendo imagens de teste que serão processadas.
    - Para automatizar o download dos checkpoints oficiais, rode:

        ```powershell
        python tools/download_models.py
        ```

        O script criará a pasta `models_realesrgan/` (se necessário) e fará o download dos arquivos `.pth` padrão. Use `python tools/download_models.py --help` para ver opções como alterar o destino ou baixar apenas modelos específicos.

1. **Abrir o PowerShell na pasta do app**

    ```powershell
    cd "C:\caminho\para\UpVision"
    ```

1. **Criar e ativar um ambiente virtual**

    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```

1. **Atualizar ferramentas básicas do pip**

    ```powershell
    python -m pip install --upgrade pip setuptools wheel
    ```

1. **Instalar PyTorch conforme o hardware**

    - GPU (CUDA 12.1):

        ```powershell
        pip install torch==2.5.1+cu121 torchvision==0.20.1+cu121 torchaudio==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121
        ```

    - CPU apenas:

        ```powershell
        pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1
        ```

1. **Instalar as demais dependências do projeto**

    ```powershell
    pip install -r requirements.txt
    ```

1. **(Opcional) Rodar o cheque de ambiente**

    ```powershell
    python tools/env_check.py
    ```

1. **Executar o aplicativo**

   ```powershell
   python main.py
   ```

   Dentro da interface:
   - Clique em **Adicionar imagens…** para escolher arquivos (por padrão o diálogo abre em `assets/`).
   - Defina a pasta de saída (a sugestão inicial também aponta para `assets/`).
   - Escolha o modelo desejado na lista e o dispositivo (CPU ou CUDA).
   - Pressione **Iniciar upscale** e acompanhe o progresso no painel inferior.

## Estrutura

```text
UpVision/
  main.py                    # Interface gráfica
  engine.py                  # Lógica de carregamento do modelo e processamento
  README.md                  # Este arquivo
  requirements.txt           # Dependências específicas da aplicação
  tools/
    env_check.py             # Verifica torch / CUDA / realesrgan
    diagnostico_realesrgan.py# Teste rápido de inferência em uma imagem
    patch_basicsr_torchvision.py  # Ajusta import legacy do basicsr
```

Os modelos `.pth` podem estar em `models_realesrgan/` (dentro da própria pasta do aplicativo) ou em `../models_realesrgan`. Por padrão o motor procura arquivos como `RealESRGAN_x2plus.pth`.

> Para uso portátil (copiar apenas a pasta do UpVision), coloque os arquivos do modelo em `UpVision/models_realesrgan/` e as imagens de teste em `UpVision/assets/`. O aplicativo detecta automaticamente essa estrutura.

## Instalação

1. Crie e ative um ambiente virtual (recomendado Python 3.10).
2. Atualize as ferramentas básicas: `python -m pip install --upgrade pip setuptools wheel`.
3. Instale PyTorch de acordo com o hardware:
   - **GPU (CUDA 12.1)**:

     ```powershell
     pip install torch==2.5.1+cu121 torchvision==0.20.1+cu121 torchaudio==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121
     ```

   - **CPU apenas**:

     ```powershell
     pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1
     ```

4. Instale as demais dependências:

   ```powershell
   pip install -r requirements.txt
   ```

5. (Opcional) Rode os utilitários em `tools/` para validar o ambiente.

### Modo standalone

Para rodar o app em outro local, copie a pasta `upscale app` inteira e dentro dela adicione:

- `models_realesrgan/` com os checkpoints `.pth` necessários;
- `assets/` (opcional) contendo as imagens que deseja processar.

Ao abrir o aplicativo, a seleção de arquivos e a pasta de destino já apontarão para `assets/`, e a barra de status mostrará o caminho atual dos modelos.

## Execução

```powershell
python main.py
```

Passos típicos dentro do aplicativo:

1. Clique em **Adicionar imagens…** e selecione os arquivos desejados.
2. Escolha a pasta de destino para salvar as imagens processadas.
3. Selecione o checkpoint Real-ESRGAN na lista.
4. Defina o dispositivo (CPU ou CUDA).
5. Clique em **Iniciar upscale**.

O programa criará os arquivos com sufixo `_x2`, `_x4`, etc., conforme o fator do modelo escolhido.

## Scripts auxiliares (`tools/`)

- `env_check.py`: imprime versões de Python, torch, torchvision, torchaudio, realesrgan e basicsr.
- `diagnostico_realesrgan.py`: realiza um upscale de teste usando o modelo `RealESRGAN_x2plus.pth` e salva `teste_realesrgan_sr.jpg`.
- `patch_basicsr_torchvision.py`: aplica o patch necessário quando `torchvision.transforms.functional_tensor` não está disponível.
- `download_models.py`: baixa automaticamente os checkpoints oficiais do Real-ESRGAN para a pasta configurada.

Execute-os com `python tools/<script>.py` (respeitando o ambiente virtual).

## Problemas comuns

| Situação | Causa provável | Solução |
|----------|----------------|---------|
| Nenhum modelo listado | Pasta `models_realesrgan` vazia | Baixe e coloque os `.pth` no diretório mencionado |
| Erro ao importar basicsr | Incompatibilidade com torchvision | Rode `python tools/patch_basicsr_torchvision.py` |
| CUDA indisponível | Driver antigo ou PyTorch CPU | Atualize driver e reinstale PyTorch com wheels CUDA |
| Imagens não aparecem no destino | Falha de permissão ou caminho inválido | Confirme se a pasta de saída existe e está acessível |

## Licenciamento

Os modelos Real-ESRGAN seguem a licença do projeto original (veja [https://github.com/xinntao/Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)). Utilize apenas com imagens que você tem permissão para processar.
