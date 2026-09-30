# 🗺️ ROADMAP.md - Planejamento Estratégico (UpVision)

> 🔒 **USO INTERNO EXCLUSIVO**: Este roadmap alinha os ciclos de engenharia e evolução técnica do **UpVision**. É expressamente proibido o compartilhamento deste documento fora do ambiente corporativo.

---

## Legenda de Status
* ✅ **concluído**: Funcionalidade homologada, validada e ativa no código-fonte.
* 🚧 **em andamento**: Funcionalidade em estágio ativo de desenvolvimento ou validação.
* 🔲 **planejado**: Próxima evolução mapeada com arquitetura pré-definida.
* 🔬 **pesquisa**: Prova de conceito (PoC) ou análise de viabilidade técnica.

---

## ⚙️ Fases de Desenvolvimento

### 1. Motor Core, Hardware e Estabilidade (✅ concluído)
* **✅ Aceleração GPU CUDA**: Suporte nativo a aceleração NVIDIA CUDA 12.1+ com precisão mista FP16 (`half=True`) e fallback para CPU.
* **✅ Modelos Real-ESRGAN**: Integração dos modelos oficiais `RealESRGAN_x2plus.pth` e `RealESRGAN_x4plus.pth` com arquitetura `RRDBNet` (23 blocos residuais).
* **✅ Logging Estruturado e Persistente**: Sistema rotativo com `RotatingFileHandler` (5 MB, 3 backups) em `logs/upvision.log` e streaming de terminal.
* **✅ Script de Inicialização Automatizado**: `run.bat` reescrito com checagem de Python 3.12, detecção de GPU via `nvidia-smi`, criação de `.venv312` e downloads automatizados.
* **✅ Verificação de Ambiente (Preflight Check)**: Módulo `preflight.py` para detecção de integridade de dependências antes de carregar a GUI.

### 2. Interface Gráfica e Controle Cooperativo (✅ concluído)
* **✅ Gerenciador Dinâmico de Modelos**: Interface modal Tkinter (`model_manager.py`) para download, inspeção e seleção ágil de modelos `.pth`.
* **✅ Visualizador de Comparação Lado a Lado**: Inspeção com divisão interativa entre o arquivo original e a versão em super-resolução.
* **✅ Cancelamento Cooperativo Não-Bloqueante**: Utilização de `stop_event` para interrupção de processamentos em lote sem travamento de threads.
* **✅ Encerramento Limpo (WM_DELETE_WINDOW)**: Timeout de segurança (10s) para liberação de threads ativas ao fechar o aplicativo.

### 3. Expansão de Modelos e Processamento de Vídeo (🚧 em andamento)
* **🚧 Suporte à Arquitetura SRVGGNetCompact**: Expansão do `engine.py` para carregar modelos compactos de alta velocidade (ex: `realesr-general-x4v3` e modelos para ilustração/anime).
* **🔲 Processamento de Vídeo Frame a Frame**: Pipeline assíncrono para extração, upscale e reconstrução de arquivos de vídeo MP4/AVI com sincronização de áudio via FFmpeg.
* **🔲 Fila de Prioridade de Processamento**: Gerenciador de fila com ordenação por tamanho de imagem e priorização de lotes urgentes.
* **🔲 Cache Inteligente de Inferência**: Mapeamento de hash SHA-256 de imagens processadas para evitar reprocessamento desnecessário.

### 4. Otimização de Performance Extrema e Deploy (🔲 planejado / 🔬 pesquisa)
* **🔲 Inferência via TensorRT**: Conversão e compilação de modelos PyTorch para motores TensorRT (`.engine`), reduzindo o tempo de inferência pela metade em GPUs GeForce RTX.
* **🔲 Interface Gráfica Moderna (Dark Theme)**: Evolução da GUI para componentes estilizados de alta definição com suporte nativo a HiDPI e temas modernos.
* **🔬 Empacotador Executável Standalone**: Distribuição por instalador único compilado via PyInstaller/Nuitka incorporando runtime CUDA sem necessidade de Python instalado na máquina de destino.
* **🔬 Distribuição Multi-GPU**: Paralelização de lotes massivos em múltiplas placas de vídeo conectadas na mesma estação de trabalho.
