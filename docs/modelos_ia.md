# Catálogo e Arquitetura de Modelos de IA — UpVision

Este documento descreve a arquitetura das redes neurais de Super-Resolução integradas ao **UpVision**, seus parâmetros técnicos, estratégias de carregamento e governança de pesos.

---

## 1. Visão Geral da Arquitetura Real-ESRGAN

O motor de super-resolução do UpVision fundamenta-se na família de modelos **Real-ESRGAN** (Enhanced Super-Resolution Generative Adversarial Networks voltado para degradações realistas do mundo real).

Diferente de modelos tradicionais que assumem degradações sintéticas perfeitas (como bicúbico puro), o Real-ESRGAN é treinado com esquemas de degradação de segunda ordem (*higher-order degradation modeling*), permitindo restaurar imagens com ruído de sensor, compressão JPEG agressiva, blur óptico e artefatos de redimensionamento.

```text
[Imagem de Entrada (Baixa Resolução)]
                 │
                 ▼
       ┌──────────────────┐
       │   Convolução     │
       │    Inicial       │
       └─────────┬────────┘
                 │
                 ▼
       ┌──────────────────┐
       │ RRDB Trunk (23x) │  <-- Residual-in-Residual Dense Blocks
       └─────────┬────────┘
                 │
                 ▼
       ┌──────────────────┐
       │ Upsampler Module │  <-- Módulo de Subpixel Convolution / PixelShuffle
       └─────────┬────────┘
                 │
                 ▼
       ┌──────────────────┐
       │ Reconstrução e   │
       │    Refinamento   │
       └─────────┬────────┘
                 │
                 ▼
[Imagem de Alta Resolução / Super-Resolvida]
```

---

## 2. Modelos Homologados no Catálogo (`MODEL_REGISTRY`)

O registro oficial gerenciado em [`tools/download_models.py`](../tools/download_models.py) e no modal [`model_manager.py`](../model_manager.py) homologa os seguintes checkpoints canônicos:

| Modelo | Fator de Escala | Arquitetura | Blocos | Dimensão | Tamanho (.pth) | Caso de Uso Recomendado |
|---|---|---|---|---|---|---|
| **`RealESRGAN_x2plus.pth`** | 2x | `RRDBNet` | 23 | 64 canais | ~64 MB | Imagens de resolução moderada; preservação ágil com menor custo de memória VRAM. |
| **`RealESRGAN_x4plus.pth`** | 4x | `RRDBNet` | 23 | 64 canais | ~64 MB | Restauração profunda de detalhes finos, texturas e faces em imagens de baixa qualidade. |

### Hiperparâmetros Construtivos da Rede (`RRDBNet`)
* `num_in_ch`: 3 (RGB)
* `num_out_ch`: 3 (RGB)
* `num_feat`: 64 canais intermediários
* `num_block`: 23 blocos densos residuais interconectados
* `num_grow_ch`: 32 canais de crescimento interno

---

## 3. Estratégia de Precisão Numérica e Memória

### 3.1. Inferência com Precisão Mista FP16 (`half=True`)
* Em dispositivos NVIDIA com suporte a CUDA e núcleos Tensor, os pesos e tensores de entrada são convertidos para ponto flutuante de 16 bits (`torch.half`).
* **Benefícios:**
  * Redução de ~50% no uso de VRAM (permitindo upscaling de imagens maiores sem disparar `CUDA out of memory`).
  * Ganho de velocidade de processamento de até 2x dependendo da arquitetura da GPU.

### 3.2. Fallback de Precisão Completa FP32 em CPU
* Ao executar em processadores convencionais (sem suporte a aceleração half em hardware), o sistema utiliza automaticamente precisão FP32 integral (`half=False`), preservando estabilidade numérica e prevenindo valores `NaN`.

---

## 4. Governança de Download e Integridade de Pesos

1. **Validação de Tamanho Mínimo:** 
   O utilitário de download rejeita arquivos com tamanho inferior a 10 MB (`MIN_MODEL_SIZE_BYTES = 10 * 1024 * 1024`), protegendo a engine contra carregamento de downloads interrompidos ou páginas HTML de erro 404 salvas como `.pth`.
2. **Download Atômico via Arquivo Temporário (`.part`):**
   Os dados são gravados inicialmente em `<modelo>.pth.part` e renomeados apenas após o encerramento bem-sucedido do streaming.
3. **Isolamento no Git:**
   A pasta `models_realesrgan/` armazena exclusivamente os binários pesados, os quais são terminantemente ignorados pelo `.gitignore`.

---

## 5. Modelos Futuros Mapeados

* **`SRVGGNetCompact` (`realesr-general-x4v3`):** Arquitetura ultraleve com menor contagem de parâmetros, projetada para inferência em tempo real e equipamentos com hardware restrito.
* **Modelos Especializados para Documentos / Textos:** Checkpoints otimizados para OCR e preservação de caracteres tipográficos.
