# Política de Commits e Versionamento — UpVision

Este documento define as regras corporativas para criação de commits e gerenciamento de branches no repositório **UpVision**.

---

## 1. Regra Fundamental de Autorização

> ⚠️ **ATENÇÃO:** Nenhum agente de Inteligência Artificial ou desenvolvedor está autorizado a executar comandos de escrita no histórico Git (`git commit`, `git push`, criação de tags ou merges) sem a **solicitação expressa e inequívoca do proprietário do projeto** no contexto da sessão ativa.

---

## 2. Padrão de Mensagens de Commit

As mensagens de commit devem adotar a convenção **Conventional Commits** e ser redigidas obrigatoriamente em **Português Técnico (PT-BR)**:

```text
tipo(escopo): descrição concisa no imperativo ou indicativo direto

[corpo opcional detalhando a motivação e impactos técnicos]
```

### Tipos Permitidos
* `feat`: Implementação de nova funcionalidade ou expansão de capacidades.
* `fix`: Correção de defeito, bug ou falha operacional.
* `docs`: Inclusão ou aprimoramento de documentação técnica ou governança.
* `refactor`: Refatoração estrutural de código sem modificação de comportamento externo.
* `chore`: Ajustes de dependências, `.gitignore`, scripts de build ou configurações de ambiente.
* `test`: Adição ou modificação de scripts de teste e validação de comparação.
* `perf`: Otimizações voltadas especificamente para latência de inferência ou consumo de VRAM.

### Escopos Recomendados para o UpVision
* `(core)` ou `(engine)`: Motor Real-ESRGAN, carregamento de tensores, precisão FP16.
* `(gui)`: Interface Tkinter, visualizador comparativo de split, diálogos modais.
* `(models)`: Download, verificação e gestão de checkpoints neurais.
* `(preflight)`: Diagnóstico de hardware, checagem de dependências e drivers.
* `(logging)`: Subsistema de logging rotativo estruturado.
* `(config)` ou `(deps)`: Requisitos (`requirements.txt`), scripts `run.bat` e `.gitignore`.
* `(governance)`: Manuais institucionais, políticas e especificações técnicas.

---

## 3. Atomicidade e Granularidade

1. **Separação por Finalidade:** Nunca agrupe alterações de naturezas distintas no mesmo commit. Commits devem isolar:
   - Código de inferência / engine.
   - Componentes visuais / GUI.
   - Ajustes em dependências e scripts de automação.
   - Arquivos de documentação técnica.
2. **Histórico Limpo:** Mensagens genéricas como "ajustes", "update" ou "fixes" são terminantemente proibidas.

---

## 4. Checklist Pré-Commit

Antes de executar qualquer comando de commit autorizado:
- [ ] O branch de trabalho está correto (ex: `dev`)?
- [ ] O comando `git status` foi executado para inspecionar os arquivos staged?
- [ ] Foram excluídos do staging todos os arquivos de logs (`logs/`), ambientes virtuais (`.venv312/`), modelos `.pth` e saídas temporárias?
- [ ] As mensagens de commit estão em Português Técnico (PT-BR)?
- [ ] A alteração foi validada localmente quanto à sintaxe e ausência de regressões?
