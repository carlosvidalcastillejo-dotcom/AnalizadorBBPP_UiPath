"""
Test para validar NOMENCLATURA_001 - Variables en camelCase
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analyzer import BBPPAnalyzer


def test_nomenclatura_001_camel_case():
    """Verificar que NOMENCLATURA_001 valida camelCase correctamente"""
    print("\n" + "=" * 70)
    print("TEST: NOMENCLATURA_001 - Variables en camelCase")
    print("=" * 70)
    
    test_data = {
        'file_path': '/test/Main.xaml',
        'workflow_type': 'Sequence',
        'variables': [
            {'name': 'myVariable'},      # ✅ Válido
            {'name': 'userName'},         # ✅ Válido
            {'name': 'data123'},          # ✅ Válido
            {'name': 'MyVariable'},       # ❌ Inválido (empieza con mayúscula)
            {'name': 'MYVARIABLE'},       # ❌ Inválido (todo mayúsculas)
            {'name': 'my_variable'},      # ❌ Inválido (snake_case)
            {'name': '_temp'},            # ❌ Inválido (empieza con _)
            {'name': 'x'},                # ✅ Válido (muy corto, se ignora)
        ],
        'arguments': [],
        'activities': [],
        'log_messages': [],
        'activity_count': 0
    }
    
    analyzer = BBPPAnalyzer()
    findings = analyzer.analyze(test_data)
    
    naming_findings = [f for f in findings if f.rule_id == 'NOMENCLATURA_001']
    
    print(f"\n📊 Variables analizadas: 8")
    print(f"   Hallazgos detectados: {len(naming_findings)}")
    
    # Debería detectar 4 errores: MyVariable, MYVARIABLE, my_variable, _temp
    expected_errors = 4
    
    if len(naming_findings) == expected_errors:
        print(f"   ✅ CORRECTO - Detectó {expected_errors} variables incorrectas")
        
        print(f"\n   Variables incorrectas detectadas:")
        for finding in naming_findings:
            var_name = finding.details.get('variable_name')
            suggestion = finding.details.get('suggestion', '')
            print(f"   - {var_name} → {suggestion}")
        
        return True
    else:
        print(f"   ❌ ERROR - Esperado: {expected_errors}, Detectado: {len(naming_findings)}")
        print(f"\n   Detalles:")
        for finding in naming_findings:
            print(f"   - {finding.details.get('variable_name')}")
        return False


def test_nomenclatura_001_edge_cases():
    """Verificar casos especiales"""
    print("\n" + "=" * 70)
    print("TEST: NOMENCLATURA_001 - Casos Especiales")
    print("=" * 70)
    
    test_data = {
        'file_path': '/test/Main.xaml',
        'workflow_type': 'Sequence',
        'variables': [
            {'name': 'myVar123'},         # ✅ Con números
            {'name': 'isValid'},          # ✅ Prefijo 'is'
            {'name': 'hasData'},          # ✅ Prefijo 'has'
            {'name': 'myVarTemp'},        # ✅ Múltiples palabras
        ],
        'arguments': [],
        'activities': [],
        'log_messages': [],
        'activity_count': 0
    }
    
    analyzer = BBPPAnalyzer()
    findings = analyzer.analyze(test_data)
    
    naming_findings = [f for f in findings if f.rule_id == 'NOMENCLATURA_001']
    
    print(f"\n📊 Variables válidas analizadas: 4")
    print(f"   Hallazgos: {len(naming_findings)}")
    
    if len(naming_findings) == 0:
        print(f"   ✅ CORRECTO - Todas las variables válidas aceptadas")
        return True
    else:
        print(f"   ❌ ERROR - Se reportaron errores en variables válidas:")
        for finding in naming_findings:
            print(f"   - {finding.details.get('variable_name')}")
        return False


if __name__ == "__main__":
    print("\n" + "🧪" * 35)
    print("   TESTS DE VALIDACIÓN - NOMENCLATURA_001")
    print("🧪" * 35)
    
    results = []
    results.append(("Validación camelCase", test_nomenclatura_001_camel_case()))
    results.append(("Casos Especiales", test_nomenclatura_001_edge_cases()))
    
    print("\n" + "=" * 70)
    print("RESUMEN FINAL:")
    print("=" * 70)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + ("✅ TODOS LOS TESTS PASARON" if all_passed else "❌ ALGUNOS TESTS FALLARON"))
    print("=" * 70)
