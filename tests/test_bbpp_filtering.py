"""
Test para verificar que el filtrado de reglas BBPP funcione correctamente
"""
import sys
from pathlib import Path

# Añadir ruta al proyecto
sys.path.insert(0, str(Path(__file__).parent))

from src.rules_manager import get_rules_manager

def test_filtering():
    rm = get_rules_manager()

    print("="*60)
    print("TEST: FILTRADO DE REGLAS BBPP")
    print("="*60)

    # Test 1: Solo UiPath
    print("\n[TEST 1] Selección: SOLO UiPath")
    print("-" * 60)
    rules_uipath = rm.get_active_rules(['UiPath'])
    print(f"Total reglas filtradas: {len(rules_uipath)}")

    # Verificar que incluya reglas exclusivas de UiPath
    exclusive_uipath = [r for r in rules_uipath if r.get('sets') == ['UiPath']]
    print(f"  - Reglas exclusivas UiPath: {len(exclusive_uipath)}")
    for r in exclusive_uipath:
        print(f"    ✓ {r['id']}: {r['name']}")

    # Verificar que incluya reglas compartidas
    shared = [r for r in rules_uipath if 'UiPath' in r.get('sets', []) and 'NTTData' in r.get('sets', [])]
    print(f"  - Reglas compartidas (UiPath + NTTData): {len(shared)}")

    # Verificar que NO incluya reglas exclusivas de NTTData
    exclusive_nttdata = [r for r in rules_uipath if r.get('sets') == ['NTTData']]
    print(f"  - Reglas exclusivas NTTData (debe ser 0): {len(exclusive_nttdata)}")
    if exclusive_nttdata:
        print("    ❌ ERROR: Se filtraron reglas exclusivas de NTTData!")
        for r in exclusive_nttdata:
            print(f"      - {r['id']}: {r['name']}")
    else:
        print("    ✓ OK: No se incluyen reglas exclusivas de NTTData")

    # Test 2: Solo NTTData
    print("\n[TEST 2] Selección: SOLO NTTData")
    print("-" * 60)
    rules_nttdata = rm.get_active_rules(['NTTData'])
    print(f"Total reglas filtradas: {len(rules_nttdata)}")

    # Verificar que incluya reglas exclusivas de NTTData
    exclusive_nttdata = [r for r in rules_nttdata if r.get('sets') == ['NTTData']]
    print(f"  - Reglas exclusivas NTTData: {len(exclusive_nttdata)}")
    for r in exclusive_nttdata:
        print(f"    ✓ {r['id']}: {r['name']}")

    # Verificar que incluya reglas compartidas
    shared = [r for r in rules_nttdata if 'UiPath' in r.get('sets', []) and 'NTTData' in r.get('sets', [])]
    print(f"  - Reglas compartidas (UiPath + NTTData): {len(shared)}")

    # Verificar que NO incluya reglas exclusivas de UiPath
    exclusive_uipath = [r for r in rules_nttdata if r.get('sets') == ['UiPath']]
    print(f"  - Reglas exclusivas UiPath (debe ser 0): {len(exclusive_uipath)}")
    if exclusive_uipath:
        print("    ❌ ERROR: Se filtraron reglas exclusivas de UiPath!")
        for r in exclusive_uipath:
            print(f"      - {r['id']}: {r['name']}")
    else:
        print("    ✓ OK: No se incluyen reglas exclusivas de UiPath")

    # Test 3: Ambos seleccionados
    print("\n[TEST 3] Selección: UiPath + NTTData")
    print("-" * 60)
    rules_both = rm.get_active_rules(['UiPath', 'NTTData'])
    print(f"Total reglas filtradas: {len(rules_both)}")
    print("  ✓ Debe incluir TODAS las reglas activas")

    # Test 4: Ninguno seleccionado (todas las activas)
    print("\n[TEST 4] Selección: Ninguno (todas activas)")
    print("-" * 60)
    rules_all = rm.get_active_rules(None)
    print(f"Total reglas filtradas: {len(rules_all)}")
    print("  ✓ Debe incluir TODAS las reglas activas")

    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE RESULTADOS")
    print("="*60)

    total_rules = len(rm.rules)
    print(f"Total reglas en BBPP_Master.json: {total_rules}")
    print(f"Solo UiPath → {len(rules_uipath)} reglas")
    print(f"Solo NTTData → {len(rules_nttdata)} reglas")
    print(f"Ambos → {len(rules_both)} reglas")
    print(f"Todas → {len(rules_all)} reglas")

    # Validación final
    print("\n" + "="*60)
    print("VALIDACIÓN")
    print("="*60)

    success = True

    # 1. UiPath no debe tener reglas exclusivas de NTTData
    if any(r.get('sets') == ['NTTData'] for r in rules_uipath):
        print("❌ FALLO: UiPath incluye reglas exclusivas de NTTData")
        success = False
    else:
        print("✓ PASS: UiPath NO incluye reglas exclusivas de NTTData")

    # 2. NTTData no debe tener reglas exclusivas de UiPath
    if any(r.get('sets') == ['UiPath'] for r in rules_nttdata):
        print("❌ FALLO: NTTData incluye reglas exclusivas de UiPath")
        success = False
    else:
        print("✓ PASS: NTTData NO incluye reglas exclusivas de UiPath")

    # 3. Ambos debe tener todas las reglas
    if len(rules_both) != total_rules:
        print(f"⚠ WARNING: Se esperaban {total_rules} reglas, se obtuvieron {len(rules_both)}")
    else:
        print(f"✓ PASS: Ambos conjuntos incluyen todas las reglas ({total_rules})")

    print("\n" + "="*60)
    if success:
        print("✅ TODOS LOS TESTS PASARON CORRECTAMENTE")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
    print("="*60)

if __name__ == '__main__':
    test_filtering()
