"""
Test para verificar que la configuración del usuario se conecta correctamente con el analyzer
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_user_config, save_user_config, DEFAULT_CONFIG
from src.analyzer import BBPPAnalyzer


def test_config_toggles():
    """Verificar que los toggles de validación se respetan"""
    print("=" * 60)
    print("TEST: Conexión de configuración con analyzer")
    print("=" * 60)
    
    # Datos de prueba con argumentos sin prefijo y sin descripción
    test_data = {
        'file_path': '/test/Main.xaml',
        'workflow_type': 'Sequence',
        'variables': [
            {'name': 'miVariable', 'type': 'String'}
        ],
        'arguments': [
            {'name': 'ClienteNombre', 'direction': 'In', 'annotation': ''},
            {'name': 'out_Resultado', 'direction': 'Out', 'annotation': 'Resultado del proceso'}
        ],
        'activities': [],
        'log_messages': [],
        'total_lines': 100,
        'commented_lines': 0
    }
    
    # Test 1: Con validaciones activadas
    print("\n📋 Test 1: Validaciones ACTIVADAS")
    config_on = {
        'validations': {
            'validate_variable_prefixes': True,
            'validate_argument_descriptions': True,
            'validate_init_end_pattern': False
        }
    }
    
    analyzer_on = BBPPAnalyzer(config=config_on)
    findings_on = analyzer_on.analyze(test_data)
    
    # Debería encontrar:
    # - ClienteNombre sin prefijo in_
    # - ClienteNombre sin descripción
    prefix_findings = [f for f in findings_on if 'prefijo' in f.description.lower() or 'prefix' in str(f.details).lower()]
    desc_findings = [f for f in findings_on if 'descripción' in f.description.lower() or 'description' in str(f.details).lower()]
    
    print(f"   Hallazgos de prefijos: {len(prefix_findings)}")
    print(f"   Hallazgos de descripciones: {len(desc_findings)}")
    
    for f in findings_on:
        print(f"   - {f.rule_name}: {f.description[:50]}...")
    
    # Test 2: Con validaciones desactivadas
    print("\n📋 Test 2: Validaciones DESACTIVADAS")
    config_off = {
        'validations': {
            'validate_variable_prefixes': False,
            'validate_argument_descriptions': False,
            'validate_init_end_pattern': False
        }
    }
    
    analyzer_off = BBPPAnalyzer(config=config_off)
    findings_off = analyzer_off.analyze(test_data)
    
    prefix_findings_off = [f for f in findings_off if 'prefijo' in f.description.lower() or 'prefix' in str(f.details).lower()]
    desc_findings_off = [f for f in findings_off if 'descripción' in f.description.lower() or 'description' in str(f.details).lower()]
    
    print(f"   Hallazgos de prefijos: {len(prefix_findings_off)}")
    print(f"   Hallazgos de descripciones: {len(desc_findings_off)}")
    
    # Verificaciones
    print("\n" + "=" * 60)
    print("RESULTADOS:")
    print("=" * 60)
    
    test_passed = True
    
    # Con validaciones ON debería encontrar más hallazgos
    if len(prefix_findings) > 0 and len(prefix_findings_off) == 0:
        print("✅ Toggle de prefijos funciona correctamente")
    else:
        print("❌ Toggle de prefijos NO funciona")
        test_passed = False
    
    if len(desc_findings) > 0 and len(desc_findings_off) == 0:
        print("✅ Toggle de descripciones funciona correctamente")
    else:
        print("❌ Toggle de descripciones NO funciona")
        test_passed = False
    
    return test_passed


def test_output_options():
    """Verificar que las opciones de output estén configuradas"""
    print("\n" + "=" * 60)
    print("TEST: Opciones de salida en configuración")
    print("=" * 60)
    
    config = load_user_config()
    output = config.get('output', {})
    
    print(f"   generate_html: {output.get('generate_html')}")
    print(f"   generate_excel: {output.get('generate_excel')}")
    print(f"   include_charts: {output.get('include_charts')}")
    
    test_passed = True
    
    if output.get('generate_html') is not None:
        print("✅ generate_html está configurado")
    else:
        print("❌ generate_html es None")
        test_passed = False
    
    if output.get('generate_excel') is not None:
        print("✅ generate_excel está configurado")
    else:
        print("❌ generate_excel es None")
        test_passed = False
    
    if output.get('include_charts') is not None:
        print("✅ include_charts está configurado")
    else:
        print("❌ include_charts es None")
        test_passed = False
    
    return test_passed


def test_excel_generator_import():
    """Verificar que el generador de Excel se puede importar"""
    print("\n" + "=" * 60)
    print("TEST: Importar generador de Excel")
    print("=" * 60)
    
    try:
        from src.excel_report_generator import ExcelReportGenerator, OPENPYXL_AVAILABLE
        print(f"   ✅ ExcelReportGenerator importado")
        print(f"   openpyxl disponible: {OPENPYXL_AVAILABLE}")
        return True
    except ImportError as e:
        print(f"   ❌ Error de importación: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "🧪" * 30)
    print("   TESTS DE CONFIGURACIÓN v0.2.5")
    print("🧪" * 30)
    
    results = []
    
    results.append(("Config Toggles", test_config_toggles()))
    results.append(("Output Options", test_output_options()))
    results.append(("Excel Generator", test_excel_generator_import()))
    
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
