import sys
import os
from datetime import datetime
from pathlib import Path

# Asegurar que estamos en root
os.chdir(Path(__file__).parent)

# Importar funciones de build.py
from build import (
    update_config_file, create_build_info, update_changelog_file, 
    compile_with_pyinstaller
)
from src.change_detector import get_change_summary
from src.version_manager import get_current_version, suggest_version_bump

def automated_build():
    print("🚀 INICIANDO BUILD AUTOMATIZADO")
    print("=================================")
    
    # 1. Configuración
    autor = "Carlos Vidal Castillejo"
    
    # Detectar nueva versión (Patch)
    config_path = Path('src/config.py')
    current_version = get_current_version(config_path)
    suggestions = suggest_version_bump(current_version)
    new_version = suggestions['patch']
    
    print(f"ℹ️  Versión: {current_version} -> {new_version}")
    
    # Generar changelog
    try:
        summary = get_change_summary(Path('.'), hours=48)
        changelog_desc = summary['description']
        if not changelog_desc:
            changelog_desc = "Mejoras generales y correcciones de bugs."
    except Exception as e:
        print(f"Warning changelog: {e}")
        changelog_desc = "Actualización automática."
    
    config = {
        'autor': autor,
        'version': new_version,
        'version_type': 'Beta',
        'build_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'build_date_short': datetime.now().strftime("%Y-%m-%d"),
        'bump_type': 'patch',
        'changelog_description': changelog_desc
    }
    
    # 2. Actualizar archivos
    print("\n📝 Actualizando archivos de versión...")
    update_config_file(config)
    update_changelog_file(config)
    create_build_info()
    
    # 3. Compilar App Principal
    print("\n🔨 Compilando Aplicación Principal...")
    success = compile_with_pyinstaller()
    
    if success:
        print("\n✅ Build de Aplicación completado.")
    else:
        print("\n❌ Falló el build de Aplicación.")
        sys.exit(1)
        
    print("\n🚀 BUILD FINALIZADO EXITOSAMENTE")

if __name__ == "__main__":
    automated_build()
