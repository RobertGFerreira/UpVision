"""Diálogo Tkinter para gerenciamento de modelos Real-ESRGAN.

Permite visualizar modelos disponíveis, seus status de download, e
baixar modelos ausentes com barra de progresso em tempo real.

Uso típico (chamado pelo ``main.py``)::

    from model_manager import ModelManagerDialog

    dialog = ModelManagerDialog(root, models_dir, on_close_callback)
    root.wait_window(dialog)
"""

from __future__ import annotations

import logging
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Callable, Dict, Optional

import requests

logger = logging.getLogger("upvision.model_manager")

# Registro de modelos — nome do arquivo → (URL, tamanho mínimo esperado em MB)
MODEL_REGISTRY: Dict[str, tuple[str, float]] = {
    "RealESRGAN_x2plus.pth": (
        "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth",
        64.0,
    ),
    "RealESRGAN_x4plus.pth": (
        "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
        64.0,
    ),
}


def download_file(
    url: str,
    destination: Path,
    progress_callback: Optional[Callable[[float], None]] = None,
    cancel_event: Optional[threading.Event] = None,
    chunk_size: int = 65_536,
) -> bool:
    """Baixa um arquivo em modo streaming com suporte a cancelamento.

    Returns:
        True se download completo, False se cancelado ou falhou.
    """
    temp_path = destination.with_suffix(destination.suffix + ".part")
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        total_bytes = int(response.headers.get("Content-Length", 0))
        downloaded = 0

        with temp_path.open("wb") as fh:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if cancel_event and cancel_event.is_set():
                    logger.info("Download cancelado: %s", destination.name)
                    temp_path.unlink(missing_ok=True)
                    return False
                if not chunk:
                    continue
                fh.write(chunk)
                downloaded += len(chunk)
                if progress_callback and total_bytes:
                    progress_callback(downloaded / total_bytes * 100.0)

        # Mover arquivo parcial para destino final
        if destination.exists():
            destination.unlink()
        temp_path.rename(destination)
        logger.info(
            "Download concluído: %s (%.2f MB)",
            destination.name,
            downloaded / (1024 * 1024),
        )
        return True

    except Exception as exc:
        logger.error("Falha no download de %s: %s", destination.name, exc)
        temp_path.unlink(missing_ok=True)
        raise


def validate_model_file(path: Path, min_size_mb: float = 10.0) -> bool:
    """Valida se o arquivo do modelo existe e tem tamanho mínimo aceitável."""
    if not path.exists():
        return False
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb < min_size_mb:
        logger.warning(
            "Modelo %s suspeito: %.2f MB (mínimo esperado: %.0f MB)",
            path.name, size_mb, min_size_mb,
        )
        return False
    return True


