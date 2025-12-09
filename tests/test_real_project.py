"""
Script para generar un nuevo reporte con el código actualizado
"""
import sys
import os
from pathlib import Path

sys.path.append(os.getcwd())

from src.project_scanner import ProjectScanner

# Analizar RoboticEnterpriseFramework con solo UiPath
project_path = Path(r"C:\Users\Imrik\Documents\Proyectos Git\RoboticEnterpriseFramework")

if not project_path.exists():
    print(f"❌ No se encuentra el proyecto en: {project_path}")
    print("\nPor favor, actualiza la ruta en este script o ejecuta desde la aplicación.")
    sys.exit(1)

print(f"📂 Analizando: {project_path.name}")
print(f"🎯 BBPP Sets activos: ['UiPath']")
print("\n" + "="*60)

scanner = ProjectScanner(project_path, active_sets=['UiPath'])
results = scanner.scan()

if results['success']:
    print("\n✅ Análisis completado exitosamente")
    print(f"\n📊 Dependencias encontradas: {len(results['project_info']['dependencies'])}")
    
    print("\n📦 RESUMEN DE DEPENDENCIAS:")
    print("-" * 60)
    for dep in results['project_info']['dependencies']:
        installed = dep.get('installed_version', 'N/A')
        required = dep.get('required_version', 'N/A')
        status = dep.get('status_label', 'N/A')
        
        print(f"\n  {dep['name']}")
        print(f"    Instalada: {installed}")
        print(f"    Requerida: {required}")
        print(f"    Estado: {status}")
    
    print("\n" + "="*60)
    print("✅ El reporte HTML se generó automáticamente en output/HTML/")
    print("   Busca el archivo más reciente con timestamp de HOY")
else:
    print(f"\n❌ Error: {results.get('error')}")
