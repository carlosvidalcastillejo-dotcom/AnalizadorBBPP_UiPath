"""
Verificador y auto-instalador de dependencias
Se ejecuta automáticamente al iniciar la aplicación
"""
import sys
import subprocess
import importlib.util
from pathlib import Path
from typing import List, Tuple


class DependencyChecker:
    """Verifica e instala dependencias automáticamente"""

    # Lista de dependencias críticas (módulo, nombre_paquete_pip)
    CRITICAL_DEPENDENCIES = [
        ('packaging', 'packaging>=21.0'),
        ('openpyxl', 'openpyxl>=3.0.0'),
        ('PIL', 'Pillow>=9.0.0'),
    ]

    # Bibliotecas de IA (opcionales pero recomendadas)
    AI_DEPENDENCIES = [
        ('google.generativeai', 'google-generativeai>=0.3.0'),
        ('openai', 'openai>=1.0.0'),
        ('anthropic', 'anthropic>=0.7.0'),
    ]

    def __init__(self, silent: bool = False):
        """
        Args:
            silent: Si es True, no muestra mensajes en consola
        """
        self.silent = silent
        self.missing_critical = []
        self.missing_ai = []

    def _log(self, message: str):
        """Log mensaje si no está en modo silencioso"""
        if not self.silent:
            print(message)

    def check_module(self, module_name: str) -> bool:
        """
        Verifica si un módulo está instalado

        Args:
            module_name: Nombre del módulo a verificar

        Returns:
            True si está instalado
        """
        return importlib.util.find_spec(module_name) is not None

    def check_all(self) -> Tuple[bool, List[str], List[str]]:
        """
        Verifica todas las dependencias

        Returns:
            (all_ok, missing_critical, missing_ai)
        """
        self.missing_critical = []
        self.missing_ai = []

        # Verificar dependencias críticas
        for module_name, pip_package in self.CRITICAL_DEPENDENCIES:
            if not self.check_module(module_name):
                self.missing_critical.append(pip_package)

        # Verificar dependencias de IA
        for module_name, pip_package in self.AI_DEPENDENCIES:
            if not self.check_module(module_name):
                self.missing_ai.append(pip_package)

        all_ok = len(self.missing_critical) == 0

        return all_ok, self.missing_critical, self.missing_ai

    def install_package(self, package: str) -> bool:
        """
        Instala un paquete usando pip

        Args:
            package: Nombre del paquete a instalar

        Returns:
            True si se instaló correctamente
        """
        try:
            self._log(f"  Instalando {package}...")

            process = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", package],
                check=True,
                capture_output=True,
                text=True,
                timeout=120
            )

            self._log(f"  ✓ {package} instalado")
            return True

        except subprocess.CalledProcessError as e:
            self._log(f"  ✗ Error instalando {package}: {e.stderr}")
            return False
        except subprocess.TimeoutExpired:
            self._log(f"  ✗ Timeout instalando {package}")
            return False
        except Exception as e:
            self._log(f"  ✗ Error inesperado: {e}")
            return False

    def auto_install(self, install_ai: bool = True) -> bool:
        """
        Instala automáticamente las dependencias faltantes

        Args:
            install_ai: Si es True, también instala bibliotecas de IA

        Returns:
            True si todas las dependencias críticas se instalaron
        """
        all_ok, missing_critical, missing_ai = self.check_all()

        if all_ok and (not install_ai or len(missing_ai) == 0):
            self._log("✓ Todas las dependencias están instaladas")
            return True

        # Instalar dependencias críticas
        if missing_critical:
            self._log("\n⚠ Instalando dependencias críticas faltantes...")
            for package in missing_critical:
                if not self.install_package(package):
                    self._log(f"\n❌ Error: No se pudo instalar {package}")
                    return False

        # Instalar dependencias de IA si se solicita
        if install_ai and missing_ai:
            self._log("\n📦 Instalando bibliotecas de IA...")
            for package in missing_ai:
                self.install_package(package)  # No falla si estas fallan

        # Verificar de nuevo
        all_ok, _, _ = self.check_all()

        if all_ok:
            self._log("\n✅ Todas las dependencias críticas instaladas correctamente")
        else:
            self._log("\n❌ Algunas dependencias críticas no se pudieron instalar")

        return all_ok

    def get_install_instructions(self) -> str:
        """
        Genera instrucciones de instalación manual

        Returns:
            String con instrucciones
        """
        all_ok, missing_critical, missing_ai = self.check_all()

        if all_ok:
            return "Todas las dependencias están instaladas."

        instructions = []

        if missing_critical:
            instructions.append("DEPENDENCIAS CRÍTICAS FALTANTES:")
            instructions.append("")
            for package in missing_critical:
                instructions.append(f"  • {package}")
            instructions.append("")
            instructions.append("Para instalarlas, ejecuta:")
            instructions.append(f"  {sys.executable} -m pip install " + " ".join(missing_critical))
            instructions.append("")
            instructions.append("O ejecuta el script de instalación:")
            instructions.append("  install_dependencies.bat (Windows)")
            instructions.append("  python install_dependencies.py (Multiplataforma)")

        if missing_ai:
            instructions.append("")
            instructions.append("BIBLIOTECAS DE IA OPCIONALES (para prompts especializados):")
            instructions.append("")
            for package in missing_ai:
                instructions.append(f"  • {package}")
            instructions.append("")
            instructions.append("Para instalarlas:")
            instructions.append(f"  {sys.executable} -m pip install " + " ".join(missing_ai))

        return "\n".join(instructions)


def check_and_install_dependencies(silent: bool = False, install_ai: bool = True) -> bool:
    """
    Función de conveniencia para verificar e instalar dependencias

    Args:
        silent: Si es True, no muestra mensajes
        install_ai: Si es True, también instala bibliotecas de IA

    Returns:
        True si todas las dependencias críticas están instaladas
    """
    checker = DependencyChecker(silent=silent)
    return checker.auto_install(install_ai=install_ai)


if __name__ == "__main__":
    # Test del checker
    print("="*60)
    print("VERIFICADOR DE DEPENDENCIAS - Analizador BBPP UiPath")
    print("="*60)
    print()

    checker = DependencyChecker(silent=False)

    # Verificar estado
    all_ok, missing_critical, missing_ai = checker.check_all()

    if all_ok:
        print("✅ Todas las dependencias críticas están instaladas")
    else:
        print("❌ Faltan dependencias críticas:")
        for pkg in missing_critical:
            print(f"  • {pkg}")

    if missing_ai:
        print("\n⚠ Bibliotecas de IA opcionales faltantes:")
        for pkg in missing_ai:
            print(f"  • {pkg}")

    if not all_ok:
        print("\n" + "="*60)
        print(checker.get_install_instructions())
        print("="*60)

        # Preguntar si instalar
        response = input("\n¿Deseas instalar las dependencias ahora? (S/n): ")
        if response.lower() != 'n':
            checker.auto_install(install_ai=True)
