"""
Test de los dos tipos de reporte: Normal y Detallado
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.project_scanner import ProjectScanner
from src.config import load_user_config

def test_report_types():
    project_path = r"C:\Users\Imrik\Documents\UiPath\RoboticEnterpriseFramework"

    if not Path(project_path).exists():
        print(f"❌ Proyecto no encontrado")
        return

    print("="*70)
    print("TEST: TIPOS DE REPORTE (NORMAL vs DETALLADO)")
    print("="*70)
    print()

    user_config = load_user_config()
    active_sets = ['UiPath']

    print("⏳ Analizando proyecto...")
    print()

    scanner = ProjectScanner(project_path, user_config, active_sets=active_sets)
    results = scanner.scan()

    if not results.get('success'):
        print(f"❌ Error: {results.get('error')}")
        return

    print("✅ Análisis completado")
    print()

    # Generar ambos tipos de reporte
    from src.report_generator import HTMLReportGenerator
    from src.report_utils import get_report_output_dir, generate_report_filename

    project_name = results.get('project_info', {}).get('name', 'Proyecto')
    output_dir = get_report_output_dir('html')

    # 1. Reporte NORMAL
    print("="*70)
    print("📄 GENERANDO REPORTE NORMAL")
    print("="*70)

    normal_filename = generate_report_filename(project_name, 'html').replace('.html', '_NORMAL.html')
    normal_output = output_dir / normal_filename

    generator_normal = HTMLReportGenerator(results, normal_output, report_type="normal")
    normal_path = generator_normal.generate()

    print(f"✅ Reporte Normal generado:")
    print(f"   📄 {normal_path}")
    print()

    # 2. Reporte DETALLADO
    print("="*70)
    print("📊 GENERANDO REPORTE DETALLADO")
    print("="*70)

    detailed_filename = generate_report_filename(project_name, 'html').replace('.html', '_DETALLADO.html')
    detailed_output = output_dir / detailed_filename

    generator_detailed = HTMLReportGenerator(results, detailed_output, report_type="detallado")
    detailed_path = generator_detailed.generate()

    print(f"✅ Reporte Detallado generado:")
    print(f"   📄 {detailed_path}")
    print()

    print("="*70)
    print("🎯 COMPARACIÓN DE REPORTES")
    print("="*70)
    print()
    print("📄 REPORTE NORMAL:")
    print("   • Formato clásico lineal")
    print("   • Resumen, Dependencias, Estadísticas, Hallazgos")
    print("   • Sin pestañas ni filtros interactivos")
    print("   • Todos los hallazgos en una lista simple")
    print("   • Más rápido y directo")
    print()
    print("📊 REPORTE DETALLADO:")
    print("   • Sistema de 3 pestañas (Resumen, Hallazgos, Archivos)")
    print("   • Filtros interactivos por severidad y categoría")
    print("   • Hallazgos colapsables y agrupados por regla")
    print("   • Score individual por archivo XAML")
    print("   • Más completo y visual")
    print()
    print("🌐 Abriendo ambos reportes en navegador...")
    print("="*70)

    import subprocess
    subprocess.Popen(['start', '', str(normal_path)], shell=True)
    subprocess.Popen(['start', '', str(detailed_path)], shell=True)

if __name__ == '__main__':
    test_report_types()
