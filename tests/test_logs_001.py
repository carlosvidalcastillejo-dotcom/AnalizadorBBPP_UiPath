"""
Test específico para validar la regla LOGS_001 mejorada
Verifica que el cálculo de ratio de logs por actividades funcione correctamente
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analyzer import BBPPAnalyzer
from src.rules_manager import get_rules_manager


def test_logs_001_ratio_calculation():
    """Verificar que LOGS_001 calcula ratio correctamente"""
    print("\n" + "=" * 70)
    print("TEST: LOGS_001 - Ratio de Logs por Actividades")
    print("=" * 70)
    
    # Caso 1: 50 actividades, 2 logs = ratio 25 (debería fallar con max=10)
    test_data_bad = {
        'file_path': '/test/Main.xaml',
        'workflow_type': 'Sequence',
        'variables': [],
        'arguments': [],
        'activities': [{'type': 'Assign', 'name': f'Act{i}'} for i in range(50)],
        'log_messages': [
            {'message': 'Log inicio'},
            {'message': 'Log fin'}
        ],
        'activity_count': 50
    }
    
    analyzer = BBPPAnalyzer()
    findings = analyzer.analyze(test_data_bad)
    
    logs_findings = [f for f in findings if f.rule_id == 'LOGS_001']
    
    print(f"\n📊 Caso 1: 50 actividades, 2 logs")
    print(f"   Ratio esperado: 25.0 actividades/log")
    print(f"   Máximo permitido: 10")
    print(f"   Hallazgos: {len(logs_findings)}")
    
    if len(logs_findings) > 0:
        print(f"   ✅ DETECTADO - Ratio: {logs_findings[0].details.get('actual_ratio')}")
        print(f"   Mensaje: {logs_findings[0].details.get('suggestion')}")
    else:
        print(f"   ❌ ERROR - No se detectó logging insuficiente")
        return False
    
    # Caso 2: 20 actividades, 3 logs = ratio 6.67 (debería pasar con max=10)
    test_data_good = {
        'file_path': '/test/Main.xaml',
        'workflow_type': 'Sequence',
        'variables': [],
        'arguments': [],
        'activities': [{'type': 'Assign', 'name': f'Act{i}'} for i in range(20)],
        'log_messages': [
            {'message': 'Log 1'},
            {'message': 'Log 2'},
            {'message': 'Log 3'}
        ],
        'activity_count': 20
    }
    
    analyzer2 = BBPPAnalyzer()
    findings2 = analyzer2.analyze(test_data_good)
    
    logs_findings2 = [f for f in findings2 if f.rule_id == 'LOGS_001']
    
    print(f"\n📊 Caso 2: 20 actividades, 3 logs")
    print(f"   Ratio esperado: 6.7 actividades/log")
    print(f"   Máximo permitido: 10")
    print(f"   Hallazgos: {len(logs_findings2)}")
    
    if len(logs_findings2) == 0:
        print(f"   ✅ CORRECTO - No se reportó error (ratio dentro del límite)")
    else:
        print(f"   ❌ ERROR - Se reportó error cuando no debería")
        return False
    
    # Caso 3: 100 actividades, 0 logs = ratio infinito (muy malo)
    test_data_worst = {
        'file_path': '/test/Main.xaml',
        'workflow_type': 'Sequence',
        'variables': [],
        'arguments': [],
        'activities': [{'type': 'Assign', 'name': f'Act{i}'} for i in range(100)],
        'log_messages': [],
        'activity_count': 100
    }
    
    analyzer3 = BBPPAnalyzer()
    findings3 = analyzer3.analyze(test_data_worst)
    
    logs_findings3 = [f for f in findings3 if f.rule_id == 'LOGS_001']
    
    print(f"\n📊 Caso 3: 100 actividades, 0 logs")
    print(f"   Ratio esperado: 100.0 (sin logs)")
    print(f"   Máximo permitido: 10")
    print(f"   Hallazgos: {len(logs_findings3)}")
    
    if len(logs_findings3) > 0:
        print(f"   ✅ DETECTADO - Ratio: {logs_findings3[0].details.get('actual_ratio')}")
    else:
        print(f"   ❌ ERROR - No se detectó ausencia total de logs")
        return False
    
    print(f"\n{'='*70}")
    print(f"✅ TODOS LOS CASOS PASARON - LOGS_001 funciona correctamente")
    print(f"{'='*70}")
    return True


def test_logs_001_parameter_configurable():
    """Verificar que el parámetro max_activities_per_log es configurable"""
    print("\n" + "=" * 70)
    print("TEST: LOGS_001 - Parámetro Configurable")
    print("=" * 70)
    
    manager = get_rules_manager()
    
    # Verificar que el parámetro existe
    param_value = manager.get_rule_parameter('LOGS_001', 'max_activities_per_log')
    
    print(f"\n📊 Parámetro max_activities_per_log")
    print(f"   Valor actual: {param_value}")
    print(f"   Tipo esperado: number")
    
    if param_value == 10:
        print(f"   ✅ CORRECTO - Valor por defecto es 10")
        return True
    else:
        print(f"   ❌ ERROR - Valor esperado: 10, obtenido: {param_value}")
        return False


if __name__ == "__main__":
    print("\n" + "🧪" * 35)
    print("   TESTS DE VALIDACIÓN - LOGS_001 MEJORADA")
    print("🧪" * 35)
    
    results = []
    results.append(("Cálculo de Ratio", test_logs_001_ratio_calculation()))
    results.append(("Parámetro Configurable", test_logs_001_parameter_configurable()))
    
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
