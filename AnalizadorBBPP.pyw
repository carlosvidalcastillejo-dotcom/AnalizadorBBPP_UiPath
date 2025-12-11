#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Carlos Vidal Castillejo
# Todos los derechos reservados.
# Este software es propietario. Ver LICENSE para detalles.

"""
Launcher sin consola para Analizador BBPP UiPath
Este archivo se ejecuta con pythonw.exe (Python sin ventana de consola)
"""

import sys
from pathlib import Path

# Agregar directorio raíz al path para imports
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

if __name__ == "__main__":
    # Importar y ejecutar la aplicación
    from src.ui.main_window import MainWindow
    app = MainWindow()
    app.run()
