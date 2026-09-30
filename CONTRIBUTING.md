# Guia Interno de Manutenção — UpVision

Este repositório é estritamente **privado e proprietário** de **Robert Ferreira**. O fluxo abaixo rege as diretrizes operacionais para alterações de código, interface gráfica, modelos neurais e documentação.

---

## 1. Antes de Iniciar Qualquer Modificação

1. **Inspeção do Workspace:** Verifique o estado atual do repositório (`git status`) e garanta que arquivos de outras sessões não sejam sobrescritos inadvertidamente.
2. **Avaliação de Risco:** Modificações no motor de inferência (`engine.py`), gerenciador de threads (`main.py`) ou dependências (`requirements.txt`) exigem planejamento prévio via `specs/<nome_da_spec>/plan.md` e `tasks.md`.
3. **Parada para Aprovação (Stop & Wait):** Aguarde consentimento explícito do proprietário antes de realizar alterações estruturais em fluxos centrais.

---

## 2. Padrões de Código e Qualidade

- **Versão Homologada do Python:** Toda modificação deve ser estritamente compatível com **Python 3.12**.
- **Tipagem e Docstrings:** Utilize Type Hints e docstrings claras em todas as novas funções e métodos de classes.
- **Tratamento Seguro de Threads:** Nunca execute operações bloqueantes (I/O intensivo, downloads ou inferência de redes neurais) na main thread do Tkinter. Sempre utilize threads auxiliares com controle via `stop_event`.
- **Limpeza de Recursos:** Ao descarregar modelos ou finalizar lotes, garanta que chamadas como `torch.cuda.empty_cache()` sejam aplicadas caso necessário para evitar vazamento de memória VRAM.

---

## 3. Política de Commits

- **Autorização Prévia:** Nenhum agente ou colaborador pode executar `git commit`, `git push` ou criar branches/tags sem solicitação explícita nesta conversa.
- **Estrutura Convencional:** Utilize o padrão Conventional Commits em Português Técnico (PT-BR):
  - `feat(modulo): descrição da funcionalidade`
  - `fix(modulo): correção de falha ou bug`
  - `docs(modulo): atualização de documentação`
  - `chore(modulo): ajustes em configurações, gitignore ou dependências`
  - `refactor(modulo): refatoração sem alteração comportamental`
- **Granularidade:** Separe commits por escopo lógico coerente. Não una documentação, arquivos de configuração e código de interface em um único commit massivo.

---

## 4. Manutenção de Documentação

Ao adicionar novos parâmetros de inferência, novos modelos suportados ou alterar o comportamento de scripts utilitários, atualize imediatamente os arquivos correspondentes em `docs/`, `ARCHITECTURE.md` e `README.md`.
