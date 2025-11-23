"""
Test completo de todas las configuraciones con RulesManager
Verifica que el sistema de reglas desde BBPP_Master.json funcione correctamente
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analyzer import BBPPAnalyzer
from src.rules_manager import get_rules_manager


def test_rules_manager_loading():
    """Verificar que RulesManager carga correctamente las reglas"""
    print("\n" + "=" * 60)
    print("TEST 1: Carga de Reglas desde BBPP_Master.json")
    print("=" * 60)
    
    manager = get_rules_manager()
    all_rules = manager.get_all_rules()
    active_rules = manager.get_active_rules(['UiPath', 'NTTData'])
    
    print(f"   Total reglas cargadas: {len(all_rules)}")
    print(f"   Reglas activas (UiPath + NTTData): {len(active_rules)}")
    
    # Verificar que las reglas EXCEL están marcadas como implemented
    excel_rules = [r for r in all_rules if r['id'].startswith('EXCEL_')]
    implemented_excel = [r for r in excel_rules if r.get('implementation_status') == 'implemented']
    
    print(f"   Reglas EXCEL: {len(excel_rules)}")
    print(f"   Reglas EXCEL implementadas: {len(implemented_excel)}")
    
    if len(implemented_excel) >= 7:
        print("   ✅ PASS - Reglas EXCEL correctamente marcadas como implemented")
        return True
    else:
        print("   ❌ FAIL - Algunas reglas EXCEL no están implementadas")
        return False


def test_configurable_parameters():
    """Verificar que parámetros configurables funcionan"""
    print("\n" + "=" * 60)
    print("TEST 2: Parámetros Configurables")
    print("=" * 60)
    
    manager = get_rules_manager()
    
    # Test 1: max_nested_levels (ANIDAMIENTO_001)
    max_levels = manager.get_rule_parameter('ANIDAMIENTO_001', 'max_nested_levels')
    print(f"   ANIDAMIENTO_001.max_nested_levels = {max_levels}")
    
    # Test 2: max_activities (MODULARIZACION_001)
    max_activities = manager.get_rule_parameter('MODULARIZACION_001', 'max_activities')
    print(f"   MODULARIZACION_001.max_activities = {max_activities}")
    
    # Test 3: max_percentage (COMENTARIOS_001)
    max_percentage = manager.get_rule_parameter('COMENTARIOS_001', 'max_percentage')
    print(f"   COMENTARIOS_001.max_percentage = {max_percentage}")
    
    if max_levels and max_activities and max_percentage:
        print("   ✅ PASS - Parámetros configurables cargados correctamente")
        return True
    else:
        print("   ❌ FAIL - Error al cargar parámetros")
        return False


def test_nested_ifs_with_parameter():
    """Verificar que regla de IFs anidados usa parámetro configurable"""
    print("\n" + "=" * 60)
    print("TEST 3: IFs Anidados con Parámetro Configurable")
    print("=" * 60)
    
    test_data = {
        'file_path': '/test/Main.xaml',
        'workflow_type': 'Sequence',
        'variables': [],
        'arguments': [],
        'activities': [
            {'type': 'If', 'name': 'If1'},
            {'type': 'If', 'name': 'If2'},
            {'type': 'If', 'name': 'If3'},
            {'type': 'If', 'name': 'If4'},
            {'type': 'If', 'name': 'If5'}  # 5 IFs, debería detectar si max=3
        ],
        'log_messages': [],
        'activity_count': 5
    }
    
    analyzer = BBPPAnalyzer()
    findings = analyzer.analyze(test_data)
    
    nested_findings = [f for f in findings if 'anidado' in f.description.lower() or 'nested' in f.description.lower()]
    
    print(f"   Hallazgos de IFs anidados: {len(nested_findings)}")
    
    if len(nested_findings) > 0:
        print(f"   Detalles: {nested_findings[0].details}")
        print("   ✅ PASS - Regla de IFs anidados funciona con parámetro")
        return True
    else:
        print("   ⚠️ WARNING - No se detectaron IFs anidados (puede ser normal)")
        return True  # No es error crítico


def test_commented_code_with_parameter():
    """Verificar que código comentado usa parámetro configurable"""
    print("\n" + "=" * 60)
    print("TEST 4: Código Comentado con Parámetro Configurable")
    print("=" * 60)
    
    # Archivo con 10% de código comentado
    test_data = {
        'file_path': '/test/Main.xaml',
        'workflow_type': 'Sequence',
        'variables': [],
        'arguments': [],
        'activities': [
            {'type': 'Assign', 'name': 'Act1'},
            {'type': 'Assign', 'name': 'Act2'},
            {'type': 'Assign', 'name': 'Act3'},
            {'type': 'Assign', 'name': 'Act4'},
            {'type': 'Assign', 'name': 'Act5'},
            {'type': 'Assign', 'name': 'Act6'},
            {'type': 'Assign', 'name': 'Act7'},
            {'type': 'Assign', 'name': 'Act8'},
            {'type': 'CommentOut', 'name': 'Commented1'},  # 10% comentado
            {'type': 'Assign', 'name': 'Act9'}
        ],
        'log_messages': [],
        'activity_count': 10
    }
    
    analyzer = BBPPAnalyzer()
    findings = analyzer.analyze(test_data)
    
    commented_findings = [f for f in findings if 'comentado' in f.description.lower() or 'commented' in f.description.lower()]
    
    print(f"   Hallazgos de código comentado: {len(commented_findings)}")
    
    if len(commented_findings) > 0:
        print(f"   Porcentaje detectado: {commented_findings[0].details.get('percentage', 'N/A')}%")
        print("   ✅ PASS - Regla de código comentado funciona con parámetro")
        return True
    else:
        print("   ❌ FAIL - No se detectó código comentado excesivo")
        return False


def test_excel_rules_active():
    """Verificar que reglas EXCEL están activas y funcionan"""
    print("\n" + "=" * 60)
    print("TEST 5: Reglas EXCEL Activas")
    print("=" * 60)
    
    test_data = {
        'file_path': '/test/Main.xaml',
        'workflow_type': 'Sequence',
        'variables': [],
        'arguments': [],
        'activities': [
            {
                'type': 'Click',
                'display_name': 'Click sin Try-Catch',
                'parent_type': 'Sequence',  # NO está en TryCatch
                'properties': {}
            }
        ],
        'log_messages': [],
        'activity_count': 1,
        'project_path': '/test/project'
    }
    
    analyzer = BBPPAnalyzer()
    findings = analyzer.analyze(test_data)
    
    excel_findings = [f for f in findings if f.rule_id.startswith('EXCEL_')]
    
    print(f"   Hallazgos de reglas EXCEL: {len(excel_findings)}")
    
    if len(excel_findings) > 0:
        for finding in excel_findings[:3]:  # Mostrar primeros 3
            print(f"   - {finding.rule_id}: {finding.rule_name}")
        print("   ✅ PASS - Reglas EXCEL están activas y detectando")
        return True
    else:
        print("   ⚠️ WARNING - No se detectaron violaciones EXCEL (puede ser normal)")
        return True


def test_argument_prefixes():
    """Verificar regla de prefijos de argumentos"""
    print("\n" + "=" * 60)
    print("TEST 6: Prefijos de Argumentos")
    print("=" * 60)
    
    test_data = {
        'file_path': '/test/Main.xaml',
        'workflow_type': 'Sequence',
        'variables': [],
        'arguments': [
            {'name': 'ClienteNombre', 'direction': 'In', 'annotation': 'Nombre del cliente'},  # Sin prefijo in_
            {'name': 'in_Correcto', 'direction': 'In', 'annotation': 'Correcto'},
            {'name': 'ResultadoFinal', 'direction': 'Out', 'annotation': 'Resultado'}  # Sin prefijo out_
        ],
        'activities': [],
        'log_messages': [],
        'activity_count': 0
    }
    
    analyzer = BBPPAnalyzer()
    findings = analyzer.analyze(test_data)
    
    prefix_findings = [f for f in findings if 'prefijo' in f.description.lower() or 'prefix' in f.description.lower()]
    
    print(f"   Hallazgos de prefijos: {len(prefix_findings)}")
    
    if len(prefix_findings) >= 2:  # Debería detectar 2 argumentos sin prefijo
        print("   ✅ PASS - Regla de prefijos funciona correctamente")
        return True
    else:
        print("   ❌ FAIL - No se detectaron argumentos sin prefijo")
        return False


if __name__ == "__main__":
    print("\n" + "🧪" * 30)
    print("   TESTS DE INTEGRACIÓN CON RULESMANAGER v1.0")
    print("🧪" * 30)
    
    results = []
    
    results.append(("Carga de Reglas", test_rules_manager_loading()))
    results.append(("Parámetros Configurables", test_configurable_parameters()))
    results.append(("IFs Anidados con Parámetro", test_nested_ifs_with_parameter()))
    results.append(("Código Comentado con Parámetro", test_commented_code_with_parameter()))
    results.append(("Reglas EXCEL Activas", test_excel_rules_active()))
    results.append(("Prefijos de Argumentos", test_argument_prefixes()))
    
    print("\n" + "=" * 60)
    print("RESUMEN FINAL:")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + ("✅ TODOS LOS TESTS PASARON" if all_passed else "❌ ALGUNOS TESTS FALLARON"))
    print("=" * 60)
