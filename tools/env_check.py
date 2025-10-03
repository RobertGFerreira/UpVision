"""Verificações rápidas do ambiente PyTorch/Real-ESRGAN.

Este script é uma versão independente do verificador usado no projeto ELT
original. Ele imprime informações sobre a instalação de torch, torchvision,
torchaudio, bem como a disponibilidade de CUDA e a presença dos pacotes
``realesrgan`` e ``basicsr``.

Uso:
    python env_check.py
"""

from __future__ import annotations

import sys


def main() -> None:
    print("=== ENV CHECK ===")
    print("Python exe:", sys.executable)
    print("Python versão:", sys.version.replace("\n", " "))

    try:
        import torch  # type: ignore

        print("Torch:", torch.__version__)
        print("Versão CUDA (compilada):", getattr(torch.version, "cuda", "N/A"))
        cuda_available = torch.cuda.is_available()
        print("CUDA disponível em runtime?:", cuda_available)
        if cuda_available:
            try:
                print("GPU:", torch.cuda.get_device_name(0))
            except Exception as exc:  # pragma: no cover - depende da GPU
                print("Não foi possível obter nome da GPU:", exc)
    except Exception as exc:
        print("Falha import torch:", exc)
        return

    for module in ("torchvision", "torchaudio", "realesrgan", "basicsr"):
        _check_module(module)

    print("=== FIM ENV CHECK ===")


def _check_module(name: str) -> None:
    try:
        module = __import__(name)
    except ImportError as exc:
        print(f"{name} NÃO encontrado / falhou: {exc}")
        return
    version = getattr(module, "__version__", "(versão não encontrada)")
    print(f"{name} OK - versão {version}")


if __name__ == "__main__":
    main()
