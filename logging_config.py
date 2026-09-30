"""Configuração centralizada de logging para o UpVision.

Fornece log simultâneo no console (StreamHandler) e em arquivo rotativo
(RotatingFileHandler), seguindo o mesmo padrão adotado nos demais projetos
do ecossistema Rural.

Uso típico::

    from logging_config import setup_logging, get_logger

    setup_logging()
    logger = get_logger("upvision.engine")
    logger.info("Mensagem de exemplo")
"""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

# Diretório de logs — criado automaticamente ao lado do executável
_LOG_DIR = Path(__file__).resolve().parent / "logs"

_CONSOLE_FMT = "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"

_configured = False


def setup_logging(
    level: int = logging.DEBUG,
    log_file: str = "upvision.log",
    max_bytes: int = 5 * 1024 * 1024,  # 5 MB
    backup_count: int = 3,
) -> None:
    """Configura os handlers de logging.  Pode ser chamado mais de uma vez
    sem efeito colateral (idempotente após a primeira chamada)."""

    global _configured
    if _configured:
        return
    _configured = True

    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(_CONSOLE_FMT, datefmt=_DATE_FMT)

    # --- Handler de console ---------------------------------------------------
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # --- Handler de arquivo rotativo -----------------------------------------
    file_handler = logging.handlers.RotatingFileHandler(
        _LOG_DIR / log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # --- Logger raiz ----------------------------------------------------------
    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    # Silenciar loggers muito verbosos de bibliotecas externas
    for noisy in ("PIL", "urllib3", "requests", "torch", "basicsr", "facexlib"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger("upvision").info(
        "Logging inicializado. Arquivo: %s", _LOG_DIR / log_file
    )


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger nomeado (a configuração root já propagará)."""
    return logging.getLogger(name)
