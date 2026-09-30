<!-- HEADER E BADGES -->
<div align="center">

  # 👁️ UpVision
  
  <h3>Inteligência Visual Local e de Alta Performance para Aplicações Críticas</h3>

  <p>
    Framework de Visão Computacional otimizado para inferência em borda (Edge), <br>
    garantindo <b>Privacidade Zero-Trust</b> e latência mínima.
  </p>

  <!-- Badges de Tecnologias e Status -->
  <p>
    <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
    <img src="https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV" />
    <img src="https://img.shields.io/badge/TensorFlow-Lite-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white" alt="TensorFlow" />
    <img src="https://img.shields.io/badge/Code_Style-PEP8-blueviolet?style=for-the-badge" alt="Code Style PEP8" />
    <img src="https://img.shields.io/badge/Status-Active_Development-2EA44F?style=for-the-badge" alt="Status" />
    <img src="https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge" alt="Proprietary License" />
  </p>
</div>

---

<!-- PREVIEW (VITRINE) -->
## 📸 Demonstração

> *Abaixo, uma demonstração do UpVision processando fluxos de vídeo em tempo real, identificando padrões e anomalias com milissegundos de latência.*

<div align="center">
  <!-- LOCAL RESERVADO PARA DEMO - SUBSTITUA O ARQUIVO EM assets/demo.gif -->
  <img src="assets/demo.gif" alt="Demo do UpVision em ação: detecção de objetos e análise de fluxo em tempo real" width="100%" style="border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <br>
  <sub><i>Interface de processamento mostrando a detecção de objetos e telemetria em tempo real.</i></sub>
</div>

---

## 🎯 O Problema vs. A Solução

### 🔴 O Desafio
A implementação de sistemas de Visão Computacional robustos frequentemente esbarra no "Trilema da IA": **Latência**, **Privacidade** e **Custo**. Soluções baseadas em APIs de nuvem sofrem com delay de rede e expõem dados sensíveis de vídeo a terceiros, enquanto implementações locais muitas vezes carecem de otimização, consumindo recursos excessivos de hardware.

### 🟢 A Abordagem UpVision
O **UpVision** resolve isso desacoplando a inferência da dependência de nuvem. Utilizamos modelos quantizados e pipelines de pré-processamento otimizados com `OpenCV` e `NumPy` para rodar localmente.
*   **Zero Data Leakage:** Nenhum frame sai da máquina local.
*   **Inferência Otimizada:** Pipeline assíncrono para maximizar o FPS.
*   **Modularidade:** Arquitetura plug-and-play para diferentes modelos (YOLO, SSD, Custom).

---

## ✨ Funcionalidades Principais

*   🚀 **Processamento Real-Time:** Pipeline de captura e inferência multithreaded para minimizar gargalos de I/O.
*   🧠 **Suporte Multi-Modelo:** Abstração para fácil integração de modelos `.tflite`, `.onnx` ou `.pt`.
*   🛡️ **Privacidade por Design:** Todo o processamento ocorre *on-premise* ou *on-device*.
*   📊 **Analytics Integrado:** Geração automática de logs e estatísticas de detecção (contagem, tempos de permanência).
*   🔧 **Configuração Declarativa:** Ajuste de parâmetros de sensibilidade e ROI (Region of Interest) via arquivos JSON/YAML.

---

## 🛠️ Stack Tecnológica

A arquitetura do projeto foi desenhada visando **manutenibilidade** e **performance**.

| Tecnologia | Função no Projeto |
| :--- | :--- |
| **Python 3.10+** | Linguagem core, escolhida pela vasta biblioteca de Data Science. |
| **OpenCV** | Manipulação de matrizes de imagem e pré-processamento de alta velocidade. |
| **TensorFlow / PyTorch** | Backends para execução dos modelos de Deep Learning. |
| **NumPy** | Operações vetoriais otimizadas para cálculos geométricos. |
| **Docker** | Padronização do ambiente de desenvolvimento e deploy reprodutível. |
| **PyTest** | Garantia de qualidade através de testes unitários automatizados. |

---

## 🚀 Instalação e Uso

### Pré-requisitos
*   **Python 3.12** (versões 3.13+ não são suportadas pelo `realesrgan 0.3.0`)
*   **Git**
*   **Driver NVIDIA** (recomendado para aceleração GPU via CUDA)

### Quick Start (Windows)

