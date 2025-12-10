"""
Script para instalar dependencias del Analizador BBPP UiPath
Se ejecuta automáticamente durante la instalación o manualmente si es necesario
"""
import sys
import subprocess
import os

def print_separator():
    print("=" * 60)

def check_python_version():
    """Verifica que la versión de Python sea compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("ERROR: Se requiere Python 3.8 o superior")
        print(f"Versión actual: {sys.version}")
        return False
    return True

def install_dependencies():
    """Instala las dependencias necesarias"""
    print_separator()
    print("INSTALADOR DE DEPENDENCIAS - Analizador BBPP UiPath")
    print_separator()
    print()

    # Verificar versión de Python
    print("[1/5] Verificando versión de Python...")
    if not check_python_version():
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print()

    # Actualizar pip
    print("[2/5] Actualizando pip...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            capture_output=True
        )
        print("✓ pip actualizado")
    except subprocess.CalledProcessError as e:
        print(f"⚠ Warning: No se pudo actualizar pip: {e}")
    print()

    # Lista de dependencias críticas
    critical_deps = [
        "packaging>=21.0",
        "openpyxl>=3.0.0",
        "Pillow>=9.0.0"
    ]

    # Instalar dependencias desde requirements.txt si existe
    requirements_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_file):
        print("[3/5] Instalando desde requirements.txt...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", requirements_file],
                check=True
            )
            print("✓ Dependencias de requirements.txt instaladas")
        except subprocess.CalledProcessError as e:
            print(f"⚠ Error instalando desde requirements.txt: {e}")
    else:
        print("[3/5] requirements.txt no encontrado, saltando...")
    print()

    # Instalar dependencias críticas
    print("[4/5] Instalando dependencias críticas...")
    for dep in critical_deps:
        try:
            print(f"  Instalando {dep}...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", dep],
                check=True,
                capture_output=True
            )
            print(f"  ✓ {dep} instalado")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Error instalando {dep}: {e}")
            return False
    print()

    # Verificar instalación
    print("[5/5] Verificando instalación...")
    try:
        import packaging
        import openpyxl
        import PIL
        print("✓ Todas las dependencias están instaladas correctamente")
        print()
        print_separator()
        print("INSTALACIÓN COMPLETADA EXITOSAMENTE")
        print_separator()
        return True
    except ImportError as e:
        print(f"✗ Error: Falta dependencia: {e}")
        return False

if __name__ == "__main__":
    try:
        success = install_dependencies()
        if not success:
            print()
            print("ERROR: La instalación de dependencias falló")
            input("Presiona Enter para salir...")
            sys.exit(1)
        else:
            print()
            print("Puedes cerrar esta ventana y ejecutar el Analizador BBPP.")
            input("Presiona Enter para salir...")
            sys.exit(0)
    except Exception as e:
        print(f"ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        input("Presiona Enter para salir...")
        sys.exit(1)
