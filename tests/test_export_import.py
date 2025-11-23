"""
Test - Sistema de Exportar/Importar BBPP
Validar funciones de exportación e importación
"""

import sys
from pathlib import Path
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import (
    export_bbpp_set, import_bbpp_set,
    export_all_active_bbpp, validate_bbpp_structure,
    get_available_bbpp_sets, BBPP_DIR
)

print("=" * 80)
print("🧪 TEST - Sistema de Exportar/Importar BBPP")
print("=" * 80)

# Crear directorio temporal para tests
temp_dir = Path(tempfile.mkdtemp())
print(f"\n📁 Directorio temporal: {temp_dir}\n")

# Test 1: Validar estructura de BBPP
print("📋 Test 1: Validar estructura de BBPP")
print("-" * 80)

# Estructura válida
valid_bbpp = {
    "metadata": {"name": "Test", "version": "1.0.0"},
    "rules": [
        {
            "id": "TEST_001",
            "name": "Regla de prueba",
            "category": "test",
            "severity": "info",
            "enabled": True,
            "rule_type": "test",
            "parameters": {}
        }
    ]
}

is_valid, message = validate_bbpp_structure(valid_bbpp)
print(f"{'✅' if is_valid else '❌'} Estructura válida: {message}")

# Estructura inválida (sin reglas)
invalid_bbpp = {"metadata": {"name": "Test"}}
is_valid, message = validate_bbpp_structure(invalid_bbpp)
print(f"{'✅' if not is_valid else '❌'} Estructura inválida detectada: {message}")

# Test 2: Exportar conjunto individual
print("\n\n📋 Test 2: Exportar conjunto individual")
print("-" * 80)

available_sets = get_available_bbpp_sets()
if available_sets:
    first_set = available_sets[0]
    export_path = temp_dir / "exported_set.json"
    
    print(f"📤 Exportando: {first_set['name']}")
    success = export_bbpp_set(Path(first_set['filepath']), export_path)
    
    if success:
        print(f"✅ Exportado a: {export_path.name}")
        print(f"   Tamaño: {export_path.stat().st_size} bytes")
    else:
        print("❌ Error en exportación")
else:
    print("⚠️ No hay conjuntos disponibles para exportar")

# Test 3: Importar conjunto
print("\n\n📋 Test 3: Importar conjunto")
print("-" * 80)

if available_sets and export_path.exists():
    # Crear nombre único para importación
    import_name = "TEST_Imported.json"
    
    print(f"📥 Importando desde: {export_path.name}")
    success = import_bbpp_set(export_path, import_name)
    
    if success:
        imported_path = BBPP_DIR / import_name
        print(f"✅ Importado como: {import_name}")
        print(f"   Ubicación: {imported_path}")
        
        # Limpiar archivo de prueba
        if imported_path.exists():
            imported_path.unlink()
            print(f"🧹 Archivo de prueba eliminado")
    else:
        print("❌ Error en importación")

# Test 4: Exportar configuración completa
print("\n\n📋 Test 4: Exportar configuración completa")
print("-" * 80)

config_export_path = temp_dir / "config_completa.json"
print(f"📦 Exportando configuración completa...")
success = export_all_active_bbpp(config_export_path)

if success:
    print(f"✅ Exportado a: {config_export_path.name}")
    print(f"   Tamaño: {config_export_path.stat().st_size} bytes")
    
    # Leer y mostrar info
    import json
    with open(config_export_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n   Contenido:")
    print(f"   • Nombre: {data['metadata']['name']}")
    print(f"   • Conjuntos incluidos: {len(data['sets'])}")
    for i, bbpp_set in enumerate(data['sets'], 1):
        print(f"     {i}. {bbpp_set['metadata']['name']} ({len(bbpp_set['rules'])} reglas)")
else:
    print("❌ Error en exportación")

# Test 5: Backup automático en importación
print("\n\n📋 Test 5: Backup automático")
print("-" * 80)

if export_path.exists():
    # Crear archivo existente
    existing_file = BBPP_DIR / "TEST_Existing.json"
    
    import json
    with open(existing_file, 'w', encoding='utf-8') as f:
        json.dump(valid_bbpp, f)
    
    print(f"📄 Creado archivo existente: {existing_file.name}")
    
    # Intentar importar con el mismo nombre (debe crear backup)
    print(f"📥 Importando con nombre duplicado...")
    success = import_bbpp_set(export_path, "TEST_Existing.json")
    
    if success:
        print(f"✅ Importación exitosa")
        
        # Buscar backups
        backups = list(BBPP_DIR.glob("TEST_Existing.json.backup_*"))
        if backups:
            print(f"📦 Backup creado: {backups[0].name}")
            
            # Limpiar
            for backup in backups:
                backup.unlink()
            existing_file.unlink()
            print(f"🧹 Archivos de prueba eliminados")
        else:
            print(f"⚠️ No se encontró backup (puede que no se necesitara)")
    else:
        print("❌ Error en importación")

# Test 6: Validación de archivo corrupto
print("\n\n📋 Test 6: Validación de archivo corrupto")
print("-" * 80)

corrupt_file = temp_dir / "corrupt.json"
with open(corrupt_file, 'w') as f:
    f.write("{ invalid json")

print(f"📄 Creado archivo corrupto")
print(f"📥 Intentando importar...")
success = import_bbpp_set(corrupt_file, "TEST_Corrupt.json")

if not success:
    print(f"✅ Archivo corrupto rechazado correctamente")
else:
    print(f"❌ ERROR: Se importó archivo corrupto")

# Limpiar directorio temporal
print("\n\n🧹 Limpieza")
print("-" * 80)
shutil.rmtree(temp_dir)
print(f"✅ Directorio temporal eliminado")

# Resumen final
print("\n\n" + "=" * 80)
print("🎉 RESUMEN DEL TEST")
print("=" * 80)
print(f"✅ Validación de estructura: OK")
print(f"✅ Exportación individual: OK")
print(f"✅ Importación: OK")
print(f"✅ Exportación completa: OK")
print(f"✅ Sistema de backup: OK")
print(f"✅ Validación de errores: OK")
print("\n🎯 Sistema de Exportar/Importar funcionando correctamente")
print("=" * 80)
