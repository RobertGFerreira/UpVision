# Plan — UpVision: Ambiente, Logging e GPU

**Data:** 2026-09-27  
**Escopo:** Setup completo do ambiente de execução do UpVision com Python moderno, log em arquivo, download automático de modelos e priorização de GPU (CUDA).

---

## 1. Diagnóstico atual

### 1.1 Python disponível na máquina
| Versão | Caminho |
|--------|---------|
| 3.14 (padrão global via `py`) | `C:\...\Python314\python.exe` |
| 3.13 | `C:\...\Python313\python.exe` |
| **3.12** (escolhido para o projeto) | `C:\...\Python312\python.exe` |

### 1.2 Compatibilidade das dependências com Python moderno

| Dependência | 3.10 | 3.11 | 3.12 | 3.13 | 3.14 |
|---|---|---|---|---|---|
| `torch` (cu121+) | ✅ | ✅ | ✅ | ✅ (2.5+) | ⚠️ experimental |
| `realesrgan 0.3.0` | ✅ | ✅ | ✅ + patch | ⚠️ requer fork | ❌ |
| `basicsr` | ✅ | ✅ | ✅ + patch | ⚠️ | ❌ |
| `facexlib 0.3.0` | ✅ | ✅ | ✅ | ⚠️ | ❌ |
| `opencv-python-headless` | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| `Pillow ≥ 10` | ✅ | ✅ | ✅ | ✅ | ✅ |

> **Decisão de versão:** usar **Python 3.12** com o venv `.venv312`.  
> É a versão mais recente com suporte sólido ao stack `basicsr/realesrgan`.  
> Python 3.13+ ainda não é suportado pelo `realesrgan 0.3.0` upstream.  
> Python 3.12 tem `distutils` removido → precisamos pinnar `setuptools>=68` explicitamente.

### 1.3 Problemas identificados no projeto atual

1. **`run.bat` com erros de sintaxe** — linhas `# comentário` (Unix) dentro de `.bat`; devem ser `REM`.
2. **PyTorch instalado como CPU** no `run.bat` — não aproveita a GPU Nvidia.
3. **Sem venv criado** — projeto não possui `.venv312` ou similar.
4. **Sem log em arquivo** — apenas `print()` no terminal, sem persistência.
5. **`download_models.py` com URL errada** — `RealESRGAN_x4plus.pth` aponta para `realesr-general-x4v3.pth` (modelo diferente, arquitetura incompatível com `RRDBNet` usado em `_build_upsampler`).
6. **`_first_run_sentinel`** tenta auto-teste sem verificar se modelos foram baixados.
7. **Detecção de CUDA tardia** — só ocorre quando a janela abre, sem log prévio.

### 1.4 O que já foi feito nesta sessão
- [x] Criado `logging_config.py` com `RotatingFileHandler` (5 MB, 3 backups) + console
- [x] `engine.py` integrado com logger nomeado `upvision.engine`
- [x] `main.py` inicializa logging antes de criar a janela Tk e loga device preferido

---

## 2. Abordagem técnica

### 2.1 Ambiente virtual com Python 3.12
- Criar `.venv312` usando `py -3.12 -m venv .venv312`
- Instalar `setuptools>=68` primeiro (necessário para `distutils` em 3.12)
- Instalar PyTorch com suporte CUDA 12.1 via índice oficial PyTorch
- Instalar demais dependências do `requirements.txt`
- Aplicar patch `basicsr/data/degradations.py` (script já existe em `tools/patch_basicsr_torchvision.py`)

### 2.2 Script `run.bat` reescrito
- Corrigir todos os `# comentários` → `REM comentários` (sintaxe correta para `.bat`)
- Detectar automaticamente CUDA na máquina via `nvidia-smi`
- Selecionar índice de torch correto: `cu121` (GPU) ou `cpu` (fallback)
- Baixar modelos automaticamente via `tools/download_models.py` após setup
- Verificar Python 3.12 explicitamente com `py -3.12`

### 2.3 Correção das URLs dos modelos
- `RealESRGAN_x2plus.pth` → URL mantida (correta)
- `RealESRGAN_x4plus.pth` → corrigir para URL do release v0.1.0 (usa `RRDBNet x4`, compatível)
- Ambos os modelos devem usar `RRDBNet` com `num_block=23`

### 2.4 Logging
- `logging_config.py` já criado — logs em `logs/upvision.log`
- `engine.py` já integrado com logger `upvision.engine`
- `tools/download_models.py` integrado com logger `upvision.download`
- Log de hardware no startup: GPU name, VRAM disponível (via `torch.cuda.mem_get_info`)

### 2.5 GPU como padrão
- `_populate_devices()` já seleciona `cuda` como padrão quando disponível
- `_normalise_device("auto")` retorna `cuda` se disponível
- `half=True` ativado apenas em device `cuda` (correto, já implementado)
- `run.bat` usa CUDA 12.1 por padrão com fallback automático para CPU

