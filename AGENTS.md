# AGENTS.md - MANUAL DE OPERAÇÃO DOS AGENTES DE IA (UPVISION)

Este documento rege a atuação, orquestração e execução de tarefas de engenharia no projeto **UpVision** através de agentes inteligentes.

---

## 1. Visão Geral do Ecossistema

O **UpVision** é um sistema corporativo proprietário de visão computacional, processamento de imagem e super-resolução local acelerada por GPU. A atuação de agentes deve manter a integridade operacional da engine de IA, o fluxo multithreaded da interface gráfica e a segurança do ambiente.

---

## 2. Processo de Trabalho e Complexidade de Mudanças

Antes de alterar qualquer linha de código, o agente ativo deve avaliar o escopo e o risco da alteração e seguir o workflow adequado:

### 2.1. Mudanças Pequenas e Triviais (Ajustes Rápidos)
* **Definição**: Correção de erros de digitação (typos), ajustes de documentação pontual, pequenos comentários explicativos, correções óbvias de sintaxe ou pequenos ajustes de estilo de widgets.
* **Workflow**: O agente atua diretamente, realiza as edições necessárias, valida a sintaxe e executa testes locais. Não requer plano formal prévio, mas deve documentar claramente a intervenção.

### 2.2. Mudanças Médias, Grandes ou Estruturais (Planejamento Obrigatório)
* **Definição**: Alteração no pipeline de inferência da `engine.py`, modificações no ciclo de vida de threads e cancelamento cooperativo (`stop_event`), atualização de dependências centrais (`torch`, `basicsr`, `realesrgan`), adições ao `main.py` com impacto no event loop do Tkinter, ou novos componentes no gerenciador de modelos.
* **Workflow**:
  1. Criação física em `specs/<nome_da_spec>/` dos arquivos `plan.md` e `tasks.md` detalhando a abordagem técnica, riscos, dependências e checklist granular.
  2. **PARADA OBRIGATÓRIA (STOP & WAIT)**: O agente interrompe as operações e solicita expressamente o "OK" do usuário no chat antes de alterar código produtivo.
  3. Somente após a aprovação expressa do usuário, os passos de implementação são iniciados, seguindo estritamente as tarefas mapeadas em `tasks.md`.

---

## 3. Gestão de Tarefas e Acompanhamento

3.1. **Criação de Tarefas**: As tarefas criadas em `tasks.md` devem ser atômicas, granulares e numeradas.
3.2. **Estados das Tasks**:
  - `[ ]` Tarefa pendente.
  - `[/]` Tarefa em andamento.
  - `[x]` Tarefa concluída.
3.3. **Revisão de Documentação**: Antes de finalizar qualquer alteração, validar se a documentação (`ARCHITECTURE.md`, `README.md`, `specs/`) reflete fielmente o estado real do código.

---

## 4. Governança de Validação e Qualidade Técnica

4.1. **Validação de Runtime e GPU**: Nenhuma alteração pode quebrar a inicialização em modo GPU (CUDA) nem o fallback seguro para CPU.
4.2. **Preflight e Tolerância a Falhas**: Scripts de bootstrap (`run.bat`, `run.sh`) e verificadores (`preflight.py`, `tools/env_check.py`) devem ser validados quanto à ausência de loops infinitos ou bloqueios silenciosos.
4.3. **Gerenciamento de Modelos**: Não adicionar URLs ou modelos sem validação de arquitetura compatível (`RRDBNet` vs `SRVGGNetCompact`) e verificação de integridade mínima de download (> 10 MB).

---

## 5. Preferências Operacionais do Proprietário

- O idioma padrão de respostas, documentação e mensagens de commit é **Português Técnico (PT-BR)**.
- **Nenhum agente pode executar `git commit`, `git push` ou criar release sem solicitação explícita do usuário nesta conversa.**
- Quando houver solicitação explícita de commit, separar as alterações por módulo e finalidade (ex: `feat(core)`, `docs(governance)`, `chore(config)`); não consolidar UI, engine, testes e documentação em um único commit sem justificativa.
- O produto é **estritamente privado e proprietário** de Robert Ferreira. É proibido o uso de termos de projetos públicos ou open source.
- Arquivos sensíveis, logs locais (`logs/`), ambientes virtuais (`.venv312/`) e binários pesados de redes neurais (`*.pth`) devem permanecer protegidos pelo `.gitignore`.
