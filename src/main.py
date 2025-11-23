"""
Analizador de Buenas Prácticas para UiPath
Versión: 0.1.0 Beta
Autor: Carlos + Claude
Empresa: NTT Data
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.ui.main_window import MainWindow

def main():
    """Punto de entrada principal de la aplicación"""
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main()
