"""Verificação de dependências obrigatórias antes de abrir a GUI.

Executa importações de teste e retorna diagnóstico completo para o
ponto de entrada (``main.py``) decidir se a aplicação pode ser aberta.
"""

from __future__ import annotations

import importlib
import logging
import sys
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger("upvision.preflight")

# Dependências obrigatórias — (nome_importável, nome_amigável, instrução pip)
_REQUIRED_MODULES = [
    ("torch", "PyTorch", "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"),
    ("numpy", "NumPy", "pip install numpy"),
    ("PIL", "Pillow", "pip install pillow"),
    ("cv2", "OpenCV", "pip install opencv-python-headless"),
    ("realesrgan", "Real-ESRGAN", "pip install realesrgan==0.3.0"),
    ("basicsr", "BasicSR", "pip install basicsr"),
]


@dataclass
class PreflightResult:
    """Resultado consolidado da checagem de dependências."""
    missing: List[str] = field(default_factory=list)
    install_instructions: List[str] = field(default_factory=list)
    python_version: str = ""
    python_ok: bool = True
    cuda_available: bool = False
    cuda_device_name: Optional[str] = None
    cuda_vram_total_mb: Optional[float] = None
    warnings: List[str] = field(default_factory=list)

    @property
    def can_run(self) -> bool:
        """True se todas as dependências obrigatórias estão presentes."""
        return len(self.missing) == 0 and self.python_ok


def check_dependencies() -> PreflightResult:
    """Verifica todas as dependências obrigatórias e retorna diagnóstico."""
    result = PreflightResult()

    # --- Versão Python ---
    ver = sys.version_info
    result.python_version = f"{ver.major}.{ver.minor}.{ver.micro}"
    logger.info("Python %s (%s)", result.python_version, sys.executable)

    if ver < (3, 12):
        result.python_ok = False
        result.warnings.append(
            f"Python {result.python_version} não é suportado. Requer Python >= 3.12."
        )
        logger.warning("Python %s abaixo do mínimo 3.12.", result.python_version)
    elif ver >= (3, 14):
        result.python_ok = False
        result.warnings.append(
            f"Python {result.python_version} não é suportado pelo realesrgan 0.3.0. Use Python 3.12 ou 3.13."
        )
        logger.warning("Python %s acima do máximo suportado.", result.python_version)

    # --- Módulos obrigatórios ---
    for module_name, friendly_name, pip_cmd in _REQUIRED_MODULES:
        try:
            importlib.import_module(module_name)
            logger.debug("[OK] %s (%s)", friendly_name, module_name)
        except ImportError:
            result.missing.append(friendly_name)
            result.install_instructions.append(f"  {pip_cmd}")
            logger.error("[AUSENTE] %s (%s)", friendly_name, module_name)

    # --- CUDA / GPU ---
    try:
        import torch
        result.cuda_available = torch.cuda.is_available()
        if result.cuda_available:
            try:
                result.cuda_device_name = torch.cuda.get_device_name(0)
                vram_free, vram_total = torch.cuda.mem_get_info(0)
                result.cuda_vram_total_mb = vram_total / (1024 * 1024)
                logger.info(
                    "GPU: %s | VRAM total: %.0f MB | VRAM livre: %.0f MB",
                    result.cuda_device_name,
                    vram_total / (1024 * 1024),
                    vram_free / (1024 * 1024),
                )
            except Exception as exc:
                result.cuda_device_name = "GPU não identificada"
                logger.warning("Falha ao obter info da GPU: %s", exc)
        else:
            result.warnings.append(
                "CUDA não disponível. O processamento usará CPU (mais lento)."
            )
            logger.info("CUDA não disponível — modo CPU.")
    except ImportError:
        pass  # Já capturado na checagem de módulos acima

    return result


def format_error_message(result: PreflightResult) -> str:
    """Formata mensagem de erro amigável para exibição em messagebox."""
    lines = ["O UpVision não pode iniciar. Dependências ausentes:\n"]
    for name in result.missing:
        lines.append(f"  ❌  {name}")
    lines.append("\nPara instalar, execute no terminal:")
    lines.extend(result.install_instructions)
    if result.warnings:
        lines.append("\nAvisos:")
        for w in result.warnings:
            lines.append(f"  ⚠️  {w}")
    return "\n".join(lines)


def format_warning_message(result: PreflightResult) -> str:
    """Formata mensagem de aviso (dependências OK, mas CUDA ausente, etc.)."""
    return "\n".join(f"⚠️  {w}" for w in result.warnings)
