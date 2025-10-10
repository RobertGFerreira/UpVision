#!/usr/bin/env python3
"""
Teste da funcionalidade de comparação de imagens
"""
import sys
import os
from pathlib import Path

# Adicionar o diretório atual ao path para importar main
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import UpscaleApp

def test_comparison():
    """Testa a funcionalidade de comparação de imagens"""
    print("Testando funcionalidade de comparação de imagens...")

    # Criar uma instância da aplicação (sem interface)
    app = UpscaleApp.__new__(UpscaleApp)  # Criar sem __init__

    # Testar o método de detecção
    processed_path = Path("assets/teste_realesrgan_sr.jpg")
    original_path = app._find_original_image(processed_path)

    print(f"Imagem processada: {processed_path}")
    print(f"Imagem original encontrada: {original_path}")

    if original_path and original_path.exists():
        print("✅ Detecção funcionou!")
        return True
    else:
        print("❌ Detecção falhou!")
        return False

if __name__ == "__main__":
    test_comparison()