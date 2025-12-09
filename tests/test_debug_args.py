"""
Test simple para debug
"""
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from analyzer import BBPPAnalyzer
from rules_manager import get_rules_manager

# Cargar reglas
rules_manager = get_rules_manager()
rules = rules_manager.get_active_rules(['UiPath', 'NTTData'])

# Ver cuántas reglas de tipo argument_prefixes hay
prefix_rules = [r for r in rules if r.get('rule_type') == 'argument_prefixes']
print(f"Reglas de tipo 'argument_prefixes': {len(prefix_rules)}")
for rule in prefix_rules:
    print(f"  - {rule['id']}: {rule['name']}")
    print(f"    Enabled: {rule.get('enabled')}")
    print(f"    Parameters: {rule.get('parameters', {})}")

# Crear analyzer
analyzer = BBPPAnalyzer(rules=rules, active_sets=['UiPath', 'NTTData'])

# Datos de prueba
test_data = {
    'file_path': 'test.xaml',
    'variables': [],
    'arguments': [
        {'name': 'in_myArgument', 'direction': 'In'},
    ]
}

# Analizar
findings = analyzer.analyze(test_data)

print(f"\n📊 Hallazgos encontrados: {len(findings)}")

for i, finding in enumerate(findings, 1):
    print(f"\n{i}. Regla: {finding.rule_id}")
    print(f"   Argumento: {finding.details.get('argument_name')}")
    print(f"   Problema: {finding.details.get('issue', 'N/A')}")
