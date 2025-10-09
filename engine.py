"""Utility classes to drive Real-ESRGAN inference for the desktop GUI.

The goal of this module is to concentrate all heavy lifting around:
- discovering available Real-ESRGAN models on disk;
- loading PyTorch/RealESRGAN components lazily;
- running batch inference while emitting friendly log messages;
- summarising the current runtime environment (torch / CUDA / GPU).

It is designed to be imported by ``main.py`` without triggering any GPU
allocations up-front; models are only loaded when ``process_batch`` is
invoked.
"""

from __future__ import annotations

import dataclasses
import queue
import re
import threading
import time
import warnings
from pathlib import Path
from typing import Iterable, List, Optional

import numpy as np
from PIL import Image

warnings.filterwarnings(
    "ignore",
    message="You are using `torch.load` with `weights_only=False`",
    category=FutureWarning,
)
warnings.filterwarnings(
    "ignore",
    message="The torchvision.transforms.functional_tensor module is deprecated",
    category=UserWarning,
)

try:  # torch is optional until runtime, but GUI feedback needs it.
    import torch
except ImportError as exc:  # pragma: no cover - handled downstream
    torch = None  # type: ignore[assignment]
    _torch_import_error = exc
else:
    _torch_import_error = None

# These imports are delayed because the packages are relatively heavy. They are
# resolved inside ``_LazyModel`` the first time we really need them.
RealESRGANer = None
RRDBNet = None


@dataclasses.dataclass(slots=True)
class ModelInfo:
    """Metadata about a Real-ESRGAN checkpoint available on disk."""

    name: str
    path: Path
    scale: int


@dataclasses.dataclass(slots=True)
class DeviceSummary:
    torch_available: bool
    torch_version: Optional[str]
    torch_cuda_compiled: Optional[str]
    cuda_available: bool
    cuda_device_name: Optional[str]

    def preferred_device(self) -> str:
        if self.cuda_available:
            return "cuda"
        return "cpu"


@dataclasses.dataclass(slots=True)
class BatchResult:
    total: int
    succeeded: int
    failed: int
    duration: float


