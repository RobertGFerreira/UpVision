"""Aplica o patch de compatibilidade do basicsr com torchvision."""

from __future__ import annotations

import importlib.util
import os
import re
import sys

LEGACY_LINE_REGEX = r"from torchvision\.transforms\.functional_tensor import rgb_to_grayscale"
REPLACEMENT = (
    "try:\n"
    "    from torchvision.transforms.functional_tensor import rgb_to_grayscale  # legacy (torchvision antigo)\n"
    "except ImportError:\n"
    "    from torchvision.transforms.functional import rgb_to_grayscale  # fallback (torchvision >=0.15)\n"
)


def main() -> None:
    print("=== PATCH BASICSR ===")

    spec = importlib.util.find_spec("basicsr")
    if spec is None:
        print("[ERRO] basicsr não encontrado. Instale primero: pip install realesrgan==0.3.0")
        sys.exit(1)

    init_path = spec.origin
    if not init_path or not os.path.isfile(init_path):
        print("[ERRO] Não foi possível determinar caminho de basicsr (__init__).")
        sys.exit(1)

    basicsr_dir = os.path.dirname(init_path)
    target = os.path.join(basicsr_dir, "data", "degradations.py")

    if not os.path.isfile(target):
        print("[ERRO] Arquivo degradations.py não encontrado:", target)
        sys.exit(1)

    with open(target, "r", encoding="utf-8") as handle:
        content = handle.read()

    if REPLACEMENT.strip() in content:
        print("[INFO] Patch aparentemente já aplicado.")
        print("Arquivo:", target)
        return

    if re.search(LEGACY_LINE_REGEX, content) is None:
        print("[AVISO] Linha legacy não encontrada. Confira manualmente:")
        print("Arquivo:", target)
        return

    backup = target + ".bak"
    if not os.path.isfile(backup):
        with open(backup, "w", encoding="utf-8") as backup_file:
            backup_file.write(content)
        print("[INFO] Backup criado em:", backup)
    else:
        print("[INFO] Backup já existente:", backup)

    patched, count = re.subn(LEGACY_LINE_REGEX, REPLACEMENT.rstrip(), content, count=1)
    if count == 0:
        print("[ERRO] Nenhuma substituição realizada (regex não casou).")
        sys.exit(1)

    with open(target, "w", encoding="utf-8") as handle:
        handle.write(patched)

    print(f"[SUCESSO] Patch aplicado. Substituições: {count}")
    print("Arquivo modificado:", target)

    print("[INFO] Teste rápido de import...")
    try:
        from realesrgan import RealESRGANer  # type: ignore  # noqa: F401
        from basicsr.archs.rrdbnet_arch import RRDBNet  # type: ignore  # noqa: F401
        print("[OK] Import RealESRGAN/BasisSR após patch.")
    except Exception as exc:  # pragma: no cover
        print("[ERRO] Ainda falha ao importar após patch:")
        print(exc)
        print("Se persistir, compare o arquivo degradations.py com a versão original.")

    print("=== FIM PATCH ===")


if __name__ == "__main__":
    main()