```bash
# 1. Clone o repositório
git clone https://github.com/RobertGFerreira/UpVision.git
cd UpVision

# 2. Execute o script de setup automático
#    - Cria venv com Python 3.12
#    - Detecta GPU e instala PyTorch (CUDA 12.1 ou CPU)
#    - Aplica patches necessários
#    - Baixa modelos Real-ESRGAN
run.bat

# 3. Ative o venv e execute
.venv312\Scripts\activate
python main.py
```

### Setup Manual

```bash
# Criar venv com Python 3.12
py -3.12 -m venv .venv312
.venv312\Scripts\activate

# Instalar PyTorch com GPU (CUDA 12.1)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Instalar dependências
pip install -r requirements.txt

# Aplicar patch de compatibilidade
python tools\patch_basicsr_torchvision.py

# Baixar modelos
python tools\download_models.py

# Executar
python main.py
```

> **Nota:** Na primeira execução sem modelos, o aplicativo abrirá automaticamente um diálogo para download dos checkpoints necessários.

### 🎮 GPU (Aceleração CUDA)

O UpVision detecta automaticamente GPUs NVIDIA com CUDA e as utiliza por padrão.

*   **Verificar GPU:** Execute `python tools\env_check.py` para ver se CUDA está disponível.
*   **Sem GPU:** O processamento funciona em CPU, porém significativamente mais lento.
*   **Driver mínimo:** NVIDIA Driver 525.60+ para CUDA 12.1. Baixe em [nvidia.com/drivers](https://www.nvidia.com/download/index.aspx).

---

## 🔒 Padrões de Código e Segurança

Este projeto segue rigorosos padrões de engenharia de software para garantir escalabilidade e colaboração segura:

*   **Conventional Commits:** Todo o histórico de git segue o padrão convencional (ex: `feat: add new detector`, `fix: memory leak in stream`).
*   **Arquitetura Limpa:** O código é separado em camadas de responsabilidade (Core, Adapters, Utils), facilitando testes e refatoração.
*   **Type Hinting:** Uso extensivo de tipagem estática do Python para clareza e redução de bugs em tempo de execução.
*   **Segurança (.env):** Credenciais e chaves de API (se necessárias futuramente) são gerenciadas exclusivamente via variáveis de ambiente, nunca hardcoded. O arquivo `.env.example` serve como template seguro.
*   **Linter & Formatter:** Código padronizado com `Black` e `Isort`.

---

## 📚 Documentação e Governança

O projeto conta com um conjunto completo de especificações técnicas e diretrizes corporativas:

* **[Arquitetura](ARCHITECTURE.md)** — Visão executiva da engenharia, threads e pipeline de inferência.
* **[Manual de Agentes](AGENTS.md)** — Governança de atuação de IA, regras de complexidade e checklist.
* **[Constituição Global](SYSTEM.md)** — Regras de engenharia, isolamento e formato obrigatório de resposta.
* **[Guia de Manutenção Interna](CONTRIBUTING.md)** — Normas de commit convencional, testes e qualidade.
* **[Planejamento Estratégico](ROADMAP.md)** — Fases de desenvolvimento, backlog e evolução tecnológica.
* **[Segurança e Privacidade](SECURITY.md)** — Reporte interno de vulnerabilidades e proteção de dados.
* **[Documentação Técnica Aprofundada](docs/)** — Manuais de arquitetura, catálogo de modelos e guias de execução.

---

## 🔒 Licença e Confidencialidade

Este software é um produto comercial **fechado, privado e proprietário** de **Robert Ferreira**. Todos os direitos reservados. Consulte [`LICENSE.md`](LICENSE.md) para termos contratuais e restrições de uso.

---

<!-- AUTOR (DADOS FIXOS) -->
<div align="center">
  <img src="https://github.com/RobertGFerreira.png" width="120px;" alt="Foto do Robert Ferreira" style="border-radius: 50%; border: 2px solid #3776AB;">
  <br />
  <sub><b>Robert Ferreira</b></sub>
  <br />
  <i>Developer | Problem Solver | Open Source Enthusiast</i>
  <br /><br />
  <a href="https://www.linkedin.com/in/robert-guilherme-ferreira/" target="_blank">
    <img src="https://img.shields.io/badge/-LinkedIn-0077B5?style=for-the-badge&logo=Linkedin&logoColor=white" alt="LinkedIn">
  </a>
  <a href="mailto:contato.robferreira@gmail.com" target="_blank">
    <img src="https://img.shields.io/badge/-Gmail-D14836?style=for-the-badge&logo=Gmail&logoColor=white" alt="Gmail">
  </a>
  <a href="https://github.com/RobertGFerreira" target="_blank">
    <img src="https://img.shields.io/badge/-Portfolio-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
  </a>
</div>