class UpscaleEngine:
    """High-level front-end for Real-ESRGAN inference."""

    def __init__(self, models_dir: Optional[Path] = None) -> None:
        self.app_dir = Path(__file__).resolve().parent
        self.models_dir = models_dir or self._default_models_dir()
        self._check_models_dir()
        self._model_cache: dict[str, ModelInfo] = {}
        self._lazy_model: Optional[_LazyModel] = None

    # ------------------------------------------------------------------
    # Public helpers

    def list_models(self) -> List[ModelInfo]:
        models: List[ModelInfo] = []
        if not self.models_dir.exists():
            return models
        for item in sorted(self.models_dir.glob("*.pth")):
            scale = _infer_scale(item.name)
            models.append(ModelInfo(name=item.stem, path=item, scale=scale))
        self._model_cache = {model.name: model for model in models}
        return models

    def get_device_summary(self) -> DeviceSummary:
        if torch is None:
            return DeviceSummary(
                torch_available=False,
                torch_version=None,
                torch_cuda_compiled=None,
                cuda_available=False,
                cuda_device_name=None,
            )
        cuda_available = torch.cuda.is_available()
        cuda_name: Optional[str]
        if cuda_available:
            try:
                cuda_name = torch.cuda.get_device_name(0)
            except Exception:  # pragma: no cover - depends on driver state
                cuda_name = "GPU não identificada"
        else:
            cuda_name = None
        return DeviceSummary(
            torch_available=True,
            torch_version=torch.__version__,
            torch_cuda_compiled=getattr(torch.version, "cuda", None),
            cuda_available=cuda_available,
            cuda_device_name=cuda_name,
        )

    # ------------------------------------------------------------------
    # Main entry point used by the GUI

    def process_batch(
        self,
        image_paths: Iterable[Path],
        output_dir: Path,
        model_name: str,
        device: str,
        event_queue: "queue.Queue[tuple[str, object]]",
    ) -> BatchResult:
        start = time.time()
        paths = [Path(p) for p in image_paths]
        output_dir.mkdir(parents=True, exist_ok=True)

        model = self._resolve_model(model_name)
        lazy_model = self._ensure_lazy_model(model, device)

        succeeded = 0
        failed = 0

        total = len(paths)
        for index, source in enumerate(paths, start=1):
            event_queue.put(("log", f"Processando: {source.name}"))
            try:
                dest = lazy_model.enhance_image(source, output_dir)
            except Exception as err:  # pragma: no cover - runtime errors only
                failed += 1
                event_queue.put(("log", f"[ERRO] {source.name}: {err}"))
            else:
                succeeded += 1
                event_queue.put(("log", f"[OK] {source.name} → {dest.name}"))
            finally:
                event_queue.put(("progress", (index, total, source.name)))

        duration = time.time() - start
        event_queue.put(("done", BatchResult(total, succeeded, failed, duration)))
        return BatchResult(total, succeeded, failed, duration)

    # ------------------------------------------------------------------
    # Internal helpers

    def _resolve_model(self, model_name: str) -> ModelInfo:
        if not self._model_cache:
            self.list_models()
        info = self._model_cache.get(model_name)
        if info is None:
            raise FileNotFoundError(f"Modelo '{model_name}' não encontrado em {self.models_dir}")
        if not info.path.exists():
            raise FileNotFoundError(f"Arquivo de modelo ausente: {info.path}")
        return info

    def _ensure_lazy_model(self, model: ModelInfo, device: str) -> "_LazyModel":
        if self._lazy_model is None or not self._lazy_model.matches(model, device):
            self._lazy_model = _LazyModel(model, device)
        return self._lazy_model

    def _check_models_dir(self) -> None:
        if not self.models_dir.exists():
            # We do not raise here to allow the GUI to start. The user can
            # still configure a valid directory afterwards.
            return
        if not self.models_dir.is_dir():
            raise NotADirectoryError(f"Caminho de modelos inválido: {self.models_dir}")

    def _default_models_dir(self) -> Path:
        candidates = [
            self.app_dir / "models_realesrgan",
            self.app_dir.parent / "models_realesrgan",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        # Fallback to first option even que não exista; UI irá alertar
        return candidates[0]


class _LazyModel:
    """Caches the loaded Real-ESRGAN network for reuse across images."""

    def __init__(self, model_info: ModelInfo, device: str) -> None:
        if torch is None:
            raise ModuleNotFoundError(
                "PyTorch não está instalado. Instale torch/torchvision/torchaudio antes de rodar o upscale."
            ) from _torch_import_error
        self.model_info = model_info
        self.device = _normalise_device(device)
        self._upsampler = self._build_upsampler()
        self._lock = threading.Lock()

    def matches(self, model: ModelInfo, device: str) -> bool:
        return self.model_info.name == model.name and self.device == _normalise_device(device)

    def enhance_image(self, image_path: Path, output_dir: Path) -> Path:
        image_path = image_path.resolve()
        if not image_path.exists():
            raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

        with Image.open(image_path) as img:
            rgb = img.convert("RGB")
            bgr = np.array(rgb)[:, :, ::-1]

        with self._lock:
            sr, _ = self._upsampler.enhance(bgr, outscale=self.model_info.scale)

        sr_rgb = Image.fromarray(sr[:, :, ::-1])
        suffix = f"_x{self.model_info.scale}"
        output_path = output_dir / f"{image_path.stem}{suffix}{image_path.suffix}"
        sr_rgb.save(output_path, quality=95 if output_path.suffix.lower() in {".jpg", ".jpeg"} else None)
        return output_path

    # ------------------------------------------------------------------
    # Building blocks

    def _build_upsampler(self):
        global RealESRGANer, RRDBNet
        if RealESRGANer is None or RRDBNet is None:
            RealESRGANer, RRDBNet = _import_realesrgan()
        half_precision = self.device.startswith("cuda")
        rrdb = RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=23,
            num_grow_ch=32,
            scale=self.model_info.scale,
        )
        return RealESRGANer(
            scale=self.model_info.scale,
            model_path=str(self.model_info.path),
            model=rrdb,
            pre_pad=0,
            half=half_precision,
            device=self.device,
        )


# ----------------------------------------------------------------------
# Utility helpers


def _import_realesrgan() -> tuple[object, object]:
    try:
        from realesrgan import RealESRGANer as _RealESRGANer
        from basicsr.archs.rrdbnet_arch import RRDBNet as _RRDBNet
    except Exception as exc:  # pragma: no cover - import errors tested manually
        raise ModuleNotFoundError(
            "Falha ao importar realesrgan/basicsr. Garanta que as dependências foram instaladas e aplique o patch em basicsr, se necessário."
        ) from exc
    return _RealESRGANer, _RRDBNet


def _infer_scale(filename: str) -> int:
    match = re.search(r"x(\d+)", filename.lower())
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass
    return 4  # default known scale for common checkpoints


def _normalise_device(device: str) -> str:
    device = device.strip().lower()
    if device in {"cuda", "gpu"}:
        return "cuda"
    if device in {"cpu"}:
        return "cpu"
    if device in {"auto", "auto"}:
        return "cuda" if torch and torch.cuda.is_available() else "cpu"
    # Accept raw torch device strings (e.g., cuda:1)
    return device
