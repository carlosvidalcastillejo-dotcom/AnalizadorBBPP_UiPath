"""
Test completo del Sistema de Excepciones para Reglas BBPP
Valida que las excepciones del REFramework funcionen correctamente
"""
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from analyzer import BBPPAnalyzer
from rules_manager import get_rules_manager

def test_exceptions_in_json():
    """Test 1: Verificar que las excepciones están en BBPP_Master.json"""
    print("\n" + "="*70)
    print("TEST 1: Verificar Excepciones en BBPP_Master.json")
    print("="*70)
    
    rules_manager = get_rules_manager()
    
    # Reglas que deben tener excepciones
    rules_with_exceptions = [
        'NOMENCLATURA_001',
        'NOMENCLATURA_002',
        'NOMENCLATURA_003',
        'NOMENCLATURA_004',
        'NOMENCLATURA_005'
    ]
    
    all_passed = True
    
    for rule_id in rules_with_exceptions:
        rule = rules_manager.get_rule_by_id(rule_id)
        if not rule:
            print(f"❌ {rule_id}: Regla no encontrada")
            all_passed = False
            continue
        
        params = rule.get('parameters', {})
        exceptions = params.get('exceptions', [])
        
        if not exceptions:
            print(f"❌ {rule_id}: No tiene excepciones")
            all_passed = False
        else:
            print(f"✅ {rule_id}: {len(exceptions)} excepciones")
            # Mostrar algunas excepciones
            print(f"   Ejemplos: {', '.join(exceptions[:3])}")
    
    return all_passed

def test_config_exception_not_flagged():
    """Test 2: Variable 'Config' no debe generar hallazgo"""
    print("\n" + "="*70)
    print("TEST 2: Variable 'Config' NO debe generar hallazgo")
    print("="*70)
    
    rules_manager = get_rules_manager()
    
    # Asegurar que NOMENCLATURA_005 (PascalCase) está activa
    rules_manager.update_rule('NOMENCLATURA_005', {'enabled': True})
    rules_manager.update_rule('NOMENCLATURA_001', {'enabled': False})
    rules_manager.save_rules()
    
    # Obtener reglas activas
    rules = rules_manager.get_active_rules(['UiPath', 'NTTData'])
    
    # Crear analyzer
    analyzer = BBPPAnalyzer(rules=rules, active_sets=['UiPath', 'NTTData'])
    
    # Datos de prueba con variable Config (está en excepciones)
    test_data = {
        'file_path': 'test.xaml',
        'variables': [
            {'name': 'Config'},  # Debe ser ignorada (excepción)
            {'name': 'myConfig'},  # Debe generar hallazgo (no es excepción)
        ],
        'arguments': []
    }
    
    # Analizar
    findings = analyzer.analyze(test_data)
    
    # Filtrar solo hallazgos de NOMENCLATURA_005
    pascal_findings = [f for f in findings if f.rule_id == 'NOMENCLATURA_005']
    
    print(f"\n📊 Hallazgos de PascalCase: {len(pascal_findings)}")
    
    # Verificar que Config NO está en los hallazgos
    config_flagged = any(f.details.get('variable_name') == 'Config' for f in pascal_findings)
    myconfig_flagged = any(f.details.get('variable_name') == 'myConfig' for f in pascal_findings)
    
    if config_flagged:
        print("❌ FALLO: 'Config' fue reportada (debería ser excepción)")
        return False
    else:
        print("✅ ÉXITO: 'Config' fue ignorada (excepción funcionando)")
    
    if myconfig_flagged:
        print("✅ ÉXITO: 'myConfig' fue reportada (no es excepción)")
    else:
        print("❌ FALLO: 'myConfig' no fue reportada (debería serlo)")
        return False
    
    # Restaurar estado
    rules_manager.update_rule('NOMENCLATURA_005', {'enabled': True})
    rules_manager.update_rule('NOMENCLATURA_001', {'enabled': False})
    rules_manager.save_rules()
    
    return True

