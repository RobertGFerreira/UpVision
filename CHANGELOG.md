# Changelog — UpVision

Todas as alterações notáveis neste projeto corporativo serão documentadas neste arquivo.

O formato baseia-se nas melhores práticas de versionamento semântico e registros internos corporativos.

---

## [1.1.0] - 2026-09-30

### Adicionado
- **Suite de Governança e Documentação**: Criação de `.ai-context.md`, `AGENTS.md`, `ARCHITECTURE.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE.md`, `ROADMAP.md`, `SECURITY.md`, `SYSTEM.md` e pasta `docs/` (`arquitetura.md`, `modelos_ia.md`, `guia_execucao.md`, `COMMIT_POLICY.md`, `seguranca-operacao.md`).
- **Gerenciador de Modelos Dinâmico (`model_manager.py`)**: Diálogo modal Tkinter permitindo download sob demanda, verificação de existência e seleção rápida de modelos Real-ESRGAN.
- **Sistema de Preflight Check (`preflight.py`)**: Checagem de requisitos de ambiente, PyTorch, CUDA, OpenCV, PIL e dependências essenciais antes da abertura da interface.
- **Logging Rotativo Estruturado (`logging_config.py`)**: Implementação de `RotatingFileHandler` gravando em `logs/upvision.log` (5 MB, 3 cópias de backup) com saída simultânea no console.
- **Cancelamento Cooperativo de Processamento**: Controle de parada imediata em lote via `threading.Event` (`stop_event`) integrado ao `engine.py` e botões de controle da UI.
- **Handler `WM_DELETE_WINDOW`**: Encerramento seguro de threads de trabalho ao fechar a janela principal, com timeout de segurança de 10s.
- **Detecção Avançada de Hardware**: Relatório automático de GPU NVIDIA, VRAM total e disponível no startup do sistema.

### Modificado
- **`.gitignore`**: Reestruturação completa com regras para dados sensíveis, ambientes virtuais (.venv312), pesos pesados de redes neurais (*.pth, *.pt, *.onnx), logs, caches e saídas geradas.
- **`run.bat`**: Reescrita integral com sintaxe nativa batch (`REM`), detecção de Python 3.12, verificação de GPU via `nvidia-smi`, instalação de PyTorch compatível com CUDA 12.1 e download automatizado de modelos.
- **`tools/download_models.py`**: Correção de URLs de download para modelos compatíveis com `RRDBNet` e adição de validação de tamanho mínimo de arquivo (> 10 MB).
- **`tools/env_check.py`**: Adição de diagnóstico de versão de Python, status de patches do `basicsr` e capacidade de VRAM.
- **`engine.py`**: Integração com logger `upvision.engine`, suporte a cancelamento de lotes e cálculo com precisão mista FP16 (`half=True`) em dispositivos CUDA.
- **`main.py`**: Integração de logging, preflight checks, abertura condicional do gerenciador de modelos e visualização de avisos de execução em CPU.

---

## [1.0.0] - 2026-09-27

### Adicionado
- **Motor de Upscaling Real-ESRGAN**: Implementação inicial de super-resolução com suporte aos fatores de escala 2x, 4x e 8x.
- **Interface Gráfica Desktop (Tkinter/ttk)**: Carregamento de imagens individuais e processamento em lote.
- **Visualizador Comparativo Interativo**: Visualização lado a lado entre a imagem original e o resultado upscalado com detecção automática do par correspondente.
- **Diagnóstico e Patch do Basicsr**: Script utilitário para correção de compatibilidade entre `basicsr` e versões recentes do `torchvision`.
- **Scripts de Execução**: `run.bat` e `run.sh` para inicialização básica do ambiente de desenvolvimento.
