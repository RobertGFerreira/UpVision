"""
diagnostico_realesrgan.py
Teste rápido do Real-ESRGAN:
 - Verifica CUDA
 - Carrega modelo x2plus
 - Seleciona primeira imagem (plantas_invasoras) em assets ou backup
 - Faz upscale 2x e salva resultado
Execute: python diagnostico_realesrgan.py
"""

import os
import json
import time
import numpy as np
from PIL import Image
import torch

print("Torch:", torch.__version__)
print("Compilado com CUDA:", getattr(torch.version, "cuda", "N/A"))
print("CUDA disponível runtime:", torch.cuda.is_available())
if torch.cuda.is_available():
    try:
        print("GPU:", torch.cuda.get_device_name(0))
    except Exception as e:
        print("Falha ao obter nome da GPU:", e)

try:
    from realesrgan import RealESRGANer
    from basicsr.archs.rrdbnet_arch import RRDBNet
except Exception as e:
    print("Falha import RealESRGAN/BasisSR:", e)
    raise SystemExit(1)

MODEL_PATH = os.path.join("models_realesrgan", "RealESRGAN_x2plus.pth")
assert os.path.isfile(MODEL_PATH), f"Modelo não encontrado: {MODEL_PATH}"

device = "cuda:0" if torch.cuda.is_available() else "cpu"
print("Device escolhido:", device)

model_rrdb = RRDBNet(num_in_ch=3, num_out_ch=3,
                     num_feat=64, num_block=23,
                     num_grow_ch=32, scale=2)

upsampler = RealESRGANer(
    scale=2,
    model_path=MODEL_PATH,
    model=model_rrdb,
    pre_pad=0,
    half=(device.startswith("cuda")),
    device=device
)

json_path = os.path.join("assets", "problemas", "plantas_invasoras_data", "todas_as_plantas_invasoras.json")
if not os.path.isfile(json_path):
    raise SystemExit(f"JSON não encontrado: {json_path}")

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

candidate = None
for rec in data:
    lst = rec.get("downloaded_image_paths")
    if isinstance(lst, list):
        for p in lst:
            if not isinstance(p, str):
                continue
            if os.path.isfile(p):
                candidate = p
                break
            bkp = p.replace("assets/problemas", "assets_backup/problemas")
            if os.path.isfile(bkp):
                candidate = bkp
                break
    if candidate:
        break

if not candidate:
    raise SystemExit("Nenhuma imagem encontrada (verifique downloaded_image_paths).")

print("Imagem selecionada:", candidate)
img = Image.open(candidate).convert("RGB")
print("Dimensão original:", img.size)

bgr = np.array(img)[:, :, ::-1]
t0 = time.time()
sr, _ = upsampler.enhance(bgr, outscale=2)
elapsed = time.time() - t0
print(f"Inferência concluída em {elapsed:.3f}s")

sr_img = Image.fromarray(sr[:, :, ::-1])
out_path = "teste_realesrgan_sr.jpg"
sr_img.save(out_path, quality=90)
print("Resultado salvo em:", out_path, "Dimensão:", sr_img.size)