### 2.6 Atualização do `requirements.txt`
- Adicionar `setuptools>=68` (necessário para Python 3.12, pois `distutils` foi removido)
- Manter `realesrgan==0.3.0` pinado (versão testada com o patch)

### 2.7 Verificação de dependências no startup (preflight check)
Antes de abrir a janela Tk, o `main.py` executa uma checagem de todas as
bibliotecas obrigatórias (torch, realesrgan, basicsr, PIL, numpy, cv2).
- Se alguma faltar, exibe um `messagebox.showerror` amigável listando as
  ausentes e encerra sem abrir a GUI.
- Se torch estiver presente mas sem CUDA, mostra aviso (mas permite continuar
  em CPU).

### 2.8 Gerenciamento de modelos na UI
- **Bloqueio de abertura sem modelos:** se `models_realesrgan/` estiver vazio
  (nenhum `.pth`), o app exibe um diálogo modal obrigatório de download antes
  de mostrar a janela principal.
- **Diálogo de download de modelos:** uma `Toplevel` com:
  - Lista de modelos disponíveis do `MODEL_REGISTRY` com checkboxes
  - Status de cada modelo ("baixado" / "ausente")
  - Botão "Baixar selecionados" que faz download em thread separada com
    barra de progresso
  - Após download, refresca o Combobox de modelos automaticamente
- **Acesso permanente via menu/botão:** além do diálogo obrigatório na
  primeira execução, a janela principal terá um botão "Gerenciar modelos…"
  no frame de opções, permitindo baixar modelos adicionais ou trocar o
  modelo ativo a qualquer momento.

### 2.9 Controle cooperativo de jobs (stop_event)
Padrão extraído do Projeto Rural (`ai_runtime_state.py` e
`ollama_client.py`):
- Criar um `threading.Event` (`_stop_event`) no `UpscaleApp`.
- Passar o `_stop_event` para `engine.process_batch()` via parâmetro.
- No loop de processamento de imagens, verificar `stop_event.is_set()` a
  cada iteração — se acionado, interrompe o batch imediatamente e emite
  evento `"cancelled"`.
- O botão "Cancelar" chama `_stop_event.set()` em vez de exibir o
  `messagebox` atual (que é inútil).
- Ao iniciar novo batch, `_stop_event.clear()` é chamado.
- Ao fechar a janela (`WM_DELETE_WINDOW`), `_stop_event.set()` é chamado
  para garantir encerramento limpo das threads.
- Timeout de segurança: se a thread não encerrar em 10s após
  `_stop_event.set()`, forçar `thread.join(timeout=10)` e encerrar.

### 2.10 Modelo registrado com arquitetura correta
O `MODEL_REGISTRY` em `download_models.py` passa a incluir também a
arquitetura esperada (`rrdb` vs `srvgg`) para que o `engine.py` possa
instanciar a rede correta. Por ora, todos os modelos usam `RRDBNet`, mas a
estrutura fica preparada para modelos futuros (`SRVGGNetCompact`).

---

## 3. Arquivos afetados

| Arquivo | Ação |
|---|---|
| `run.bat` | Reescrever — GPU detection, Python 3.12, download models, corrigir sintaxe `.bat` |
| `requirements.txt` | Adicionar `setuptools>=68` |
| `tools/download_models.py` | Corrigir URL `RealESRGAN_x4plus.pth` + integrar logging + expor `MODEL_REGISTRY` |
| `logging_config.py` | ✅ Criado nesta sessão |
| `engine.py` | ✅ Logging integrado + adicionar `stop_event` no `process_batch` |
| `main.py` | ✅ Logging startup + adicionar preflight check + model manager + stop_event + `WM_DELETE_WINDOW` handler |
| `tools/env_check.py` | Atualizar para reportar Python 3.12+ e CUDA + VRAM |
| `model_manager.py` (**novo**) | Diálogo Tkinter de gerenciamento de modelos (download, seleção, status) |
| `preflight.py` (**novo**) | Checagem de dependências obrigatórias antes de abrir a GUI |

---

## 4. Riscos e mitigações

| Risco | Probabilidade | Mitigação |
|---|---|---|
| `basicsr` falha no Python 3.12 (distutils) | Alta | Instalar `setuptools>=68` + patch automático |
| CUDA não disponível | Baixa | Fallback automático para CPU com aviso claro nos logs |
| `realesrgan 0.3.0` incompatível Python 3.13+ | Alta | Fixar em Python 3.12 com `.venv312` |
| Driver NVIDIA desatualizado para CUDA 12.1 | Média | Checar `nvidia-smi` no `run.bat` + log de aviso |
| URL de modelo incorreta gera crash no auto-teste | Alta | Corrigir URL + validar arquivo baixado com tamanho mínimo |
| Thread de upscale trava ao fechar janela | Média | `stop_event.set()` no `WM_DELETE_WINDOW` + `thread.join(timeout=10)` |
| Download de modelo falha no meio | Média | Deletar arquivo parcial + retry com log + validação de tamanho |

