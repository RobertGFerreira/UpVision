"""Teste rápido de inferência com Real-ESRGAN.

Executa um upscale 2x utilizando o primeiro arquivo de imagem encontrado nos
pastas de `assets` (ou, como fallback, nos JSONs legados em
`assets/problemas/*/todas_as_*.json`). O resultado é salvo ao lado do
script como `teste_realesrgan_sr.jpg`.

Uso:
    python diagnostico_realesrgan.py
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
from PIL import Image

try:
    import torch  # type: ignore
except Exception as exc:  # pragma: no cover - depende do ambiente
    raise SystemExit(f"Torch não disponível: {exc}")

try:
    from realesrgan import RealESRGANer  # type: ignore
    from basicsr.archs.rrdbnet_arch import RRDBNet  # type: ignore
except Exception as exc:
    raise SystemExit(
        "Falha ao importar realesrgan/basicsr. Instale os pacotes e aplique o patch se necessário."
    ) from exc

BASE_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = BASE_DIR / "models_realesrgan"
MODEL_PATH = MODELS_DIR / "RealESRGAN_x2plus.pth"
if not MODEL_PATH.is_file():
    raise SystemExit(f"Modelo não encontrado em {MODEL_PATH}")

ASSETS_DIR = BASE_DIR / "assets"
JSON_GLOBS = [
    "doencas_data/todas_as_doencas.json",
    "plantas_daninhas_data/todas_as_plantas_daninhas.json",
    "plantas_invasoras_data/todas_as_plantas_invasoras.json",
    "pragas_data/todas_as_pragas.json",
    "insumos_data/todos_os_insumos.json",
]


def main() -> None:
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    print("Torch:", torch.__version__)
    print("Compilado com CUDA:", getattr(torch.version, "cuda", "N/A"))
    print("CUDA disponível runtime:", torch.cuda.is_available())
    if torch.cuda.is_available():
        try:
            print("GPU:", torch.cuda.get_device_name(0))
        except Exception as exc:  # pragma: no cover
            print("Falha ao obter nome da GPU:", exc)
    print("Device escolhido:", device)

    model_rrdb = RRDBNet(
        num_in_ch=3,
        num_out_ch=3,
        num_feat=64,
        num_block=23,
        num_grow_ch=32,
        scale=2,
    )

    upsampler = RealESRGANer(
        scale=2,
        model_path=str(MODEL_PATH),
        model=model_rrdb,
        pre_pad=0,
        half=device.startswith("cuda"),
        device=device,
    )

    candidate = _find_candidate_image()
    if candidate is None:
        raise SystemExit("Nenhuma imagem encontrada em 'assets'.")

    print("Imagem selecionada:", candidate)
    with Image.open(candidate) as img:
        rgb = img.convert("RGB")
        print("Dimensão original:", rgb.size)
        bgr = np.array(rgb)[:, :, ::-1]

    t0 = time.time()
    sr, _ = upsampler.enhance(bgr, outscale=2)
    elapsed = time.time() - t0
    print(f"Inferência concluída em {elapsed:.3f}s")

    sr_img = Image.fromarray(sr[:, :, ::-1])
    out_path = candidate.with_name(f"{candidate.stem}_sr{candidate.suffix}")
    sr_img.save(out_path, quality=90)
    print("Resultado salvo em:", out_path, "Dimensão:", sr_img.size)


def _find_candidate_image() -> Optional[Path]:
    image = _first_image_in_directory(ASSETS_DIR)
    if image:
        return image

    # Fallback legado: procurar via manifests JSON
    problemas_dir = ASSETS_DIR / "problemas"
    for glob in JSON_GLOBS:
        json_path = problemas_dir / glob
        if not json_path.is_file():
            continue
        try:
            import json

            with open(json_path, "r", encoding="utf-8") as handle:
                records = json.load(handle)
        except Exception:
            continue
        candidate = _first_available_image(records)
        if candidate:
            return candidate
    return None


def _first_image_in_directory(directory: Path) -> Optional[Path]:
    if not directory.exists():
        return None
    exts = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}
    for path in directory.rglob("*"):
        if path.is_file() and path.suffix.lower() in exts:
            return path
    return None


def _first_available_image(records: Iterable[dict]) -> Path | None:
    for record in records:
        paths = record.get("downloaded_image_paths")
        if not isinstance(paths, list):
            continue
        for raw in paths:
            if not isinstance(raw, str):
                continue
            primary = Path(raw)
            if primary.is_file():
                return primary
            backup = Path(str(raw).replace("assets/problemas", "assets_backup/problemas"))
            if backup.is_file():
                return backup
    return None


if __name__ == "__main__":
    main()