class ModelManagerDialog(tk.Toplevel):
    """Diálogo de gerenciamento de modelos Real-ESRGAN."""

    def __init__(
        self,
        parent: tk.Tk,
        models_dir: Path,
        on_close: Optional[Callable[[], None]] = None,
        *,
        mandatory: bool = False,
    ) -> None:
        super().__init__(parent)
        self.title("Gerenciar Modelos — UpVision")
        self.geometry("600x480")
        self.minsize(500, 380)
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.models_dir = models_dir
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self._on_close = on_close
        self._mandatory = mandatory
        self._downloading = False
        self._cancel_event = threading.Event()
        self._download_thread: Optional[threading.Thread] = None

        # Variáveis de seleção por modelo
        self._check_vars: Dict[str, tk.BooleanVar] = {}

        self._build_ui()
        self._refresh_status()

        if mandatory:
            self.protocol("WM_DELETE_WINDOW", self._on_mandatory_close)
        else:
            self.protocol("WM_DELETE_WINDOW", self._on_normal_close)

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # --- Header ---
        header = ttk.Frame(self, padding=12)
        header.grid(row=0, column=0, sticky="ew")

        if self._mandatory:
            title_text = "Nenhum modelo encontrado"
            subtitle_text = "Selecione pelo menos um modelo para baixar antes de continuar."
        else:
            title_text = "Gerenciar Modelos"
            subtitle_text = "Baixe novos modelos ou verifique o status dos existentes."

        ttk.Label(header, text=title_text, font=("Segoe UI", 14, "bold")).pack(
            anchor="w"
        )
        ttk.Label(header, text=subtitle_text, font=("Segoe UI", 10)).pack(
            anchor="w", pady=(4, 0)
        )

        # --- Lista de modelos ---
        list_frame = ttk.LabelFrame(self, text="Modelos disponíveis", padding=8)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 8))
        list_frame.columnconfigure(0, weight=1)

        row = 0
        for model_name in MODEL_REGISTRY:
            var = tk.BooleanVar(value=False)
            self._check_vars[model_name] = var

            model_frame = ttk.Frame(list_frame)
            model_frame.grid(row=row, column=0, sticky="ew", pady=4)
            model_frame.columnconfigure(1, weight=1)

            chk = ttk.Checkbutton(model_frame, variable=var)
            chk.grid(row=0, column=0, padx=(0, 8))

            ttk.Label(
                model_frame,
                text=model_name,
                font=("Segoe UI", 10, "bold"),
            ).grid(row=0, column=1, sticky="w")

            self._status_label = ttk.Label(
                model_frame, text="...", font=("Segoe UI", 9)
            )
            self._status_label.grid(row=0, column=2, sticky="e", padx=(8, 0))
            # Guardar referência ao label de status
            model_frame._status_label = self._status_label  # type: ignore[attr-defined]
            model_frame._model_name = model_name  # type: ignore[attr-defined]

            row += 1

        self._model_frames = [
            list_frame.winfo_children()[i]
            for i in range(len(MODEL_REGISTRY))
        ]

        # --- Progresso ---
        progress_frame = ttk.Frame(self, padding=(12, 0, 12, 8))
        progress_frame.grid(row=2, column=0, sticky="ew")
        progress_frame.columnconfigure(0, weight=1)

        self._progress_var = tk.DoubleVar(value=0.0)
        self._progress_bar = ttk.Progressbar(
            progress_frame, variable=self._progress_var, maximum=100.0
        )
        self._progress_bar.grid(row=0, column=0, sticky="ew")

        self._progress_label = tk.StringVar(value="")
        ttk.Label(progress_frame, textvariable=self._progress_label).grid(
            row=1, column=0, sticky="w", pady=(4, 0)
        )

        # --- Botões ---
        btn_frame = ttk.Frame(self, padding=12)
        btn_frame.grid(row=3, column=0, sticky="ew")
        btn_frame.columnconfigure(0, weight=1)

        self._btn_download = ttk.Button(
            btn_frame, text="Baixar selecionados", command=self._on_download
        )
        self._btn_download.grid(row=0, column=0, sticky="e", padx=(0, 8))

        self._btn_cancel_download = ttk.Button(
            btn_frame,
            text="Cancelar download",
            command=self._on_cancel_download,
            state="disabled",
        )
        self._btn_cancel_download.grid(row=0, column=1, sticky="e", padx=(0, 8))

        close_text = "Fechar" if not self._mandatory else "Fechar"
        self._btn_close = ttk.Button(
            btn_frame, text=close_text, command=self._try_close
        )
        self._btn_close.grid(row=0, column=2, sticky="e")

    # ------------------------------------------------------------------ Status

    def _refresh_status(self) -> None:
        """Atualiza o status de cada modelo (baixado/ausente)."""
        for frame in self._model_frames:
            model_name = frame._model_name  # type: ignore[attr-defined]
            label = frame._status_label  # type: ignore[attr-defined]
            path = self.models_dir / model_name
            _, min_size = MODEL_REGISTRY[model_name]
            if validate_model_file(path, min_size):
                label.configure(text="✅ Baixado", foreground="green")
                self._check_vars[model_name].set(False)
            else:
                label.configure(text="❌ Ausente", foreground="red")
                self._check_vars[model_name].set(True)  # Pré-selecionar ausentes

    def _has_any_model(self) -> bool:
        """Retorna True se pelo menos um modelo válido existe."""
        for model_name in MODEL_REGISTRY:
            path = self.models_dir / model_name
            _, min_size = MODEL_REGISTRY[model_name]
            if validate_model_file(path, min_size):
                return True
        return False

    # ------------------------------------------------------------------ Actions

    def _on_download(self) -> None:
        selected = [
            name for name, var in self._check_vars.items() if var.get()
        ]
        if not selected:
            messagebox.showinfo(
                "UpVision", "Selecione pelo menos um modelo para baixar."
            )
            return

        self._downloading = True
        self._cancel_event.clear()
        self._btn_download.configure(state="disabled")
        self._btn_close.configure(state="disabled")
        self._btn_cancel_download.configure(state="normal")

        self._download_thread = threading.Thread(
            target=self._download_worker,
            args=(selected,),
            daemon=True,
        )
        self._download_thread.start()
        self._poll_download()

    def _download_worker(self, model_names: list[str]) -> None:
        total = len(model_names)
        for idx, model_name in enumerate(model_names, start=1):
            if self._cancel_event.is_set():
                break
            url, _ = MODEL_REGISTRY[model_name]
            dest = self.models_dir / model_name
            logger.info("[%d/%d] Baixando %s…", idx, total, model_name)

            def on_progress(pct: float, _idx=idx, _total=total) -> None:
                # Progresso geral: modelo atual contribui para 1/total
                overall = ((_idx - 1) / _total + pct / 100.0 / _total) * 100.0
                self._progress_var.set(overall)
                self._progress_label.set(
                    f"Baixando {model_name}… {pct:.0f}% ({_idx}/{_total})"
                )

            try:
                download_file(
                    url, dest,
                    progress_callback=on_progress,
                    cancel_event=self._cancel_event,
                )
            except Exception as exc:
                logger.error("Falha: %s — %s", model_name, exc)
                self._progress_label.set(f"Erro ao baixar {model_name}: {exc}")
                break

        self._downloading = False

    def _poll_download(self) -> None:
        if self._downloading:
            self.after(200, self._poll_download)
        else:
            self._btn_download.configure(state="normal")
            self._btn_close.configure(state="normal")
            self._btn_cancel_download.configure(state="disabled")
            self._refresh_status()
            if not self._cancel_event.is_set():
                self._progress_label.set("Download concluído.")
                self._progress_var.set(100.0)

    def _on_cancel_download(self) -> None:
        self._cancel_event.set()
        self._progress_label.set("Cancelando download…")
        self._btn_cancel_download.configure(state="disabled")

    # ------------------------------------------------------------------ Close

    def _try_close(self) -> None:
        if self._mandatory:
            self._on_mandatory_close()
        else:
            self._on_normal_close()

    def _on_mandatory_close(self) -> None:
        if not self._has_any_model():
            messagebox.showwarning(
                "UpVision",
                "Pelo menos um modelo é necessário para o UpVision funcionar.\n"
                "Selecione e baixe um modelo, ou feche o aplicativo.",
            )
            return
        self._finalize_close()

    def _on_normal_close(self) -> None:
        if self._downloading:
            self._cancel_event.set()
        self._finalize_close()

    def _finalize_close(self) -> None:
        if self._on_close:
            self._on_close()
        self.grab_release()
        self.destroy()
