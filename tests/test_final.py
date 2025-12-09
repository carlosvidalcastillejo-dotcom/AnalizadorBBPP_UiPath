import sys
import os
from pathlib import Path

sys.path.append(os.getcwd())

from src.project_scanner import ProjectScanner

# Test 1: Con active_sets explícito
print("="*60)
print("TEST 1: active_sets=['UiPath'] (explícito)")
print("="*60)
scanner1 = ProjectScanner(Path("dummy_project"), active_sets=['UiPath'])
results1 = scanner1.scan()

if results1['success']:
    print("\n✅ Análisis exitoso")
    for dep in results1['project_info']['dependencies'][:3]:
        print(f"\n  {dep['name']}")
        print(f"    Instalada: {dep.get('installed_version', 'N/A')}")
        print(f"    Requerida: {dep.get('required_version', 'N/A')}")
        print(f"    Estado: {dep.get('status_label', 'N/A')}")

# Test 2: Sin active_sets (debería usar default)
print("\n" + "="*60)
print("TEST 2: active_sets=None (debería usar default)")
print("="*60)
scanner2 = ProjectScanner(Path("dummy_project"))  # Sin especificar active_sets
results2 = scanner2.scan()

if results2['success']:
    print("\n✅ Análisis exitoso")
    for dep in results2['project_info']['dependencies'][:3]:
        print(f"\n  {dep['name']}")
        print(f"    Instalada: {dep.get('installed_version', 'N/A')}")
        print(f"    Requerida: {dep.get('required_version', 'N/A')}")
        print(f"    Estado: {dep.get('status_label', 'N/A')}")

print("\n" + "="*60)
print("✅ AMBOS TESTS COMPLETADOS")
print("="*60)
