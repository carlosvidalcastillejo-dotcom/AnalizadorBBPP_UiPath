import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.getcwd())

from src.rules_manager import RulesManager

def test_dependencies():
    print("="*60)
    print("TEST: Verificación de Dependencias de Sets")
    print("="*60)
    
    # Cargar rules manager
    rm = RulesManager()
    
    # Obtener dependencias del set UiPath
    print("\n1. Dependencias del set 'UiPath':")
    uipath_deps = rm.get_set_dependencies('UiPath')
    if uipath_deps:
        for pkg, ver in uipath_deps.items():
            print(f"   - {pkg}: {ver}")
    else:
        print("   ✗ No se encontraron dependencias (ERROR)")
    
    # Obtener dependencias del set NTTData
    print("\n2. Dependencias del set 'NTTData':")
    nttdata_deps = rm.get_set_dependencies('NTTData')
    if nttdata_deps:
        for pkg, ver in nttdata_deps.items():
            print(f"   - {pkg}: {ver}")
    else:
        print("   ✓ Set vacío (correcto)")
    
    # Verificar sets disponibles
    print("\n3. Sets disponibles:")
    sets_info = rm.get_sets_info()
    for set_name, info in sets_info.items():
        print(f"   - {set_name}: {info.get('name')} (enabled: {info.get('enabled')})")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_dependencies()
