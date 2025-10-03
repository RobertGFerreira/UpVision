"""
patch_basicsr_torchvision_noimport.py
Patch NÃO carrega o pacote basicsr (evita executar __init__) – apenas localiza o diretório via importlib
e substitui o import legacy 'functional_tensor' por um bloco try/except compatível com versões novas do torchvision.

Uso:
  python patch_basicsr_torchvision_noimport.py

Depois testar:
  python -c "from realesrgan import RealESRGANer; from basicsr.archs.rrdbnet_arch import RRDBNet; print('IMPORT OK')"
"""

import os
import sys
import re
import importlib.util

LEGACY_LINE_REGEX = r'from torchvision\.transforms\.functional_tensor import rgb_to_grayscale'
REPLACEMENT = (
    "try:\n"
    "    from torchvision.transforms.functional_tensor import rgb_to_grayscale  # legacy (torchvision antigo)\n"
    "except ImportError:\n"
    "    from torchvision.transforms.functional import rgb_to_grayscale  # fallback (torchvision >=0.15)\n"
)

def main():
    print("=== PATCH BASICSR (SEM IMPORT EXECUTAR) ===")

    spec = importlib.util.find_spec("basicsr")
    if spec is None:
        print("[ERRO] basicsr não encontrado. Instale primeiro: pip install realesrgan==0.3.0")
        sys.exit(1)

    # Caminho do arquivo __init__.py
    init_path = spec.origin
    if not init_path or not os.path.isfile(init_path):
        print("[ERRO] Não foi possível determinar caminho de basicsr (__init__).")
        sys.exit(1)

    basicsr_dir = os.path.dirname(init_path)
    target = os.path.join(basicsr_dir, "data", "degradations.py")

    if not os.path.isfile(target):
        print("[ERRO] Arquivo degradations.py não encontrado:", target)
        sys.exit(1)

    with open(target, "r", encoding="utf-8") as f:
        content = f.read()

    if REPLACEMENT.strip() in content:
        print("[INFO] Patch aparentemente já aplicado (bloco encontrado).")
        print("Arquivo:", target)
        return

    if re.search(LEGACY_LINE_REGEX, content) is None:
        print("[AVISO] Linha legacy não encontrada. Mostrando começo do arquivo para inspeção manual:\n")
        print("\n".join(content.splitlines()[:40]))
        print("\nSe não houver a linha 'from torchvision.transforms.functional_tensor import rgb_to_grayscale', pode ter mudado a versão.")
        return

    backup = target + ".bak"
    if not os.path.isfile(backup):
        with open(backup, "w", encoding="utf-8") as bf:
            bf.write(content)
        print("[INFO] Backup criado em:", backup)
    else:
        print("[INFO] Backup já existia:", backup)

    patched, count = re.subn(LEGACY_LINE_REGEX, REPLACEMENT.rstrip(), content, count=1)
    if count == 0:
        print("[ERRO] Nenhuma substituição realizada (regex não casou).")
        sys.exit(1)

    with open(target, "w", encoding="utf-8") as f:
        f.write(patched)

    print(f"[SUCESSO] Patch aplicado. Substituições: {count}")
    print("Arquivo modificado:", target)

    print("[INFO] Teste rápido de import (pode demorar alguns segundos)...")
    # Agora testamos import
    try:
        from realesrgan import RealESRGANer  # noqa: F401
        from basicsr.archs.rrdbnet_arch import RRDBNet  # noqa: F401
        print("[OK] Import RealESRGAN/BasisSR após patch.")
    except Exception as e:
        print("[ERRO] Ainda falha ao importar após patch:")
        print(e)
        print("Se persistir, envie as primeiras ~60 linhas do degradations.py para análise.")

    print("=== FIM PATCH ===")

if __name__ == "__main__":
    main()