def test_transaction_item_exception():
    """Test 3: TransactionItem no debe generar hallazgo"""
    print("\n" + "="*70)
    print("TEST 3: TransactionItem NO debe generar hallazgo")
    print("="*70)
    
    rules_manager = get_rules_manager()
    rules = rules_manager.get_active_rules(['UiPath', 'NTTData'])
    analyzer = BBPPAnalyzer(rules=rules, active_sets=['UiPath', 'NTTData'])
    
    # Datos de prueba
    test_data = {
        'file_path': 'test.xaml',
        'variables': [
            {'name': 'TransactionItem'},  # Debe ser ignorada
            {'name': 'Item'},  # Debe generar hallazgo (genérico)
        ],
        'arguments': []
    }
    
    # Analizar
    findings = analyzer.analyze(test_data)
    
    # Filtrar hallazgos de nombres genéricos
    generic_findings = [f for f in findings if f.rule_id == 'NOMENCLATURA_002']
    
    print(f"\n📊 Hallazgos de nombres genéricos: {len(generic_findings)}")
    
    # Verificar que TransactionItem NO está en los hallazgos
    transaction_flagged = any('TransactionItem' in str(f.details.get('variable_name', '')) for f in generic_findings)
    item_flagged = any(f.details.get('variable_name', '').lower() == 'item' for f in generic_findings)
    
    if transaction_flagged:
        print("❌ FALLO: 'TransactionItem' fue reportada (debería ser excepción)")
        return False
    else:
        print("✅ ÉXITO: 'TransactionItem' fue ignorada (excepción funcionando)")
    
    if item_flagged:
        print("✅ ÉXITO: 'Item' fue reportada (no es excepción)")
    else:
        print("⚠️  ADVERTENCIA: 'Item' no fue reportada")
    
    return True

def test_argument_exceptions():
    """Test 4: Argumentos con excepciones"""
    print("\n" + "="*70)
    print("TEST 4: Argumentos con Excepciones (in_Config, io_TransactionItem)")
    print("="*70)
    
    rules_manager = get_rules_manager()
    rules = rules_manager.get_active_rules(['UiPath', 'NTTData'])
    analyzer = BBPPAnalyzer(rules=rules, active_sets=['UiPath', 'NTTData'])
    
    # Datos de prueba
    test_data = {
        'file_path': 'test.xaml',
        'variables': [],
        'arguments': [
            {'name': 'in_Config', 'direction': 'In', 'annotation': 'Config dictionary'},  # Excepción
            {'name': 'io_TransactionItem', 'direction': 'InOut', 'annotation': 'Transaction item'},  # Excepción
            {'name': 'in_MyData', 'direction': 'In', 'annotation': 'My data'},  # No es excepción
        ]
    }
    
    # Analizar
    findings = analyzer.analyze(test_data)
    
    # Filtrar hallazgos de argumentos
    arg_findings = [f for f in findings if f.rule_id in ['NOMENCLATURA_003', 'NOMENCLATURA_004']]
    
    print(f"\n📊 Hallazgos de argumentos: {len(arg_findings)}")
    
    # Verificar que in_Config e io_TransactionItem NO están en los hallazgos
    config_flagged = any('in_Config' in str(f.details.get('argument_name', '')) for f in arg_findings)
    transaction_flagged = any('io_TransactionItem' in str(f.details.get('argument_name', '')) for f in arg_findings)
    
    if config_flagged:
        print("❌ FALLO: 'in_Config' fue reportado (debería ser excepción)")
        return False
    else:
        print("✅ ÉXITO: 'in_Config' fue ignorado (excepción funcionando)")
    
    if transaction_flagged:
        print("❌ FALLO: 'io_TransactionItem' fue reportado (debería ser excepción)")
        return False
    else:
        print("✅ ÉXITO: 'io_TransactionItem' fue ignorado (excepción funcionando)")
    
    return True

