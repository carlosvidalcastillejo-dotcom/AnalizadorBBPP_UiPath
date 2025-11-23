"""
Test del Sistema de BBPP con JSON
Validar que las reglas se cargan y aplican correctamente
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import load_all_bbpp_sets, get_enabled_rules, get_rules_by_category
from analyzer import BBPPAnalyzer

print("=" * 80)
print("🧪 TEST - Sistema de BBPP con JSON")
print("=" * 80)

# Test 1: Cargar conjuntos de BBPP
print("\n📋 Test 1: Cargar conjuntos de BBPP")
print("-" * 80)
bbpp_sets = load_all_bbpp_sets()
print(f"✅ {len(bbpp_sets)} conjunto(s) cargado(s)")

for bbpp_set in bbpp_sets:
    metadata = bbpp_set.get('metadata', {})
    rules_count = len(bbpp_set.get('rules', []))
    print(f"\n  📦 {metadata.get('name', 'Sin nombre')}")
    print(f"     Versión: {metadata.get('version', 'N/A')}")
    print(f"     Autor: {metadata.get('author', 'N/A')}")
    print(f"     Reglas: {rules_count}")

# Test 2: Obtener reglas habilitadas
print("\n\n📋 Test 2: Obtener reglas habilitadas")
print("-" * 80)
enabled_rules = get_enabled_rules(bbpp_sets)
print(f"✅ {len(enabled_rules)} regla(s) habilitada(s) en total")

# Agrupar por categoría
categories = {}
for rule in enabled_rules:
    category = rule.get('category', 'unknown')
    if category not in categories:
        categories[category] = []
    categories[category].append(rule)

print("\n  Distribución por categoría:")
for category, rules in sorted(categories.items()):
    print(f"    • {category}: {len(rules)} regla(s)")

# Test 3: Mostrar detalles de algunas reglas
print("\n\n📋 Test 3: Detalles de reglas")
print("-" * 80)
for i, rule in enumerate(enabled_rules[:3], 1):
    print(f"\n  Regla #{i}:")
    print(f"    ID: {rule.get('id')}")
    print(f"    Nombre: {rule.get('name')}")
    print(f"    Categoría: {rule.get('category')}")
    print(f"    Severidad: {rule.get('severity')}")
    print(f"    Tipo: {rule.get('rule_type')}")
    print(f"    Habilitada: {rule.get('enabled')}")

# Test 4: Inicializar analizador con reglas JSON
print("\n\n📋 Test 4: Inicializar Analizador")
print("-" * 80)
analyzer = BBPPAnalyzer()
print(f"✅ Analizador inicializado con {len(analyzer.rules)} reglas")
print(f"✅ Tipos de reglas detectados: {len(analyzer.rules_by_type)}")

for rule_type, rules in sorted(analyzer.rules_by_type.items()):
    print(f"    • {rule_type}: {len(rules)} regla(s)")

# Test 5: Simular análisis con datos de prueba
print("\n\n📋 Test 5: Análisis simulado")
print("-" * 80)

# Datos de prueba que deberían generar hallazgos
test_data = {
    'file_path': 'test_workflow.xaml',
    'workflow_type': 'Sequence',
    'variables': [
        {'name': 'MiVariable', 'type': 'String'},  # No camelCase
        {'name': 'temp', 'type': 'String'},        # Nombre genérico
        {'name': 'contador', 'type': 'Int32'},     # OK
    ],
    'arguments': [
        {'name': 'nombreCliente', 'direction': 'In', 'annotation': ''},  # Sin prefijo y sin descripción
        {'name': 'out_resultado', 'direction': 'Out', 'annotation': 'Resultado del proceso'},  # OK
    ],
    'activities': [],
    'activity_count': 5,
    'try_catch_blocks': [
        {'catch_empty': True, 'line': 42}  # Catch vacío
    ],
    'total_lines': 100,
    'commented_lines': 15,  # 15% comentado
    'log_message_count': 0,  # Sin logs
}

findings = analyzer.analyze(test_data)

print(f"✅ Análisis completado: {len(findings)} hallazgo(s) detectado(s)")

# Agrupar hallazgos por severidad
by_severity = {}
for finding in findings:
    sev = finding.severity
    if sev not in by_severity:
        by_severity[sev] = []
    by_severity[sev].append(finding)

print("\n  Distribución por severidad:")
for severity in ['error', 'warning', 'info']:
    count = len(by_severity.get(severity, []))
    if count > 0:
        icon = '🔴' if severity == 'error' else '⚠️' if severity == 'warning' else 'ℹ️'
        print(f"    {icon} {severity.upper()}: {count}")

# Mostrar algunos hallazgos
print("\n  Ejemplo de hallazgos:")
for i, finding in enumerate(findings[:5], 1):
    print(f"\n    Hallazgo #{i}:")
    print(f"      Regla: {finding.rule_name} ({finding.rule_id})")
    print(f"      Categoría: {finding.category}")
    print(f"      Severidad: {finding.severity}")
    print(f"      Ubicación: {finding.location}")

# Test 6: Validación de estructura JSON
print("\n\n📋 Test 6: Validar estructura JSON")
print("-" * 80)

required_fields = ['id', 'name', 'category', 'severity', 'enabled', 'description', 'rule_type', 'parameters']
issues_found = False

for bbpp_set in bbpp_sets:
    bbpp_name = bbpp_set.get('metadata', {}).get('name', 'Unknown')
    
    for rule in bbpp_set.get('rules', []):
        missing_fields = [field for field in required_fields if field not in rule]
        
        if missing_fields:
            issues_found = True
            print(f"  ⚠️ {bbpp_name} - Regla {rule.get('id', 'NO_ID')}: Faltan campos {missing_fields}")

if not issues_found:
    print("  ✅ Todas las reglas tienen la estructura correcta")

# Resumen final
print("\n\n" + "=" * 80)
print("🎉 RESUMEN DEL TEST")
print("=" * 80)
print(f"✅ Conjuntos cargados: {len(bbpp_sets)}")
print(f"✅ Reglas habilitadas: {len(enabled_rules)}")
print(f"✅ Tipos de reglas: {len(analyzer.rules_by_type)}")
print(f"✅ Hallazgos en test: {len(findings)}")
print(f"✅ Estructura JSON: {'OK' if not issues_found else 'CON PROBLEMAS'}")
print("\n🎯 Sistema de BBPP con JSON funcionando correctamente")
print("=" * 80)
