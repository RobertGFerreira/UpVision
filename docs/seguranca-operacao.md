# Segurança e Operação em Ambiente Crítico — UpVision

Este documento formaliza as diretrizes de segurança da informação, operação local e integridade de dados do ecossistema **UpVision**.

---

## 1. Princípio de Isolamento Total (Air-Gap & Zero Data Leakage)

O UpVision é projetado especificamente para operações onde a confidencialidade de imagens e dados visuais é mandatória:

- **Processamento 100% On-Premises:** Nenhum byte de imagem, miniatura de pré-visualização ou metadado EXIF é transmitido pela internet.
- **Isolamento de Rede:** Toda a inferência de super-resolução funciona sem necessidade de conectividade ativa de rede uma vez que os modelos estejam localizados em `models_realesrgan/`.
- **Prevenção de Telemetria Oculta:** O código-fonte não contém bibliotecas de telemetria externa, tracking de uso ou captura de comportamento do operador.

---

## 2. Integridade dos Checkpoints e Prevenção contra Deserialização Insegura

A biblioteca PyTorch armazena modelos `.pth` utilizando internamente rotinas de serialização `pickle`, as quais podem executar código arbitrário caso originadas de fontes hostis:

1. **Repositório Confiável Restrito:** O download automatizado de pesos restringe-se às URLs oficiais homologadas no `MODEL_REGISTRY` em [`tools/download_models.py`](../tools/download_models.py).
2. **Checagem de Tamanho Mínimo:** Downloads que resultem em arquivos menores que 10 MB são sumariamente descartados para evitar a substituição de checkpoints por scripts corrompidos ou payloads falsos.
3. **Download Atômico:** A escrita é efetuada em extensão temporária (`.part`) com renomeação transacional no sistema de arquivos.

---

## 3. Manipulação Segura de Arquivos e Sanitização de Caminhos

- **Prevenção de Path Traversal:** A geração de nomes de saída para imagens processadas utiliza exclusivamente `pathlib.Path` e manipulação de sufixos canônicos (`.with_name(...)`), impedindo sequências de escape de diretório como `../../`.
- **Substituição Controlada:** Arquivos de imagem já existentes são renomeados ou incrementados sem destruição acidental de arquivos de sistema.

---

## 4. Governança de Logs e Dados Temporários

- **Ausência de Payloads Visuais nos Logs:** O arquivo `logs/upvision.log` armazena unicamente dimensões numéricas, tempos de execução e mensagens diagnósticas de hardware. Nenhum dado binário de imagem é despejado nos arquivos de log.
- **Proteção do Histórico Git:** O `.gitignore` bloqueia logs (`logs/`), saídas de testes (`assets/*_sr.*`), ambientes virtuais e modelos binários pesados, impedindo a exposição involuntária de dados no repositório.
