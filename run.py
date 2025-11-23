#!/usr/bin/env python3
"""
Script de inicio del Analizador BBPP UiPath
Ejecutar: python run.py
"""

import sys
from pathlib import Path

# Agregar src al path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from src.ui.main_window import MainWindow

if __name__ == "__main__":
    print("=" * 60)
    print("  Analizador de Buenas Prácticas para UiPath")
    print("  Versión 0.1.0 Beta")
    print("  NTT Data")
    print("=" * 60)
    print()
    print("Iniciando aplicación...")
    print()
    
    app = MainWindow()
    app.run()
