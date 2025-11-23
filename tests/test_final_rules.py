"""
Test de validación para el sistema de penalización y reglas finales
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analyzer import BBPPAnalyzer


def test_penalty_mode_individual():
    """Verificar que penalty_mode individual multiplica por casos"""
    print("\n" + "=" * 70)
    print("TEST: Penalty Mode - Individual")
    print("=" * 70)
    
    # Simular 5 actividades con timeout por defecto
    test_data = {
        'file_path': '/test/Main.xaml',
        'workflow_type': 'Sequence',
        'variables': [],
        'arguments': [],
        'activities': [
            {'type': 'Click', 'display_name': 'Click 1', 'properties': {'TimeoutMS': '30000'}},
            {'type': 'Click', 'display_name': 'Click 2', 'properties': {'TimeoutMS': '30000'}},
            {'type': 'TypeInto', 'display_name': 'Type 1', 'properties': {}},
            {'type': 'GetText', 'display_name': 'Get 1', 'properties': {'Timeout': '30000'}},
            {'type': 'ElementExists', 'display_name': 'Exists 1', 'properties': {'TimeoutMS': '30000'}},
        ],
        'log_messages': [],
        'activity_count': 5
    }
    
    analyzer = BBPPAnalyzer()
    findings = analyzer.analyze(test_data)
    
    timeout_findings = [f for f in findings if f.rule_id == 'RENDIMIENTO_001']  # Nuevo ID
    
    print(f"\n📊 Actividades con timeout por defecto: 5")
    print(f"   Hallazgos: {len(timeout_findings)}")

    
    if len(timeout_findings) > 0:
        finding = timeout_findings[0]
        print(f"   ✅ DETECTADO")
        print(f"   Base penalty: {finding.details.get('base_penalty', 'N/A')}")
        print(f"   Casos encontrados: {finding.details.get('cases_found', 'N/A')}")
        print(f"   Penalty mode: {finding.details.get('penalty_mode', 'N/A')}")
        print(f"   Penalización actual: {finding.details.get('actual_penalty', 'N/A')}")
        
        # Verificar que penalty_mode = individual multiplica
        if finding.details.get('penalty_mode') == 'individual':
            expected = finding.details.get('base_penalty', 0) * finding.details.get('cases_found', 0)
            actual = finding.details.get('actual_penalty', 0)
            if actual == expected:
                print(f"   ✅ Penalización individual correcta: {actual}")
                return True
            else:
                print(f"   ❌ Error: esperado {expected}, obtenido {actual}")
                return False
    else:
        print(f"   ❌ No se detectaron timeouts por defecto")
        return False


def test_anidamiento_nesting_level():
    """Verificar que ANIDAMIENTO_001 usa nesting_level"""
    print("\n" + "=" * 70)
    print("TEST: ANIDAMIENTO_001 - Nesting Level Real")
    print("=" * 70)
    
    test_data = {
        'file_path': '/test/Main.xaml',
        'workflow_type': 'Sequence',
        'variables': [],
        'arguments': [],
        'activities': [],
        'if_activities': [
            {'display_name': 'If 1', 'nesting_level': 0},
            {'display_name': 'If 2', 'nesting_level': 1},
            {'display_name': 'If 3', 'nesting_level': 2},
            {'display_name': 'If 4', 'nesting_level': 4},  # Excede límite de 3
        ],
        'log_messages': [],
        'activity_count': 10
    }
    
    analyzer = BBPPAnalyzer()
    findings = analyzer.analyze(test_data)
    
    nesting_findings = [f for f in findings if f.rule_id == 'ESTRUCTURA_001']  # Nuevo ID
    
    print(f"\n📊 IFs con nesting_level máximo: 4")
    print(f"   Límite permitido: 3")
    print(f"   Hallazgos: {len(nesting_findings)}")
    
    if len(nesting_findings) > 0:
        finding = nesting_findings[0]
        max_found = finding.details.get('max_nesting_found', 0)
        print(f"   ✅ DETECTADO - Máximo encontrado: {max_found}")
        return max_found == 4
    else:
        print(f"   ❌ No se detectó anidamiento excesivo")
        return False


def test_excel_006_suggestion():
    """Verificar que EXCEL_006 es sugerencia sin penalización"""
    print("\n" + "=" * 70)
    print("TEST: EXCEL_006 - Sugerencia sin Penalización")
    print("=" * 70)
    
    test_data = {
        'file_path': '/test/Main.xaml',
        'workflow_type': 'Sequence',
        'variables': [],
        'arguments': [],
        'activities': [{'type': 'Assign', 'display_name': f'Act{i}'} for i in range(60)],
        'log_messages': [],
        'activity_count': 60
    }
    
    analyzer = BBPPAnalyzer()
    findings = analyzer.analyze(test_data)
    
    invoke_findings = [f for f in findings if f.rule_id == 'MODULARIZACION_002']  # Nuevo ID
    
    print(f"\n📊 Workflow con 60 actividades sin Invoke")
    print(f"   Hallazgos: {len(invoke_findings)}")
    
    if len(invoke_findings) > 0:
        finding = invoke_findings[0]
        penalty = finding.details.get('actual_penalty', -1)
        print(f"   ✅ SUGERENCIA DETECTADA")
        print(f"   Penalización: {penalty}")
        
        if penalty == 0:
            print(f"   ✅ Penalización correcta (0)")
            return True
        else:
            print(f"   ❌ Error: debería ser 0, es {penalty}")
            return False
    else:
        print(f"   ❌ No se generó sugerencia")
        return False


if __name__ == "__main__":
    print("\n" + "🧪" * 35)
    print("   TESTS DE VALIDACIÓN - REGLAS FINALES")
    print("🧪" * 35)
    
    results = []
    results.append(("Penalty Mode Individual", test_penalty_mode_individual()))
    results.append(("Anidamiento Nesting Level", test_anidamiento_nesting_level()))
    results.append(("EXCEL_006 Sugerencia", test_excel_006_suggestion()))
    
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
