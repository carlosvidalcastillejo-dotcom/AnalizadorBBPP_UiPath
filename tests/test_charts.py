"""
Test de la pestaña de gráficos en el reporte detallado
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.project_scanner import ProjectScanner
from src.config import load_user_config

def test_charts():
    project_path = r"C:\Users\Imrik\Documents\UiPath\RoboticEnterpriseFramework"

    if not Path(project_path).exists():
        print(f"❌ Proyecto no encontrado")
        return

    print("="*70)
    print("TEST: PESTAÑA DE GRÁFICOS EN REPORTE DETALLADO")
    print("="*70)
    print()

    user_config = load_user_config()
    active_sets = ['UiPath']

    print("⏳ Generando reporte detallado con gráficos...")
    print()

    scanner = ProjectScanner(project_path, user_config, active_sets=active_sets)
    results = scanner.scan()

    if not results.get('success'):
        print(f"❌ Error: {results.get('error')}")
        return

    print("✅ Análisis completado")
    print()

    # Generar reporte detallado
    from src.report_generator import HTMLReportGenerator
    from src.report_utils import get_report_output_dir, generate_report_filename

    project_name = results.get('project_info', {}).get('name', 'Proyecto')
    output_dir = get_report_output_dir('html')
    filename = generate_report_filename(project_name, 'html').replace('.html', '_GRAFICOS.html')
    output_path = output_dir / filename

    generator = HTMLReportGenerator(results, output_path, report_type="detallado")
    report_path = generator.generate()

    print("="*70)
    print("✅ REPORTE DETALLADO CON GRÁFICOS GENERADO")
    print("="*70)
    print(f"📄 {report_path}")
    print()
    print("🎯 NUEVA FUNCIONALIDAD: PESTAÑA DE GRÁFICOS")
    print()
    print("📈 Gráficos Incluidos:")
    print("   1. 📊 Distribución por Severidad (Gráfico de Dona)")
    print("      - Errores, Warnings e Info con porcentajes")
    print("      - Colores distintivos por tipo")
    print()
    print("   2. 🎯 Score Global del Proyecto (Gauge)")
    print("      - Visualización tipo velocímetro")
    print("      - Color dinámico según puntuación")
    print("      - Calificación textual")
    print()
    print("   3. 📂 Hallazgos por Categoría (Barras Horizontales)")
    print("      - Comparación visual entre categorías")
    print("      - Ordenado alfabéticamente")
    print()
    print("   4. 📄 Top 10 Archivos con Más Hallazgos (Barras)")
    print("      - Identifica archivos problemáticos")
    print("      - Ordenado de mayor a menor")
    print()
    print("💡 Características:")
    print("   • Gráficos interactivos con Chart.js")
    print("   • Tooltips informativos al pasar el mouse")
    print("   • Diseño responsive (se adapta a pantalla)")
    print("   • Tarjetas con efecto hover")
    print("   • Grid de 2 columnas en pantallas grandes")
    print()
    print("🌐 Abriendo reporte en navegador...")
    print("="*70)

    import subprocess
    subprocess.Popen(['start', '', str(report_path)], shell=True)

if __name__ == '__main__':
    test_charts()
