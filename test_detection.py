#!/usr/bin/env python3
"""Teste rápido da funcionalidade de detecção de imagens."""

from pathlib import Path

def test_find_original():
    # Simular a lógica de detecção
    processed_path = Path("assets/teste_realesrgan_sr.jpg")

    stem = processed_path.stem
    print(f"Stem da imagem processada: {stem}")

    # Testar sufixos
    for suffix in ['_x2', '_x4', '_x8', '_sr']:
        if stem.endswith(suffix):
            original_stem = stem[:-len(suffix)]
            original_path = processed_path.parent / f"{original_stem}{processed_path.suffix}"
            print(f"Tentando sufixo '{suffix}': {original_path} -> {'existe' if original_path.exists() else 'não existe'}")
            if original_path.exists():
                return original_path

    # Último recurso
    for file_path in processed_path.parent.iterdir():
        if (file_path != processed_path and
            file_path.is_file() and
            file_path.suffix.lower() == processed_path.suffix.lower()):
            print(f"Arquivo similar encontrado: {file_path}")
            if file_path.stem in stem:
                return file_path

    return None

if __name__ == "__main__":
    result = test_find_original()
    print(f"Resultado: {result}")