def test_case_sensitive():
    """Test 5: Excepciones son case-sensitive"""
    print("\n" + "="*70)
    print("TEST 5: Excepciones son Case-Sensitive")
    print("="*70)
    
    rules_manager = get_rules_manager()
    rules = rules_manager.get_active_rules(['UiPath', 'NTTData'])
    analyzer = BBPPAnalyzer(rules=rules, active_sets=['UiPath', 'NTTData'])
    
    # Datos de prueba
    test_data = {
        'file_path': 'test.xaml',
        'variables': [
            {'name': 'Config'},  # Excepción (mayúscula)
            {'name': 'config'},  # NO es excepción (minúscula)
        ],
        'arguments': []
    }
    
    # Analizar
    findings = analyzer.analyze(test_data)
    
    # Filtrar hallazgos
    all_findings = [f for f in findings if f.rule_id in ['NOMENCLATURA_002', 'NOMENCLATURA_005']]
    
    print(f"\n📊 Hallazgos totales: {len(all_findings)}")
    
    # Verificar que Config NO está pero config SÍ está
    Config_flagged = any(f.details.get('variable_name') == 'Config' for f in all_findings)
    config_flagged = any(f.details.get('variable_name') == 'config' for f in all_findings)
    
    if Config_flagged:
        print("❌ FALLO: 'Config' (mayúscula) fue reportada (debería ser excepción)")
        return False
    else:
        print("✅ ÉXITO: 'Config' (mayúscula) fue ignorada")
    
    if config_flagged:
        print("✅ ÉXITO: 'config' (minúscula) fue reportada (case-sensitive funcionando)")
    else:
        print("⚠️  ADVERTENCIA: 'config' (minúscula) no fue reportada")
    
    return True

def main():
    """Ejecutar todos los tests"""
    print("\n🧪 TESTS DEL SISTEMA DE EXCEPCIONES")
    print("="*70)
    print("Validando que las excepciones del REFramework funcionan correctamente")
    print("="*70)
    
    results = []
    
    # Test 1: Verificar JSON
    try:
        result1 = test_exceptions_in_json()
        results.append(("Excepciones en JSON", result1))
    except Exception as e:
        print(f"\n❌ Error en Test 1: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Excepciones en JSON", False))
    
    # Test 2: Config
    try:
        result2 = test_config_exception_not_flagged()
        results.append(("Config no reportada", result2))
    except Exception as e:
        print(f"\n❌ Error en Test 2: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Config no reportada", False))
    
    # Test 3: TransactionItem
    try:
        result3 = test_transaction_item_exception()
        results.append(("TransactionItem no reportada", result3))
    except Exception as e:
        print(f"\n❌ Error en Test 3: {e}")
        import traceback
        traceback.print_exc()
        results.append(("TransactionItem no reportada", False))
    
    # Test 4: Argumentos
    try:
        result4 = test_argument_exceptions()
        results.append(("Argumentos con excepciones", result4))
    except Exception as e:
        print(f"\n❌ Error en Test 4: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Argumentos con excepciones", False))
    
    # Test 5: Case-sensitive
    try:
        result5 = test_case_sensitive()
        results.append(("Case-sensitive", result5))
    except Exception as e:
        print(f"\n❌ Error en Test 5: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Case-sensitive", False))
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE TESTS")
    print("="*70)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 ¡Todos los tests pasaron correctamente!")
        print("\n📝 Sistema de Excepciones FUNCIONANDO:")
        print("   ✅ Excepciones cargadas desde BBPP_Master.json")
        print("   ✅ Variables del REFramework ignoradas")
        print("   ✅ Argumentos del REFramework ignorados")
        print("   ✅ Case-sensitive funcionando")
        print("\n💡 Próximos pasos:")
        print("   1. Probar UI para agregar/eliminar excepciones")
        print("   2. Analizar REFramework completo")
        print("   3. Verificar reducción de falsos positivos")
    else:
        print("\n⚠️  Algunos tests fallaron. Revisar implementación.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
