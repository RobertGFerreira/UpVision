"""Utilitário para baixar checkpoints do Real-ESRGAN usados pelo UpVision.

Uso básico:
    python tools/download_models.py

Isso fará o download dos modelos padrão (RealESRGAN_x2plus.pth e RealESRGAN_x4plus.pth)
para a pasta `models_realesrgan/`. Utilize --help para ver todas as opções.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Iterable

import requests

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("upvision.download")

# Lista de modelos suportados e suas respectivas URLs oficiais.
# Ambos usam arquitetura RRDBNet (num_block=23) — compatível com engine._build_upsampler.
MODEL_REGISTRY: Dict[str, str] = {
    "RealESRGAN_x2plus.pth": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth",
    "RealESRGAN_x4plus.pth": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
}

# Tamanho mínimo esperado (em bytes) para considerar o modelo válido.
# Ambos os modelos RRDBNet x2/x4 têm ~64 MB.
MIN_MODEL_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

DEFAULT_MODELS: Iterable[str] = tuple(MODEL_REGISTRY.keys())


def download_file(url: str, destination: Path, chunk_size: int = 65_536) -> None:
    """Baixa um arquivo em modo streaming exibindo o progresso aproximado."""
    logger.info("Iniciando download: %s → %s", url, destination.name)
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()

    total_bytes = int(response.headers.get("Content-Length", 0))
    downloaded = 0
    last_logged_mb = 0

    temp_path = destination.with_suffix(destination.suffix + ".part")

    try:
        with temp_path.open("wb") as file_handle:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if not chunk:
                    continue
                file_handle.write(chunk)
                downloaded += len(chunk)

                # Log a cada 10 MB de progresso
                current_mb = downloaded // (10 * 1024 * 1024)
                if current_mb > last_logged_mb:
                    last_logged_mb = current_mb
                    if total_bytes:
                        pct = downloaded / total_bytes * 100
                        logger.info(
                            "  %s: %.1f%% (%.1f / %.1f MB)",
                            destination.name, pct,
                            downloaded / 1_048_576, total_bytes / 1_048_576,
                        )
                    else:
                        logger.info(
                            "  %s: %.1f MB baixados",
                            destination.name, downloaded / 1_048_576,
                        )

                if total_bytes:
                    percent = downloaded / total_bytes * 100
                    sys.stdout.write(
                        f"\r- {destination.name}: {percent:6.2f}% ({downloaded / 1_048_576:.2f} MiB)"
                    )
                else:
                    sys.stdout.write(
                        f"\r- {destination.name}: {downloaded / 1_048_576:.2f} MiB"
                    )
                sys.stdout.flush()

        sys.stdout.write("\n")

        # Mover para destino final
        if destination.exists():
            destination.unlink()
        temp_path.rename(destination)

    except Exception:
        temp_path.unlink(missing_ok=True)
        raise

    logger.info(
        "Download concluído: %s (%.2f MB)",
        destination.name, downloaded / 1_048_576,
    )


def validate_model(path: Path) -> bool:
    """Verifica se o arquivo do modelo existe e tem tamanho mínimo aceitável."""
    if not path.exists():
        return False
    size = path.stat().st_size
    if size < MIN_MODEL_SIZE_BYTES:
        logger.warning(
            "Modelo %s suspeito: %.2f MB (mínimo: %.0f MB). Pode estar corrompido.",
            path.name, size / 1_048_576, MIN_MODEL_SIZE_BYTES / 1_048_576,
        )
        return False
    return True


def ensure_models(models: Iterable[str], dest_dir: Path) -> None:
    """Baixa os modelos solicitados, se ainda não existirem."""
    dest_dir.mkdir(parents=True, exist_ok=True)

    for model_name in models:
        if model_name not in MODEL_REGISTRY:
            logger.warning("Modelo desconhecido: %s. Ignorado.", model_name)
            print(f"[aviso] Modelo desconhecido: {model_name}. Pulei")
            continue

        target_path = dest_dir / model_name
        if validate_model(target_path):
            logger.info("[ok] %s já existe — ignorando download", model_name)
            print(f"[ok] {model_name} já existe — ignorando download")
            continue

        # Se existe mas é inválido, remover
        if target_path.exists():
            logger.warning("Removendo modelo inválido/corrompido: %s", model_name)
            target_path.unlink()

        logger.info("[baixando] %s", model_name)
        print(f"[baixando] {model_name}")
        download_file(MODEL_REGISTRY[model_name], target_path)

        # Validação pós-download
        if not validate_model(target_path):
            logger.error(
                "Modelo %s falhou na validação pós-download. Arquivo possivelmente corrompido.",
                model_name,
            )
            print(f"[ERRO] {model_name} falhou na validação. Tente novamente.")
        else:
            logger.info("[ok] %s validado com sucesso.", model_name)

    print("\nConcluído. Modelos disponíveis em:")
    print(f"  {dest_dir.resolve()}")
    logger.info("Modelos disponíveis em: %s", dest_dir.resolve())


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
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
    )
    args = parse_args()
    ensure_models(args.models, args.dest)


if __name__ == "__main__":
    main()
