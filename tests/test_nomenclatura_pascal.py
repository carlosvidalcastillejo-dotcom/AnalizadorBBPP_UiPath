"""
Test simplificado y corregido para verificar las nuevas reglas de nomenclatura
"""
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from analyzer import BBPPAnalyzer
from rules_manager import get_rules_manager

def test_pascal_case():
    """Test de validación PascalCase"""
    print("\n" + "="*60)
    print("TEST: Validación de PascalCase en Variables")
    print("="*60)
    
    # Cargar reglas
    rules_manager = get_rules_manager()
    
    # Activar temporalmente NOMENCLATURA_005
    rules_manager.update_rule('NOMENCLATURA_005', {'enabled': True})
    rules_manager.update_rule('NOMENCLATURA_001', {'enabled': False})
    
    # Obtener reglas activas
    rules = rules_manager.get_active_rules(['UiPath', 'NTTData'])
    
    # Crear analyzer
    analyzer = BBPPAnalyzer(rules=rules, active_sets=['UiPath', 'NTTData'])
    
    # Datos de prueba
    test_data = {
        'file_path': 'test.xaml',
        'variables': [
            {'name': 'MyVariable'},      # ✅ Válido PascalCase
            {'name': 'UserName'},        # ✅ Válido PascalCase
            {'name': 'myVariable'},      # ❌ Inválido (camelCase)
        ],
        'arguments': []
    }
    
    # Analizar
    findings = analyzer.analyze(test_data)
    
    # Filtrar solo hallazgos de NOMENCLATURA_005
    pascal_findings = [f for f in findings if f.rule_id == 'NOMENCLATURA_005']
    
    print(f"\n📊 Hallazgos de PascalCase: {len(pascal_findings)}")
    
    for finding in pascal_findings:
        print(f"\n  ❌ Variable: {finding.details.get('variable_name')}")
        print(f"     Sugerencia: {finding.details.get('suggestion')}")
    
    # Restaurar estado
    rules_manager.update_rule('NOMENCLATURA_005', {'enabled': False})
    rules_manager.update_rule('NOMENCLATURA_001', {'enabled': True})
    rules_manager.save_rules()
    
    print(f"\n✅ Test completado: {len(pascal_findings)} hallazgos (esperado: 1)")
    return len(pascal_findings) == 1

def test_camel_case():
    """Test de validación camelCase"""
    print("\n" + "="*60)
    print("TEST: Validación de camelCase en Variables")
    print("="*60)
    
    # Cargar reglas
    rules_manager = get_rules_manager()
    
    # Obtener reglas activas (camelCase ya está activo por defecto)
    rules = rules_manager.get_active_rules(['UiPath', 'NTTData'])
    
    # Crear analyzer
    analyzer = BBPPAnalyzer(rules=rules, active_sets=['UiPath', 'NTTData'])
    
    # Datos de prueba
    test_data = {
        'file_path': 'test.xaml',
        'variables': [
            {'name': 'myVariable'},      # ✅ Válido camelCase
            {'name': 'userName'},        # ✅ Válido camelCase
            {'name': 'MyVariable'},      # ❌ Inválido (PascalCase)
        ],
        'arguments': []
    }
    
    # Analizar
    findings = analyzer.analyze(test_data)
    
    # Filtrar solo hallazgos de NOMENCLATURA_001
    camel_findings = [f for f in findings if f.rule_id == 'NOMENCLATURA_001']
    
    print(f"\n📊 Hallazgos de camelCase: {len(camel_findings)}")
    
    for finding in camel_findings:
        print(f"\n  ❌ Variable: {finding.details.get('variable_name')}")
        print(f"     Sugerencia: {finding.details.get('suggestion')}")
    
    print(f"\n✅ Test completado: {len(camel_findings)} hallazgos (esperado: 1)")
    return len(camel_findings) == 1

def test_arguments():
    """Test de validación de formato en argumentos"""
    print("\n" + "="*60)
    print("TEST: Validación de Formato en Argumentos (camelCase)")
    print("="*60)
    
    # Cargar reglas
    rules_manager = get_rules_manager()
    
    # Obtener reglas activas
    rules = rules_manager.get_active_rules(['UiPath', 'NTTData'])
    
    # Crear analyzer
    analyzer = BBPPAnalyzer(rules=rules, active_sets=['UiPath', 'NTTData'])
    
    # Datos de prueba
    test_data = {
        'file_path': 'test.xaml',
        'variables': [],
        'arguments': [
            {'name': 'in_myArgument', 'direction': 'In', 'annotation': 'Test argument'},      # ✅ Válido (in_ + camelCase)
            {'name': 'in_MyArgument', 'direction': 'In', 'annotation': 'Test argument'},      # ❌ Inválido (PascalCase)
            {'name': 'myArgument', 'direction': 'In', 'annotation': 'Test argument'},         # ❌ Inválido (falta prefijo)
        ]
    }
    
    # Analizar
    findings = analyzer.analyze(test_data)
    
    # Filtrar solo hallazgos de NOMENCLATURA_003
    prefix_findings = [f for f in findings if f.rule_id == 'NOMENCLATURA_003']
    
    print(f"\n📊 Hallazgos de prefijos: {len(prefix_findings)}")
    
    for finding in prefix_findings:
        print(f"\n  ❌ Argumento: {finding.details.get('argument_name')}")
        print(f"     Problema: {finding.details.get('issue', 'Falta prefijo')}")
        if 'suggestion' in finding.details:
            print(f"     Sugerencia: {finding.details.get('suggestion')}")
    
    print(f"\n✅ Test completado: {len(prefix_findings)} hallazgos (esperado: 2)")
    return len(prefix_findings) == 2

def main():
    """Ejecutar todos los tests"""
    print("\n🧪 TESTS DE NOMENCLATURA - PascalCase y camelCase")
    print("="*60)
    
    results = []
    
    try:
        result1 = test_pascal_case()
        results.append(("PascalCase", result1))
    except Exception as e:
        print(f"\n❌ Error en Test PascalCase: {e}")
        import traceback
        traceback.print_exc()
        results.append(("PascalCase", False))
    
    try:
        result2 = test_camel_case()
        results.append(("camelCase", result2))
    except Exception as e:
        print(f"\n❌ Error en Test camelCase: {e}")
        import traceback
        traceback.print_exc()
        results.append(("camelCase", False))
    
    try:
        result3 = test_arguments()
        results.append(("Argumentos", result3))
    except Exception as e:
        print(f"\n❌ Error en Test Argumentos: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Argumentos", False))
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE TESTS")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 ¡Todos los tests pasaron correctamente!")
        print("\n📝 Resumen de funcionalidades implementadas:")
        print("   ✅ NOMENCLATURA_001: Variables en camelCase")
        print("   ✅ NOMENCLATURA_005: Variables en PascalCase (nueva)")
        print("   ✅ NOMENCLATURA_003: Argumentos con prefijos + formato")
        print("\n💡 Configuración:")
        print("   - Variables: Activar camelCase O PascalCase (no ambas)")
        print("   - Argumentos: in_camelCase o in_PascalCase según config")
    else:
        print("\n⚠️  Algunos tests fallaron. Revisar implementación.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
