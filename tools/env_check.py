"""Verificação rápida do ambiente UpVision.

Verifica Python, torch, CUDA, GPU, VRAM, modelos disponíveis e status do patch.

Uso:
    python tools/env_check.py
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = BASE_DIR / "models_realesrgan"


def main() -> None:
    print("=" * 60)
    print("  UpVision — Verificação de Ambiente")
    print("=" * 60)

    # --- Python ---
    ver = sys.version_info
    ver_str = f"{ver.major}.{ver.minor}.{ver.micro}"
    print(f"\n[Python]")
    print(f"  Versão:    {ver_str}")
    print(f"  Caminho:   {sys.executable}")
    if ver < (3, 12):
        print(f"  ⚠️  AVISO: Python {ver_str} < 3.12. Recomendado Python 3.12.")
    elif ver >= (3, 14):
        print(f"  ⚠️  AVISO: Python {ver_str} >= 3.14. realesrgan pode não funcionar.")
    else:
        print(f"  ✅ Versão compatível.")

    # --- Torch ---
    print(f"\n[PyTorch]")
    try:
        import torch
        print(f"  Versão:         {torch.__version__}")
        print(f"  CUDA compilado: {getattr(torch.version, 'cuda', 'N/A')}")
        print(f"  CUDA runtime:   {'Sim' if torch.cuda.is_available() else 'Não'}")
        if torch.cuda.is_available():
            try:
                gpu_name = torch.cuda.get_device_name(0)
                vram_free, vram_total = torch.cuda.mem_get_info(0)
                print(f"  GPU:            {gpu_name}")
                print(f"  VRAM total:     {vram_total / (1024 * 1024):.0f} MB")
                print(f"  VRAM livre:     {vram_free / (1024 * 1024):.0f} MB")
                print(f"  ✅ GPU detectada e CUDA disponível.")
            except Exception as exc:
                print(f"  ⚠️  Falha ao obter info da GPU: {exc}")
        else:
            print(f"  ⚠️  CUDA não disponível. Usando CPU (mais lento).")
    except ImportError:
        print(f"  ❌ PyTorch NÃO instalado.")

    # --- Dependências ---
    print(f"\n[Dependências]")
    deps = [
        ("realesrgan", "Real-ESRGAN"),
        ("basicsr", "BasicSR"),
        ("facexlib", "FaceXLib"),
        ("PIL", "Pillow"),
        ("numpy", "NumPy"),
        ("cv2", "OpenCV"),
        ("requests", "Requests"),
    ]
    for module_name, friendly_name in deps:
        try:
            mod = importlib.import_module(module_name)
            version = getattr(mod, "__version__", getattr(mod, "VERSION", "?"))
            print(f"  ✅ {friendly_name:12s}  v{version}")
        except ImportError:
            print(f"  ❌ {friendly_name:12s}  NÃO instalado")

    # --- Patch basicsr ---
    print(f"\n[Patch BasicSR]")
    try:
        spec = importlib.util.find_spec("basicsr")
        if spec and spec.origin:
            basicsr_dir = os.path.dirname(spec.origin)
            degradations = os.path.join(basicsr_dir, "data", "degradations.py")
            if os.path.isfile(degradations):
                with open(degradations, "r", encoding="utf-8") as f:
                    content = f.read()
                if "try:" in content and "functional_tensor" in content:
                    print(f"  ✅ Patch aplicado (try/except em degradations.py)")
                elif "from torchvision.transforms.functional_tensor" in content:
                    print(f"  ⚠️  Patch NÃO aplicado. Execute: python tools/patch_basicsr_torchvision.py")
                else:
                    print(f"  ✅ Código já compatível (sem import legado)")
            else:
                print(f"  ⚠️  degradations.py não encontrado")
        else:
            print(f"  ⚠️  basicsr não encontrado")
    except Exception as exc:
        print(f"  ⚠️  Erro ao verificar patch: {exc}")

    # --- Modelos ---
    print(f"\n[Modelos]")
    print(f"  Diretório: {MODELS_DIR}")
    if not MODELS_DIR.exists():
        print(f"  ❌ Diretório de modelos não existe.")
    else:
        models = list(MODELS_DIR.glob("*.pth"))
        if models:
            for m in models:
                size_mb = m.stat().st_size / (1024 * 1024)
                status = "✅" if size_mb > 10 else "⚠️  (suspeito)"
                print(f"  {status} {m.name:35s}  ({size_mb:.1f} MB)")
        else:
            print(f"  ❌ Nenhum modelo .pth encontrado.")
            print(f"     Execute: python tools/download_models.py")

    print(f"\n{'=' * 60}")
    print(f"  Verificação concluída.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
