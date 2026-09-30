# Tasks — UpVision: Setup Ambiente, GPU e Logging

**Spec:** `specs/setup_ambiente_gpu_logging_v1/plan.md`  
**Data:** 2026-09-27  
**Legenda:** `[ ]` pendente · `[/]` em andamento · `[x]` concluído

---

## FASE 1 — Logging (concluída)

- [x] **T-01** Criar `logging_config.py` com `RotatingFileHandler` (5 MB, 3 backups) e `StreamHandler`
- [x] **T-02** Integrar logger `upvision.engine` em `engine.py`
- [x] **T-03** Inicializar logging em `main.py` antes da criação da janela Tk
- [x] **T-04** Integrar logger `upvision.download` em `tools/download_models.py`
- [x] **T-05** Adicionar log de hardware no startup da engine: GPU name, VRAM total e VRAM disponível

---

## FASE 2 — Correção de Bugs Críticos (concluída)

- [x] **T-06** Corrigir `run.bat` — substituir todos os `# comentários` por `REM` (reescrita completa)
- [x] **T-07** Corrigir URL do modelo `RealESRGAN_x4plus.pth` em `tools/download_models.py`
- [x] **T-08** Adicionar validação de tamanho mínimo do arquivo `.pth` após download (mínimo 10 MB)

---

## FASE 3 — Python 3.12 e Ambiente Virtual (concluída)

- [x] **T-09** Adicionar `setuptools>=68` no `requirements.txt`
- [x] **T-10** Reescrever `run.bat` completo (GPU detection, Python 3.12, download models, patch, env_check)
- [x] **T-11** Atualizar `tools/env_check.py` (Python 3.12+, CUDA, VRAM, modelos, patch status)

---

## FASE 4 — Preflight Check (concluída)

- [x] **T-12** Criar `preflight.py` com `check_dependencies() -> PreflightResult`
- [x] **T-13** Integrar `preflight.py` no `main.py` — bloqueia abertura se faltar dependência

---

## FASE 5 — Gerenciamento de Modelos na UI (concluída)

- [x] **T-14** Criar `model_manager.py` com classe `ModelManagerDialog(tk.Toplevel)`
- [x] **T-15** Integrar `ModelManagerDialog` como modal obrigatório quando não há modelos
- [x] **T-16** Adicionar botão "Gerenciar modelos…" no frame de Opções

---

## FASE 6 — Controle Cooperativo de Jobs (concluída)

- [x] **T-17** Adicionar `_stop_event = threading.Event()` ao `__init__` de `UpscaleApp`
- [x] **T-18** Modificar `engine.process_batch()` para aceitar `stop_event` com cancelamento cooperativo
- [x] **T-19** Modificar `_on_cancel()` — cancelamento real via `stop_event.set()`
- [x] **T-20** Modificar `_on_start()` — `stop_event.clear()` e guardar referência à thread
- [x] **T-21** Tratar evento `"cancelled"` no `_poll_queue()` com messagebox de resumo
- [x] **T-22** Handler `WM_DELETE_WINDOW` para encerramento limpo com `thread.join(timeout=10)`

---

## FASE 7 — GPU como Padrão e Robustez

- [x] **T-23** `_populate_devices()` já seleciona `cuda` como padrão quando CUDA disponível (validado)
- [x] **T-24** Adicionar label de aviso visual no status quando app roda em CPU
- [x] **T-25** `_build_upsampler` confirma `half=True` apenas em device `cuda*` (validado)

---

## FASE 8 — Documentação e Gitignore

- [x] **T-26** Atualizar `README.md`
- [x] **T-27** Garantir entries no `.gitignore` para `logs/`, `.venv312/`, `*.pth`

---

## Checklist de Validação Final

Antes de considerar a spec concluída:

- [ ] `run.bat` executa do zero sem erros no Windows 11
- [ ] `python main.py` sem modelos → abre diálogo de download obrigatório
- [ ] `python main.py` com modelos → abre GUI com GPU selecionada por padrão
- [ ] Preflight check bloqueia abertura se faltar dependência
- [ ] Arquivo `logs/upvision.log` é criado e populado corretamente
- [ ] Download dos dois modelos `.pth` funciona sem erro via diálogo
- [ ] Botão "Gerenciar modelos…" abre diálogo e refresca Combobox
- [ ] Botão "Cancelar" interrompe batch entre imagens (sem travar)
- [ ] Fechar janela durante processamento encerra thread em até 10s
- [ ] Auto-teste inicial processa `teste_realesrgan.jpg` com sucesso
- [ ] Log exibe nome da GPU e VRAM no startup
