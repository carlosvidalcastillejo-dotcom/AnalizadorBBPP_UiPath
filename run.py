#!/usr/bin/env python3
# Copyright (c) 2025 Carlos Vidal Castillejo
# Todos los derechos reservados.
# Este software es propietario. Ver LICENSE para detalles.

"""
Script de inicio del Analizador BBPP UiPath
Ejecutar: python run.py
"""

import sys
from pathlib import Path

# Agregar src al path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

if __name__ == "__main__":
    print("=" * 60)
    print("  Analizador de Buenas Prácticas para UiPath")
    print("  Versión 1.2.0")
    print("  Carlos Vidal Castillejo")
    print("=" * 60)
    print()
    print("Iniciando aplicación...")
    print()

    from src.ui.main_window import MainWindow
    app = MainWindow()
    app.run()
