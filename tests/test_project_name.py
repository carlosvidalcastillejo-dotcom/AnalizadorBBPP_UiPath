"""
Test para verificar la regla NOMENCLATURA_006 - Nombre del Proceso/Step
Valida dos patrones: N.1 (procesos) y N.2 (steps)
"""
import sys
from pathlib import Path

# Añadir el directorio raíz al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rules_manager import RulesManager
from src.analyzer import BBPPAnalyzer

def test_project_name():
    """
    Verificar que la regla NOMENCLATURA_006 valida correctamente el nombre del proyecto
    """
    print("="*80)
    print("TEST: NOMENCLATURA_006 - Nombre del Proceso")
    print("="*80)

    # Cargar reglas
    rules_manager = RulesManager()
    rules_manager.load_rules()

    # Crear analizador con conjunto UiPath
    analyzer = BBPPAnalyzer(rules_manager, active_sets=['UiPath'])

    # Verificar que la regla está cargada
    project_name_rule = next((r for r in analyzer.rules if r.get('id') == 'NOMENCLATURA_006'), None)
    if project_name_rule:
        print(f"\n[OK] Regla NOMENCLATURA_006 cargada correctamente")
        patterns = project_name_rule.get('parameters', {}).get('patterns', [])
        print(f"     Patterns: {len(patterns)} patrones configurados")
        for i, p in enumerate(patterns, 1):
            print(f"       {i}. {p}")
    else:
        print(f"\n[ERROR] Regla NOMENCLATURA_006 NO encontrada")
        return

    # TEST 1: Nombre válido con patrón estándar
    print("\n" + "-"*80)
    print("TEST 1: Nombre válido - FIN_003_GenerarFactura")
    print("-"*80)
    analyzer.findings = []  # Resetear findings
    project_info_valid = {
        'name': 'FIN_003_GenerarFactura',
        'dependencies': []
    }
    findings = analyzer.analyze_project(project_info_valid)
    project_name_findings = [f for f in findings if f.rule_id == 'NOMENCLATURA_006']

    if len(project_name_findings) == 0:
        print("[OK] No se detectaron errores (comportamiento esperado)")
    else:
        print(f"[ERROR] Se detectó error cuando NO debería: {project_name_findings[0].details}")

    # TEST 2: Nombre válido con Dispatcher
    print("\n" + "-"*80)
    print("TEST 2: Nombre válido - FIN_001_Dispatcher")
    print("-"*80)
    analyzer.findings = []
    project_info_dispatcher = {
        'name': 'FIN_001_Dispatcher',
        'dependencies': []
    }
    findings = analyzer.analyze_project(project_info_dispatcher)
    project_name_findings = [f for f in findings if f.rule_id == 'NOMENCLATURA_006']

    if len(project_name_findings) == 0:
        print("[OK] No se detectaron errores (comportamiento esperado)")
    else:
        print(f"[ERROR] Se detectó error cuando NO debería: {project_name_findings[0].details}")

    # TEST 3: Nombre válido con Performer
    print("\n" + "-"*80)
    print("TEST 3: Nombre válido - ACC_SAP_Performer")
    print("-"*80)
    analyzer.findings = []
    project_info_performer = {
        'name': 'ACC_SAP_Performer',
        'dependencies': []
    }
    findings = analyzer.analyze_project(project_info_performer)
    project_name_findings = [f for f in findings if f.rule_id == 'NOMENCLATURA_006']

    if len(project_name_findings) == 0:
        print("[OK] No se detectaron errores (comportamiento esperado)")
    else:
        print(f"[ERROR] Se detectó error cuando NO debería: {project_name_findings[0].details}")

    # TEST 4: Nombre válido STEP - ACC_001_0100_App1_ConsultarOrden (patrón N.2)
    print("\n" + "-"*80)
    print("TEST 4: Nombre válido STEP - ACC_001_0100_App1_ConsultarOrden (N.2)")
    print("-"*80)
    analyzer.findings = []
    project_info_step1 = {
        'name': 'ACC_001_0100_App1_ConsultarOrden',
        'dependencies': []
    }
    findings = analyzer.analyze_project(project_info_step1)
    project_name_findings = [f for f in findings if f.rule_id == 'NOMENCLATURA_006']

    if len(project_name_findings) == 0:
        print("[OK] No se detectaron errores (comportamiento esperado)")
    else:
        print(f"[ERROR] Se detectó error cuando NO debería: {project_name_findings[0].details}")

    # TEST 5: Nombre válido STEP - LOG_CRM_0210_Portal_CrearSolicitud (patrón N.2)
    print("\n" + "-"*80)
    print("TEST 5: Nombre válido STEP - LOG_CRM_0210_Portal_CrearSolicitud (N.2)")
    print("-"*80)
    analyzer.findings = []
    project_info_step2 = {
        'name': 'LOG_CRM_0210_Portal_CrearSolicitud',
        'dependencies': []
    }
    findings = analyzer.analyze_project(project_info_step2)
    project_name_findings = [f for f in findings if f.rule_id == 'NOMENCLATURA_006']

    if len(project_name_findings) == 0:
        print("[OK] No se detectaron errores (comportamiento esperado)")
    else:
        print(f"[ERROR] Se detectó error cuando NO debería: {project_name_findings[0].details}")

    # TEST 6: Nombre válido STEP - FIN_SAP_0315_Sistema_ActualizarEstado (patrón N.2)
    print("\n" + "-"*80)
    print("TEST 6: Nombre válido STEP - FIN_SAP_0315_Sistema_ActualizarEstado (N.2)")
    print("-"*80)
    analyzer.findings = []
    project_info_step3 = {
        'name': 'FIN_SAP_0315_Sistema_ActualizarEstado',
        'dependencies': []
    }
    findings = analyzer.analyze_project(project_info_step3)
    project_name_findings = [f for f in findings if f.rule_id == 'NOMENCLATURA_006']

    if len(project_name_findings) == 0:
        print("[OK] No se detectaron errores (comportamiento esperado)")
    else:
        print(f"[ERROR] Se detectó error cuando NO debería: {project_name_findings[0].details}")

    # TEST 7: Nombre inválido - minúsculas
    print("\n" + "-"*80)
    print("TEST 7: Nombre inválido - fin_001_test (minúsculas)")
    print("-"*80)
    analyzer.findings = []
    project_info_invalid1 = {
        'name': 'fin_001_test',
        'dependencies': []
    }
    findings = analyzer.analyze_project(project_info_invalid1)
    project_name_findings = [f for f in findings if f.rule_id == 'NOMENCLATURA_006']

    if len(project_name_findings) > 0:
        print("[OK] Se detectó error (comportamiento esperado)")
        print(f"     Issue: {project_name_findings[0].details.get('issue')}")
        print(f"     Suggestion: {project_name_findings[0].details.get('suggestion')}")
    else:
        print("[ERROR] NO se detectó error cuando SI debería")

    # TEST 8: Nombre inválido - sin patrón
    print("\n" + "-"*80)
    print("TEST 8: Nombre inválido - proceso1 (sin patrón)")
    print("-"*80)
    analyzer.findings = []
    project_info_invalid2 = {
        'name': 'proceso1',
        'dependencies': []
    }
    findings = analyzer.analyze_project(project_info_invalid2)
    project_name_findings = [f for f in findings if f.rule_id == 'NOMENCLATURA_006']

    if len(project_name_findings) > 0:
        print("[OK] Se detectó error (comportamiento esperado)")
        print(f"     Issue: {project_name_findings[0].details.get('issue')}")
    else:
        print("[ERROR] NO se detectó error cuando SI debería")

    # TEST 9: Nombre inválido - falta código de sistema
    print("\n" + "-"*80)
    print("TEST 9: Nombre inválido - FIN_GenerarFactura (falta código sistema)")
    print("-"*80)
    analyzer.findings = []
    project_info_invalid3 = {
        'name': 'FIN_GenerarFactura',
        'dependencies': []
    }
    findings = analyzer.analyze_project(project_info_invalid3)
    project_name_findings = [f for f in findings if f.rule_id == 'NOMENCLATURA_006']

    if len(project_name_findings) > 0:
        print("[OK] Se detectó error (comportamiento esperado)")
        print(f"     Issue: {project_name_findings[0].details.get('issue')}")
    else:
        print("[ERROR] NO se detectó error cuando SI debería")

    # TEST 10: Nombre con guiones bajos múltiples - FIN_001_01_Consultar
    # NOTA: Este nombre cumple con N.1 (proceso general), aunque parezca un step mal formado
    print("\n" + "-"*80)
    print("TEST 10: Nombre válido (N.1) - FIN_001_01_Consultar")
    print("-"*80)
    analyzer.findings = []
    project_info_mixed = {
        'name': 'FIN_001_01_Consultar',
        'dependencies': []
    }
    findings = analyzer.analyze_project(project_info_mixed)
    project_name_findings = [f for f in findings if f.rule_id == 'NOMENCLATURA_006']

    if len(project_name_findings) == 0:
        print("[OK] No se detectaron errores (cumple patrón N.1)")
    else:
        print(f"[ADVERTENCIA] Se detectó error: {project_name_findings[0].details}")

    print("\n" + "="*80)
    print("FIN DEL TEST - Total: 10 casos de prueba")
    print("="*80)

if __name__ == "__main__":
    test_project_name()
