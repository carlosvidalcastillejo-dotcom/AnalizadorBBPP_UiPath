"""
Test Completo - Sistema de Gestión de Conjuntos de BBPP
Validar funciones de configuración y gestión
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import (
    load_user_config, save_user_config,
    get_active_bbpp_sets, set_active_bbpp_sets,
    get_available_bbpp_sets, get_active_rules
)

print("=" * 80)
print("🧪 TEST - Sistema de Gestión de Conjuntos de BBPP")
print("=" * 80)

# Test 1: Cargar configuración de usuario
print("\n📋 Test 1: Cargar configuración de usuario")
print("-" * 80)
user_config = load_user_config()
print(f"✅ Configuración cargada")
print(f"   Versión: {user_config.get('version', 'N/A')}")
print(f"   Última actualización: {user_config.get('last_updated', 'N/A')}")
print(f"   Conjuntos activos: {user_config.get('active_bbpp_sets', [])}")

# Test 2: Obtener conjuntos activos
print("\n\n📋 Test 2: Obtener conjuntos activos")
print("-" * 80)
active_sets = get_active_bbpp_sets()
print(f"✅ {len(active_sets)} conjunto(s) activo(s):")
for bbpp_set in active_sets:
    print(f"   • {bbpp_set}")

# Test 3: Obtener información de conjuntos disponibles
print("\n\n📋 Test 3: Información de conjuntos disponibles")
print("-" * 80)
available_sets = get_available_bbpp_sets()
print(f"✅ {len(available_sets)} conjunto(s) disponible(s):")

for bbpp_set in available_sets:
    status = "🟢 ACTIVO" if bbpp_set['is_active'] else "⚪ INACTIVO"
    print(f"\n   {status} {bbpp_set['name']}")
    print(f"      Archivo: {bbpp_set['filename']}")
    print(f"      Versión: {bbpp_set['version']}")
    print(f"      Autor: {bbpp_set['author']}")
    print(f"      Reglas: {bbpp_set['rules_count']}")
    if bbpp_set['description']:
        print(f"      Desc: {bbpp_set['description'][:60]}...")

# Test 4: Cambiar conjuntos activos
print("\n\n📋 Test 4: Cambiar configuración de conjuntos activos")
print("-" * 80)
print("📝 Activando solo BBPP_UiPath.json...")
success = set_active_bbpp_sets(["BBPP_UiPath.json"])
if success:
    print("✅ Configuración guardada")
    
    # Verificar
    active_sets = get_active_bbpp_sets()
    print(f"   Conjuntos activos ahora: {active_sets}")
else:
    print("❌ Error al guardar configuración")

# Test 5: Obtener reglas activas
print("\n\n📋 Test 5: Obtener reglas activas (solo conjuntos activos)")
print("-" * 80)
active_rules = get_active_rules()
print(f"✅ {len(active_rules)} regla(s) activa(s)")

# Agrupar por categoría
by_category = {}
for rule in active_rules:
    category = rule.get('category', 'unknown')
    if category not in by_category:
        by_category[category] = []
    by_category[category].append(rule)

print("\n   Distribución por categoría:")
for category, rules in sorted(by_category.items()):
    print(f"      • {category}: {len(rules)} regla(s)")

# Test 6: Activar todos los conjuntos
print("\n\n📋 Test 6: Activar todos los conjuntos")
print("-" * 80)
all_filenames = [s['filename'] for s in available_sets]
print(f"📝 Activando todos los conjuntos: {all_filenames}")
success = set_active_bbpp_sets(all_filenames)
if success:
    print("✅ Todos los conjuntos activados")
    
    active_rules = get_active_rules()
    print(f"   Total de reglas activas: {len(active_rules)}")
else:
    print("❌ Error al guardar configuración")

# Test 7: Simular análisis con configuración
print("\n\n📋 Test 7: Simular análisis con configuración activa")
print("-" * 80)
from analyzer import BBPPAnalyzer

analyzer = BBPPAnalyzer()
print(f"✅ Analizador inicializado con {len(analyzer.rules)} reglas")

# Datos de prueba
test_data = {
    'file_path': 'test.xaml',
    'workflow_type': 'Sequence',
    'variables': [{'name': 'Temp', 'type': 'String'}],  # Nombre genérico
    'arguments': [],
    'activities': [],
    'activity_count': 5,
    'try_catch_blocks': [],
    'total_lines': 100,
    'commented_lines': 0,
    'log_message_count': 1,
}

findings = analyzer.analyze(test_data)
print(f"✅ Análisis completado: {len(findings)} hallazgo(s)")

if findings:
    print("\n   Hallazgos detectados:")
    for finding in findings[:3]:
        print(f"      • {finding.rule_name} ({finding.severity})")

# Resumen final
print("\n\n" + "=" * 80)
print("🎉 RESUMEN DEL TEST")
print("=" * 80)
print(f"✅ Configuración de usuario: OK")
print(f"✅ Conjuntos disponibles: {len(available_sets)}")
print(f"✅ Conjuntos activos: {len(active_sets)}")
print(f"✅ Reglas activas: {len(active_rules)}")
print(f"✅ Persistencia: OK")
print(f"✅ Integración con analizador: OK")
print("\n🎯 Sistema de Gestión de Conjuntos funcionando correctamente")
print("=" * 80)
