# 🛡️ SECURITY.md - Diretrizes de Segurança Interna (UpVision)

Este documento descreve as políticas de segurança corporativa, tratamento de dados locais e procedimentos para reporte e mitigação de vulnerabilidades no ecossistema **UpVision**.

---

## 1. Processo de Reporte de Vulnerabilidades

Qualquer desenvolvedor interno, auditor ou colaborador que identificar vulnerabilidades técnicas ou riscos de integridade de dados deve manter o **mais estrito sigilo**, sendo proibida qualquer divulgação pública.

### Canal Interno de Comunicação
* As falhas devem ser comunicadas diretamente ao proprietário do projeto:
  * **E-mail de Segurança:** `contato.robferreira@gmail.com`
* Informações obrigatórias no reporte:
  * Descrição clara da vulnerabilidade identificada.
  * Prova de Conceito (PoC) ou passos exatos para reprodução.
  * Análise do impacto na integridade de arquivos locais ou consumo de recursos de GPU/memória.

---

## 2. Princípios de Segurança e Isolamento

### A. Privacidade Zero-Trust e Zero-Data Leakage
O UpVision é expressamente construído para operar de maneira isolada (air-gapped ou offline):
* **Nenhum Envio de Mídia Externa:** Nenhum frame, imagem original ou imagem restaurada pode ser transmitido via requisições HTTP/WebSockets para terceiros.
* **Telemetria Opcional e Controlada:** Não são mantidos scripts de telemetria invasiva ou analytics em nuvem sem o consentimento formal do usuário.

### B. Proteção contra Carregamento de Pesos Maliciosos (Pickle Insecurity)
* Checkpoints PyTorch (`.pth`) utilizam serialização baseada em pickle, que pode apresentar riscos se originada de fontes não verificadas.
* O UpVision restringe downloads de modelos exclusivamente a endpoints oficiais catalogados no `MODEL_REGISTRY`.
* Todo arquivo baixado passa por verificação de tamanho mínimo (> 10 MB) para prevenir injeções de arquivos truncados ou corrompidos.

### C. Proteção contra Path Traversal e Injeção de Arquivos
* A manipulação de nomes de arquivos para exportação (`_sr.jpg`, `_x2.png`) utiliza métodos seguros da biblioteca `pathlib.Path` para impedir escapes de diretórios via `../`.

### D. Gestão de Logs e Dados Transitórios
* Os arquivos gravados em `logs/upvision.log` contêm apenas metadados técnicos de execução (dimensões de imagem, taxa de upscale, uso de memória VRAM e tempos de processamento).
* Caminhos de arquivos de usuários não devem expor segredos de sistema ou credenciais de usuário.
