"""Utilitário para baixar checkpoints do Real-ESRGAN usados pelo UpVision.

Uso básico:
    python tools/download_models.py

Isso fará o download dos modelos padrão (RealESRGAN_x2plus.pth e RealESRGAN_x4plus.pth)
para a pasta `models_realesrgan/`. Utilize --help para ver todas as opções.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, Iterable

import requests

# Lista de modelos suportados e suas respectivas URLs oficiais.
MODEL_REGISTRY: Dict[str, str] = {
    "RealESRGAN_x2plus.pth": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.0/RealESRGAN_x2plus.pth",
    "RealESRGAN_x4plus.pth": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.0/RealESRGAN_x4plus.pth",
}

DEFAULT_MODELS: Iterable[str] = tuple(MODEL_REGISTRY.keys())


def download_file(url: str, destination: Path, chunk_size: int = 8192) -> None:
    """Baixa um arquivo em modo streaming exibindo o progresso aproximado."""
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    total_bytes = int(response.headers.get("Content-Length", 0))
    downloaded = 0

    with destination.open("wb") as file_handle:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if not chunk:
                continue
            file_handle.write(chunk)
            downloaded += len(chunk)

            if total_bytes:
                percent = downloaded / total_bytes * 100
                sys.stdout.write(f"\r- {destination.name}: {percent:6.2f}% ({downloaded / 1_048_576:.2f} MiB)")
            else:
                sys.stdout.write(f"\r- {destination.name}: {downloaded / 1_048_576:.2f} MiB")
            sys.stdout.flush()

    sys.stdout.write("\n")


def ensure_models(models: Iterable[str], dest_dir: Path) -> None:
    """Baixa os modelos solicitados, se ainda não existirem."""
    dest_dir.mkdir(parents=True, exist_ok=True)

    for model_name in models:
        if model_name not in MODEL_REGISTRY:
            print(f"[aviso] Modelo desconhecido: {model_name}. Pulei")
            continue

        target_path = dest_dir / model_name
        if target_path.exists():
            print(f"[ok] {model_name} já existe — ignorando download")
            continue

        print(f"[baixando] {model_name}")
        download_file(MODEL_REGISTRY[model_name], target_path)

    print("\nConcluído. Modelos disponíveis em:")
    print(f"  {dest_dir.resolve()}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa checkpoints Real-ESRGAN necessários para o UpVision.",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=Path("models_realesrgan"),
        help="Diretório de destino dos modelos (default: models_realesrgan/).",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=DEFAULT_MODELS,
        help=(
            "Lista de modelos a baixar. Use nomes como RealESRGAN_x2plus.pth. "
            "Por padrão baixa todos os modelos suportados."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_models(args.models, args.dest)


if __name__ == "__main__":
    main()
