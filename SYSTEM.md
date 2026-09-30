# SYSTEM.md - DIRETRIZES DE GOVERNANÇA GLOBAL E DESENVOLVIMENTO (UPVISION)

Este documento estabelece a Constituição e as Regras Gerais de Governança para os agentes de Inteligência Artificial e Engenheiros atuantes no **UpVision**. O cumprimento destas normas é obrigatório e inegociável.

---

## 1. Princípios Gerais e Natureza do Projeto

1.1. **Propriedade Intelectual e Privacidade**: Este projeto é estritamente **privado, proprietário e comercial** de propriedade de **Robert Ferreira**. É terminantemente proibido o uso de termos relativos a ecossistemas open source (ex: "faça um fork", "abra um pull request", "contribuições comunitárias", "star no GitHub").
1.2. **Profissionalismo Técnico**: Toda a comunicação entre agentes e com o usuário deve ser conduzida em **Português Técnico (PT-BR)** de alto nível, precisa, objetiva e livre de redundâncias.
1.3. **Exatidão e Rigor**: Não são toleradas alucinações. Endpoints, modelos, rotas de arquivo ou fluxos não implementados no código ativo devem ser claramente apontados como **PLANEJADO** ou **VERIFICAR**.

---

## 2. Prioridades de Engenharia

2.1. **Estabilidade de Interface e Concorrência**: O event loop da interface gráfica Tkinter (`main.py`) jamais deve ser congelado por inferências de IA, downloads ou operações de I/O em lote. Todo processamento custoso roda em worker threads isoladas.
2.2. **Controle Cooperativo de Execução**: Tarefas em andamento devem responder a sinais de cancelamento imediato através de `threading.Event` (`stop_event`), garantindo liberação controlada de recursos e VRAM.
2.3. **Aceleração e Resiliência de Hardware**: O sistema prioriza aceleração via GPU dedicada NVIDIA (CUDA com FP16/half), mantendo sempre um caminho estável de execução de contingência em CPU.

---

## 3. Gestão de Risco e Fluxos Centrais

3.1. **Regra de Alteração de Fluxos Centrais**: É terminantemente proibido modificar a arquitetura do motor de inferência (`engine.py`), dependências de baixo nível (`torch`, `basicsr`, `realesrgan`) ou a lógica de carregamento de modelos sem alerta de risco e especificação prévia.
3.2. **Comando de Bloqueio Obrigatório (Stop & Wait)**: Alterações de médio ou grande porte requerem a criação formal em `specs/<spec_name>/` dos arquivos `plan.md` e `tasks.md`. O agente deve **parar e aguardar aprovação explícita** do usuário antes de modificar código ativo.

---

## 4. Forma de Resposta Obrigatória dos Agentes

Qualquer agente de IA configurado neste ecossistema deve, obrigatoriamente, estruturar suas respostas em quatro blocos lógicos rígidos:

1. **Problema**: Diagnóstico preciso e direto da falha ou demanda relatada.
2. **O que ocorre**: Análise técnica detalhada da causa raiz, escopo de arquivos afetados e impactos laterais no runtime.
3. **Como solucionar**: Proposta clara de solução detalhando a estratégia e a lógica técnica a ser aplicada.
4. **Código/arquivos para ajustar**: Listagem exata dos caminhos de arquivos e os trechos de código/snippets prontos para alteração.

---

## 5. Política de Documentação e Conhecimento (Documentação Viva)

5.1. **Integridade da Documentação**: Todo e qualquer ajuste na lógica de inferência, novos modelos suportados, argumentos de CLI ou componentes visuais deve se refletir na atualização imediata das especificações técnicas associadas.
5.2. **Persistência de Inteligência**: Decisões técnicas relevantes e manuais de resolução de bugs de compatibilidade devem ser formalizados em arquivos Markdown dentro da pasta `docs/`.

---

## 6. Política de Robustez e Concorrência

6.1. **Preflight Mandatório**: Nenhuma inicialização pode ocorrer sem checagem de integridade das dependências essenciais (`preflight.py`).
6.2. **Validação de Modelos**: Todos os pesos baixados devem atender ao critério de integridade mínima (> 10 MB) antes de serem disponibilizados para inferência.
6.3. **Encerramento Limpo**: Fechamentos de janela (`WM_DELETE_WINDOW`) devem conceder tempo para cancelamento de threads ativas com timeout de segurança (10s).
