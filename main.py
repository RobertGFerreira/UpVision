"""UpVision – Aplicativo desktop para realizar upscale de imagens com Real-ESRGAN.

Recursos principais:
- Seleção múltipla de arquivos de imagem.
- Escolha de diretório de saída.
- Seleção de checkpoint (``models_realesrgan/*.pth``) e do dispositivo (CPU/GPU).
- Execução em thread separada com logs ao vivo e barra de progresso.

Como executar:

```
python main.py
```
"""

import os
import queue
import threading
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import tkinter as tk

from PIL import Image, ImageTk

from engine import BatchResult, UpscaleEngine

APP_TITLE = "UpVision"
APP_SUBTITLE = "Real-ESRGAN Upscale"
PADDING = 16


class UpscaleApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("900x750")
        self.root.minsize(820, 600)

        self.engine = UpscaleEngine()
        self.device_summary = self.engine.get_device_summary()
        self.models = self.engine.list_models()
        self.default_assets_dir = (self.engine.app_dir / "assets") if hasattr(self.engine, "app_dir") else None

        self.event_queue: "queue.Queue[tuple[str, object]]" = queue.Queue()
        self.selected_files: list[Path] = []
        self.output_dir: Path | None = None
        self.processing = False
        self.current_total = 0
        self._first_run_sentinel = self.engine.app_dir / ".first_run_complete"
        self._first_run_active = False
        self._first_run_test_image: Path | None = None
        self._first_run_expected_outputs: list[Path] = []
        self._test_alert_window: tk.Toplevel | None = None
        self.logo_path = self.engine.app_dir / "assets" / "upvision_logo.png"
        self.logo_image: tk.PhotoImage | None = None
        self.header_title_var = tk.StringVar(value=APP_TITLE)
        self.header_subtitle_var = tk.StringVar(value=APP_SUBTITLE)

        self._build_ui()
        self._load_brand_assets()
        self._populate_models()
        self._populate_devices()
        self._update_status_line()
        self._start_queue_poller()
        self._maybe_schedule_first_run()

    # ------------------------------------------------------------------
    # UI construction

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main_frame = ttk.Frame(self.root, padding=PADDING)
        main_frame.grid(row=0, column=0, sticky="nsew")
        for col in range(3):
            main_frame.columnconfigure(col, weight=1)
        main_frame.rowconfigure(5, weight=1)
        main_frame.rowconfigure(6, weight=2)

        # Cabeçalho ------------------------------------------------------
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 16))
        header_frame.columnconfigure(1, weight=1)
        header_frame.columnconfigure(2, weight=1)

        self.header_image_label = ttk.Label(header_frame)
        self.header_image_label.grid(row=0, column=0, rowspan=2, sticky="nw", padx=(0, 12))

        self.header_title_label = ttk.Label(
            header_frame,
            textvariable=self.header_title_var,
            font=("Segoe UI", 20, "bold"),
            anchor="center",
        )
        self.header_title_label.grid(row=0, column=1, columnspan=2, sticky="ew")

        self.header_subtitle_label = ttk.Label(
            header_frame,
            textvariable=self.header_subtitle_var,
            font=("Segoe UI", 11),
            anchor="center",
        )
        self.header_subtitle_label.grid(row=1, column=1, columnspan=2, sticky="ew")

        # Arquivos -------------------------------------------------------
        file_frame = ttk.LabelFrame(main_frame, text="Arquivos de entrada")
        file_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=(0, 0), pady=(0, 12))
        file_frame.columnconfigure(0, weight=1)

        btn_select = ttk.Button(file_frame, text="Adicionar imagens…", command=self._on_select_files)
        btn_select.grid(row=0, column=0, sticky="w", padx=8, pady=8)

        btn_select_folder = ttk.Button(file_frame, text="Adicionar pasta…", command=self._on_select_folder)
        btn_select_folder.grid(row=0, column=1, sticky="w", padx=8, pady=8)

        btn_clear = ttk.Button(file_frame, text="Limpar lista", command=self._on_clear_files)
        btn_clear.grid(row=0, column=2, sticky="w", padx=8, pady=8)

        self.files_list = tk.Listbox(file_frame, height=6, selectmode=tk.SINGLE)
        self.files_list.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=(0, 8))
        file_frame.rowconfigure(1, weight=1)

        self.files_summary = tk.StringVar(value="Nenhuma imagem selecionada.")
        ttk.Label(file_frame, textvariable=self.files_summary).grid(row=2, column=0, columnspan=2, sticky="w", padx=8, pady=(0, 8))

        # Destino --------------------------------------------------------
        dest_frame = ttk.LabelFrame(main_frame, text="Destino")
        dest_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 12))
        dest_frame.columnconfigure(1, weight=1)

        ttk.Label(dest_frame, text="Pasta de saída:").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.dest_var = tk.StringVar(value="Nenhuma" )
        dest_entry = ttk.Entry(dest_frame, textvariable=self.dest_var, state="readonly")
        dest_entry.grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=8)

        ttk.Button(dest_frame, text="Escolher…", command=self._on_select_output_dir).grid(row=0, column=2, padx=8, pady=8)

        # Opções ---------------------------------------------------------
        options_frame = ttk.LabelFrame(main_frame, text="Opções")
        options_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0, 12))
        for col in range(4):
            options_frame.columnconfigure(col, weight=1)

        ttk.Label(options_frame, text="Checkpoint:").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(options_frame, textvariable=self.model_var, state="readonly")
        self.model_combo.grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=8)
        self.model_combo.bind("<<ComboboxSelected>>", lambda e: self._update_status_line())

        ttk.Label(options_frame, text="Dispositivo:").grid(row=0, column=2, sticky="w", padx=8, pady=8)
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(options_frame, textvariable=self.device_var, state="readonly")
        self.device_combo.grid(row=0, column=3, sticky="ew", padx=(0, 8), pady=8)

        # Ações ----------------------------------------------------------
        actions_frame = ttk.Frame(main_frame)
        actions_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(0, 12))
        actions_frame.columnconfigure(0, weight=1)

        self.btn_start = ttk.Button(actions_frame, text="Iniciar upscale", command=self._on_start)
        self.btn_start.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.btn_stop = ttk.Button(actions_frame, text="Cancelar", command=self._on_cancel, state="disabled")
        self.btn_stop.grid(row=0, column=1, sticky="e")

        self.btn_view_results = ttk.Button(actions_frame, text="Visualizar resultados", command=self._on_view_results)
        self.btn_view_results.grid(row=0, column=2, sticky="e", padx=(8, 0))

        # Progresso ------------------------------------------------------
        progress_frame = ttk.LabelFrame(main_frame, text="Progresso")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=(0, 12))
        progress_frame.columnconfigure(0, weight=1)

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100.0)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))

        self.progress_label = tk.StringVar(value="Aguardando…")
        ttk.Label(progress_frame, textvariable=self.progress_label).grid(row=1, column=0, sticky="w", padx=8, pady=(0, 8))

        # Logs -----------------------------------------------------------
        log_frame = ttk.LabelFrame(main_frame, text="Logs")
        log_frame.grid(row=6, column=0, columnspan=3, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, wrap="word", height=20, state="disabled")
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_scroll.grid(row=0, column=1, sticky="ns", pady=8)
        self.log_text.configure(yscrollcommand=log_scroll.set)

        # Status ---------------------------------------------------------
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=1, column=0, sticky="ew")
        status_frame.columnconfigure(0, weight=1)
        self.status_var = tk.StringVar()
        ttk.Label(status_frame, textvariable=self.status_var, anchor="w").grid(row=0, column=0, sticky="ew", padx=PADDING, pady=(0, 4))

    # ------------------------------------------------------------------
    # UI helpers

    def _populate_models(self) -> None:
        names = [model.name for model in self.models]
        self.model_combo["values"] = names
        if names:
            self.model_combo.configure(state="readonly")
            self.model_combo.current(0)
        else:
            self.model_var.set("Nenhum modelo encontrado")
            self.model_combo.configure(state="disabled")
        self._update_start_button()

    def _populate_devices(self) -> None:
        items = []
        default = "cpu"
        if self.device_summary.torch_available:
            items.append("cpu")
            if self.device_summary.cuda_available:
                items.append("cuda")
                default = "cuda"
        else:
            items.append("torch ausente")
            self.device_combo.configure(state="disabled")
        self.device_combo["values"] = items
        self.device_combo.set(default)
        self._update_start_button()

    def _update_status_line(self) -> None:
        summary = self.device_summary
        if not summary.torch_available:
            self.status_var.set("Torch não instalado. Instale torch/torchvision/torchaudio para continuar.")
            return
        cuda_text = "Sim" if summary.cuda_available else "Não"
        gpu_name = summary.cuda_device_name or "—"
        model_path = str(self.engine.models_dir)

        selected_model = self.model_var.get()
        if selected_model:
            model_info = next((m for m in self.models if m.name == selected_model), None)
            if model_info:
                try:
                    model_rel_path = model_info.path.relative_to(self.engine.app_dir)
                    model_text = str(model_rel_path)
                except ValueError:
                    model_text = str(model_info.path)
            else:
                model_text = "Modelo não encontrado"
        else:
            model_text = "Nenhum modelo selecionado"

        self.status_var.set(
            f"Torch {summary.torch_version} | CUDA compilado: {summary.torch_cuda_compiled or '—'} | CUDA disponível: {cuda_text} | GPU: {gpu_name} | Modelo: {model_text}"
        )

    def _append_log(self, message: str) -> None:
        print(message, flush=True)
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _load_brand_assets(self) -> None:
        if not self.logo_path.exists():
            self._append_log(
                f"[AVISO] Logo do UpVision não encontrada em {self.logo_path}."
            )
            return
        try:
            pil_image = Image.open(self.logo_path)
        except Exception as exc:  # pragma: no cover - depende do sistema de arquivos
            self._append_log(f"[ERRO] Falha ao abrir a logo do UpVision: {exc}")
            return

        max_size = (120, 120)
        try:
            resample = Image.Resampling.LANCZOS  # type: ignore[attr-defined]
        except AttributeError:  # Pillow < 9.1
            resample = Image.LANCZOS
        pil_image.thumbnail(max_size, resample=resample)

        try:
            image = ImageTk.PhotoImage(pil_image)
        except Exception as exc:  # pragma: no cover - depende do backend Tk
            self._append_log(f"[ERRO] Falha ao converter a logo do UpVision: {exc}")
            return

        self.logo_image = image
        self.header_image_label.configure(image=self.logo_image)
        self.header_image_label.image = self.logo_image  # evitar GC
        try:
            self.root.iconphoto(False, self.logo_image)
        except tk.TclError:  # pragma: no cover - algumas plataformas não suportam
            pass

    def _show_test_alert(self) -> None:
        self._close_test_alert()
        window = tk.Toplevel(self.root)
        window.title("Auto-teste inicial")
        window.resizable(False, False)
        window.transient(self.root)
        window.attributes("-topmost", True)
        window.protocol("WM_DELETE_WINDOW", lambda: None)

        padding = ttk.Frame(window, padding=20)
        padding.grid(sticky="nsew")

        ttk.Label(
            padding,
            text=(
                "Executando auto-teste inicial...\n"
                "• Validando importações e dependências\n"
                "• Conferindo dispositivos disponíveis\n"
                "• Processando imagem de exemplo"
            ),
            justify="left",
        ).grid(row=0, column=0, sticky="w")

        progress = ttk.Progressbar(padding, mode="indeterminate")
        progress.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        padding.columnconfigure(0, weight=1)
        progress.start(10)

        self._test_alert_window = window

    def _close_test_alert(self) -> None:
        if self._test_alert_window is not None:
            try:
                self._test_alert_window.destroy()
            except tk.TclError:
                pass
            finally:
                self._test_alert_window = None

    def _schedule_auto_shutdown(self, success: bool) -> None:
        if success:
            self._append_log(
                "Auto-teste finalizado. O aplicativo será fechado e poderá ser reaberto para uso normal."
            )
        else:
            self._append_log(
                "Auto-teste não foi concluído com sucesso. O aplicativo será fechado; ajuste o ambiente antes de abrir novamente."
            )
        self.root.after(1500, self.root.destroy)

    def _set_processing_state(self, processing: bool) -> None:
        self.processing = processing
        for widget in (self.model_combo, self.device_combo, self.files_list):
            widget.configure(state="disabled" if processing else "normal")
        self._update_start_button()
        self.btn_stop.configure(state="normal" if processing else "disabled")

    def _update_start_button(self) -> None:
        if self.processing:
            self.btn_start.configure(state="disabled")
            return
        if not self.models or not self.device_summary.torch_available:
            self.btn_start.configure(state="disabled")
        else:
            self.btn_start.configure(state="normal")

    # ------------------------------------------------------------------
    # Event handlers

    def _on_select_files(self) -> None:
        filetypes = [
            ("Imagens", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff;*.webp"),
            ("Todos os arquivos", "*.*"),
        ]
        dialog_kwargs = {"title": "Selecione imagens", "filetypes": filetypes}
        if self.default_assets_dir and self.default_assets_dir.exists():
            dialog_kwargs["initialdir"] = str(self.default_assets_dir)
        filenames = filedialog.askopenfilenames(**dialog_kwargs)
        if not filenames:
            return
        for name in filenames:
            path = Path(name)
            if path not in self.selected_files:
                self.selected_files.append(path)
                self.files_list.insert("end", path.name)
        self.files_summary.set(f"{len(self.selected_files)} arquivo(s) selecionado(s).")

    def _on_clear_files(self) -> None:
        self.selected_files.clear()
        self.files_list.delete(0, "end")
        self.files_summary.set("Nenhuma imagem selecionada.")

    def _on_select_folder(self) -> None:
        dialog_kwargs = {"title": "Escolha a pasta com imagens"}
        if self.default_assets_dir and self.default_assets_dir.exists():
            dialog_kwargs["initialdir"] = str(self.default_assets_dir)
        folder = filedialog.askdirectory(**dialog_kwargs)
        if not folder:
            return
        folder_path = Path(folder)
        exts = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
        new_files = []
        for path in folder_path.rglob("*"):
            if path.is_file() and path.suffix.lower() in exts and path not in self.selected_files:
                new_files.append(path)
        self.selected_files.extend(new_files)
        for path in new_files:
            self.files_list.insert("end", path.name)
        self.files_summary.set(f"{len(self.selected_files)} arquivo(s) selecionado(s).")

    def _on_select_output_dir(self) -> None:
        dialog_kwargs = {"title": "Escolha a pasta de destino"}
        if self.default_assets_dir and self.default_assets_dir.exists():
            dialog_kwargs["initialdir"] = str(self.default_assets_dir)
        directory = filedialog.askdirectory(**dialog_kwargs)
        if directory:
            self.output_dir = Path(directory)
            self.dest_var.set(directory)

    def _on_start(self) -> None:
        if not self.selected_files:
            messagebox.showwarning(APP_TITLE, "Selecione pelo menos uma imagem.")
            return
        if self.output_dir is None:
            messagebox.showwarning(APP_TITLE, "Escolha a pasta de destino.")
            return
        if self.model_var.get() not in {model.name for model in self.models}:
            messagebox.showwarning(APP_TITLE, "Escolha um checkpoint válido.")
            return
        device_choice = self.device_var.get().lower()
        if device_choice.startswith("cuda") and not self.device_summary.cuda_available:
            messagebox.showerror(APP_TITLE, "CUDA não está disponível neste ambiente.")
            return

        self._append_log("Iniciando processamento…")
        self.progress_var.set(0.0)
        self.progress_label.set("0 / {0}".format(len(self.selected_files)))
        self.current_total = len(self.selected_files)
        self._set_processing_state(True)

        thread = threading.Thread(
            target=self._worker,
            args=(
                list(self.selected_files),
                self.output_dir,
                self.model_var.get(),
                device_choice,
            ),
            daemon=True,
        )
        thread.start()

    def _on_cancel(self) -> None:
        messagebox.showinfo(
            "Cancelar", "O cancelamento imediato não está disponível. Aguarde a conclusão da imagem atual."
        )

    def _on_view_results(self) -> None:
        if not self.output_dir or not self.output_dir.exists():
            messagebox.showwarning(APP_TITLE, "Nenhuma pasta de destino definida ou não existe.")
            return
        
        # Coletar imagens processadas
        processed_images = []
        for file_path in self.output_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.tiff', '.webp']:
                processed_images.append(file_path)
        
        if not processed_images:
            messagebox.showinfo(APP_TITLE, "Nenhuma imagem processada encontrada na pasta de destino.")
            return
        
        # Criar janela de visualização
        self._show_comparison_window(processed_images)

    def _show_comparison_window(self, processed_images: list[Path]) -> None:
        """Mostra janela com imagens originais e processadas lado a lado."""
        window = tk.Toplevel(self.root)
        window.title("Comparação de Imagens - UpVision")
        window.geometry("1200x800")
        window.minsize(800, 600)
        
        # Frame principal com scrollbar
        main_frame = ttk.Frame(window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas e scrollbar para rolagem
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mousewheel para rolagem
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Título
        title_label = ttk.Label(scrollable_frame, text="Comparação: Original × Processada", 
                               font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Para cada imagem processada, tentar encontrar a original
        for processed_path in sorted(processed_images):
            self._add_image_comparison(scrollable_frame, processed_path)
        
        # Botão fechar
        close_button = ttk.Button(scrollable_frame, text="Fechar", command=window.destroy)
        close_button.pack(pady=20)

    def _add_image_comparison(self, parent: ttk.Frame, processed_path: Path) -> None:
        """Adiciona uma comparação de imagem ao frame."""
        # Tentar encontrar imagem original
        original_path = self._find_original_image(processed_path)
        
        # Frame para esta comparação
        comparison_frame = ttk.Frame(parent)
        comparison_frame.pack(fill=tk.X, pady=10)
        
        # Nome do arquivo
        filename = processed_path.name
        name_label = ttk.Label(comparison_frame, text=filename, font=("Segoe UI", 10, "bold"))
        name_label.pack(pady=(0, 10))
        
        # Frame para imagens lado a lado
        images_frame = ttk.Frame(comparison_frame)
        images_frame.pack(fill=tk.X)
        
        # Imagem original
        original_frame = ttk.LabelFrame(images_frame, text="Original", padding=10)
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        if original_path and original_path.exists():
            try:
                original_img = Image.open(original_path)
                # Redimensionar mantendo proporção
                original_img.thumbnail((400, 400), Image.Resampling.LANCZOS)
                original_photo = ImageTk.PhotoImage(original_img)
                
                original_label = ttk.Label(original_frame, image=original_photo)
                original_label.image = original_photo  # Manter referência
                original_label.pack()
                
                # Info da imagem
                orig_info = f"{original_img.size[0]}×{original_img.size[1]}"
                ttk.Label(original_frame, text=orig_info, font=("Segoe UI", 8)).pack(pady=(5, 0))
                
            except Exception as e:
                ttk.Label(original_frame, text=f"Erro ao carregar:\n{str(e)}", 
                         font=("Segoe UI", 8)).pack()
        else:
            ttk.Label(original_frame, text="Original não encontrada", 
                     font=("Segoe UI", 8)).pack()
        
        # Imagem processada
        processed_frame = ttk.LabelFrame(images_frame, text="Processada", padding=10)
        processed_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        try:
            processed_img = Image.open(processed_path)
            # Redimensionar mantendo proporção
            processed_img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            processed_photo = ImageTk.PhotoImage(processed_img)
            
            processed_label = ttk.Label(processed_frame, image=processed_photo)
            processed_label.image = processed_photo  # Manter referência
            processed_label.pack()
            
            # Info da imagem
            proc_info = f"{processed_img.size[0]}×{processed_img.size[1]}"
            ttk.Label(processed_frame, text=proc_info, font=("Segoe UI", 8)).pack(pady=(5, 0))
            
        except Exception as e:
            ttk.Label(processed_frame, text=f"Erro ao carregar:\n{str(e)}", 
                     font=("Segoe UI", 8)).pack()

    def _find_original_image(self, processed_path: Path) -> Path | None:
        """Tenta encontrar a imagem original correspondente à processada."""
        # O padrão do Real-ESRGAN adiciona sufixo como _x2, _x4, etc.
        stem = processed_path.stem
        
        # Possíveis padrões: nome_x2.jpg, nome_x4.jpg, etc.
        # Remover sufixos comuns
        for suffix in ['_x2', '_x4', '_x8', '_sr']:
            if stem.endswith(suffix):
                original_stem = stem[:-len(suffix)]
                original_path = processed_path.parent / f"{original_stem}{processed_path.suffix}"
                if original_path.exists():
                    return original_path
                # Também tentar na pasta de entrada se conhecida
                if hasattr(self, 'selected_files') and self.selected_files:
                    for input_file in self.selected_files:
                        if input_file.stem == original_stem and input_file.suffix == processed_path.suffix:
                            return input_file
        
        # Se não encontrou, tentar procurar por nome similar na pasta de entrada
        if hasattr(self, 'selected_files') and self.selected_files:
            for input_file in self.selected_files:
                if input_file.stem in stem and input_file.suffix == processed_path.suffix:
                    return input_file
        
        # Último recurso: procurar na mesma pasta por arquivos com nome similar
        for file_path in processed_path.parent.iterdir():
            if (file_path != processed_path and 
                file_path.is_file() and 
                file_path.suffix.lower() == processed_path.suffix.lower()):
                # Verificar se o nome do arquivo processado contém o nome do original
                if file_path.stem in stem:
                    return file_path
                # Ou se são muito similares (removendo sufixos comuns)
                orig_stem = file_path.stem
                proc_stem = stem
                # Remover sufixos comuns do processado
                for sfx in ['_upscaled', '_enhanced', '_processed', '_result']:
                    if proc_stem.endswith(sfx):
                        proc_stem = proc_stem[:-len(sfx)]
                        break
                if orig_stem == proc_stem:
                    return file_path
        
        return None

    # ------------------------------------------------------------------
    # Background worker & queue polling

    def _worker(self, images: list[Path], output_dir: Path, model_name: str, device: str) -> None:
        try:
            self.engine.process_batch(images, output_dir, model_name, device, self.event_queue)
        except Exception as exc:
            self.event_queue.put(("error", str(exc)))
            self.event_queue.put(("done", None))

    def _start_queue_poller(self) -> None:
        self.root.after(100, self._poll_queue)

    def _poll_queue(self) -> None:
        try:
            while True:
                event, payload = self.event_queue.get_nowait()
                if event == "log":
                    self._append_log(str(payload))
                elif event == "progress":
                    current, total, filename = payload  # type: ignore[misc]
                    self.progress_var.set((current / total) * 100.0 if total else 0.0)
                    self.progress_label.set(f"Processando: {filename} ({current} / {total})")
                elif event == "done":
                    self._finalise_run(payload)
                elif event == "error":
                    error_text = str(payload)
                    self._append_log(f"[ERRO] {error_text}")
                    if not self._first_run_active:
                        messagebox.showerror(APP_TITLE, error_text)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._poll_queue)

    def _finalise_run(self, payload: object) -> None:
        self._set_processing_state(False)
        if not self._first_run_active:
            self.progress_label.set("Concluído")
        first_run_active = self._first_run_active
        if first_run_active:
            self._close_test_alert()
        first_run_success = False
        show_dialogs = not first_run_active
        if isinstance(payload, BatchResult):
            summary = (
                f"Processadas: {payload.succeeded}/{payload.total} | Falhas: {payload.failed} | Tempo: {payload.duration:.2f}s"
            )
            self._append_log(summary)
            if show_dialogs:
                messagebox.showinfo(APP_TITLE, summary)
            first_run_success = payload.succeeded > 0 and payload.failed == 0
        else:
            self._append_log("Execução encerrada.")
            first_run_success = False
        if first_run_active:
            try:
                if first_run_success:
                    self._first_run_sentinel.touch(exist_ok=True)
                    removed_files: list[str] = []
                    for output_path in list(self._first_run_expected_outputs):
                        try:
                            if output_path.exists():
                                output_path.unlink()
                                removed_files.append(output_path.name)
                        except Exception as err:  # pragma: no cover - best effort cleanup
                            self._append_log(f"[ERRO] Não foi possível remover {output_path.name}: {err}")
                    if removed_files:
                        self._append_log(
                            "Imagens de teste removidas: " + ", ".join(removed_files)
                        )
                    self._append_log("Teste automático concluído com sucesso. Aplicativo pronto para uso.")
                    self._on_clear_files()
                    self.output_dir = None
                    self.dest_var.set("Nenhuma")
                else:
                    self._append_log(
                        "Teste automático falhou; ajuste o ambiente e reinicie o aplicativo para tentar novamente."
                    )
            finally:
                self._first_run_expected_outputs.clear()
                self._first_run_test_image = None
                self._first_run_active = False
                self._schedule_auto_shutdown(first_run_success)

    def _maybe_schedule_first_run(self) -> None:
        if self._first_run_sentinel.exists():
            return
        assets_dir = self.default_assets_dir or (self.engine.app_dir / "assets")
        test_image = assets_dir / "teste_realesrgan.jpg"
        if not test_image.exists():
            return
        if not self.models:
            self._append_log(
                "Primeira inicialização automática ignorada: nenhum modelo Real-ESRGAN encontrado."
            )
            return

        def trigger() -> None:
            if self._first_run_sentinel.exists():
                return
            if not test_image.exists():
                self._append_log(
                    "Teste automático não executado: arquivo teste_realesrgan.jpg ausente."
                )
                return
            self._first_run_test_image = test_image
            self.selected_files = [test_image]
            self.files_list.delete(0, "end")
            self.files_list.insert("end", test_image.name)
            self.files_summary.set("1 arquivo(s) selecionado(s).")

            destination = assets_dir if assets_dir.exists() else test_image.parent
            self.output_dir = destination
            self.dest_var.set(str(destination))

            if self.model_combo["state"] == "readonly" and self.model_combo["values"]:
                self.model_combo.current(0)
            model_index = self.model_combo.current()
            if model_index < 0 and self.models:
                model_index = 0
            if not self.device_var.get() and self.device_combo["values"]:
                self.device_combo.current(0)

            expected_outputs: list[Path] = []
            if 0 <= model_index < len(self.models):
                model_info = self.models[model_index]
                expected_outputs.append(
                    destination / f"{test_image.stem}_x{model_info.scale}{test_image.suffix}"
                )
            self._first_run_expected_outputs = expected_outputs

            self._append_log(
                "Auto-teste inicial: validando importações, recursos e processando a imagem teste_realesrgan.jpg."
            )
            self._show_test_alert()
            self._first_run_active = True
            self.root.after(200, self._on_start)

        self.root.after(500, trigger)

    # ------------------------------------------------------------------
    # Public entry point

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    root = tk.Tk()
    app = UpscaleApp(root)
    app.run()


if __name__ == "__main__":
    main()
