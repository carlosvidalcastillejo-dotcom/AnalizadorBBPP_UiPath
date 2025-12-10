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

# Verificar e instalar dependencias antes de cargar la UI
from src.dependency_checker import DependencyChecker

if __name__ == "__main__":
    print("=" * 60)
    print("  Analizador de Buenas Prácticas para UiPath")
    print("  Versión 1.2.0")
    print("  Carlos Vidal Castillejo")
    print("=" * 60)
    print()

    # Verificar dependencias
    print("Verificando dependencias...")
    checker = DependencyChecker(silent=False)
    all_ok, missing_critical, missing_ai = checker.check_all()

    # Si faltan dependencias críticas, instalarlas
    if not all_ok:
        print("\n⚠ Dependencias faltantes detectadas. Instalando...")
        if not checker.auto_install(install_ai=True):
            print("\n❌ ERROR: No se pudieron instalar las dependencias críticas")
            print("\nInstrucciones de instalación manual:")
            print(checker.get_install_instructions())
            input("\nPresiona Enter para salir...")
            sys.exit(1)
    else:
        print("✓ Todas las dependencias están instaladas")

        # Instalar bibliotecas de IA si faltan (opcional, no bloquea)
        if missing_ai:
            print("\n📦 Instalando bibliotecas de IA opcionales...")
            checker.auto_install(install_ai=True)

    print()
    print("Iniciando aplicación...")
    print()

    from src.ui.main_window import MainWindow
    app = MainWindow()
    app.run()
