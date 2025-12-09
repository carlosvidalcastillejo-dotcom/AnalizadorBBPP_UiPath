"""
Test para verificar la regla DESARROLLO_001 - Actividades Modernas
"""
import sys
from pathlib import Path

# Agregar raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rules_manager import RulesManager
from src.analyzer import BBPPAnalyzer

def test_modern_activities():
    """Test de la regla de actividades modernas"""

    print("\n" + "="*80)
    print("TEST: DESARROLLO_001 - Uso de Actividades Modernas")
    print("="*80 + "\n")

    # Cargar reglas
    rules_manager = RulesManager()
    rules_manager.load_rules()

    # Obtener reglas activas del conjunto UiPath
    active_rules = rules_manager.get_active_rules(['UiPath'])

    # Verificar que la regla DESARROLLO_001 está cargada
    modern_rule = next((r for r in active_rules if r['id'] == 'DESARROLLO_001'), None)

    if modern_rule:
        print(f"✅ Regla DESARROLLO_001 encontrada:")
        print(f"   Nombre: {modern_rule['name']}")
        print(f"   Categoría: {modern_rule['category']}")
        print(f"   Severidad: {modern_rule['severity']}")
        print(f"   Habilitada: {modern_rule['enabled']}")
        print(f"   Penalización: {modern_rule['penalty']}")
        print()
    else:
        print("❌ ERROR: Regla DESARROLLO_001 no encontrada\n")
        return False

    # Crear analizador
    analyzer = BBPPAnalyzer(rules_manager, active_sets=['UiPath'])

    # TEST 1: Proyecto con actividades CLÁSICAS (Legacy)
    print("\n--- TEST 1: Proyecto con actividades CLÁSICAS ---")
    project_info_legacy = {
        'name': 'TEST_001_ProyectoClasico',
        'project_profile': 'Legacy',  # ❌ Clásicas
        'dependencies': []
    }

    analyzer.findings = []  # Reset findings
    findings_legacy = analyzer.analyze_project(project_info_legacy)

    legacy_findings = [f for f in findings_legacy if f.rule_id == 'DESARROLLO_001']

    if legacy_findings:
        print(f"✅ CORRECTO: Detectó que usa actividades clásicas")
        print(f"   Hallazgos: {len(legacy_findings)}")
        for finding in legacy_findings:
            print(f"   - {finding.rule_name}")
            print(f"     Archivo: {finding.file_path}")
            print(f"     Ubicación: {finding.location}")
            print(f"     Severidad: {finding.severity}")
            if finding.details:
                print(f"     Profile actual: {finding.details.get('current_profile')}")
                print(f"     Profile requerido: {finding.details.get('required_profile')}")
                print(f"     Sugerencia: {finding.details.get('suggestion', '')[:100]}...")
    else:
        print("❌ ERROR: No detectó actividades clásicas (debería detectar)")
        return False

    # TEST 2: Proyecto con actividades MODERNAS (Simplified)
    print("\n--- TEST 2: Proyecto con actividades MODERNAS ---")
    project_info_modern = {
        'name': 'TEST_002_ProyectoModerno',
        'project_profile': 'Simplified',  # ✅ Modernas
        'dependencies': []
    }

    analyzer.findings = []  # Reset findings
    findings_modern = analyzer.analyze_project(project_info_modern)

    modern_findings = [f for f in findings_modern if f.rule_id == 'DESARROLLO_001']

    if not modern_findings:
        print(f"✅ CORRECTO: No generó hallazgos (proyecto moderno)")
    else:
        print(f"❌ ERROR: Generó hallazgos incorrectamente (no debería)")
        for finding in modern_findings:
            print(f"   - {finding.rule_name}: {finding.message}")
        return False

    # TEST 3: Proyecto sin projectProfile (default Legacy)
    print("\n--- TEST 3: Proyecto SIN projectProfile (default Legacy) ---")
    project_info_no_profile = {
        'name': 'TEST_003_SinProfile',
        # No tiene 'project_profile'
        'dependencies': []
    }

    analyzer.findings = []  # Reset findings
    findings_no_profile = analyzer.analyze_project(project_info_no_profile)

    no_profile_findings = [f for f in findings_no_profile if f.rule_id == 'DESARROLLO_001']

    if no_profile_findings:
        print(f"✅ CORRECTO: Detectó que usa Legacy por defecto")
        print(f"   Profile detectado: {no_profile_findings[0].details.get('current_profile')}")
    else:
        print("❌ ERROR: No detectó Legacy por defecto")
        return False

    print("\n" + "="*80)
    print("✅ TODOS LOS TESTS PASARON")
    print("="*80 + "\n")

    return True

if __name__ == '__main__':
    try:
        success = test_modern_activities()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR EN TEST: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
