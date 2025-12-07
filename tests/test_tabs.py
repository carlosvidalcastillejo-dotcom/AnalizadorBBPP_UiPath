"""
Test del sistema de pestañas y score por archivo
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.project_scanner import ProjectScanner
from src.config import load_user_config

def test_tabs():
    project_path = r"C:\Users\Imrik\Documents\UiPath\RoboticEnterpriseFramework"

    if not Path(project_path).exists():
        print(f"❌ Proyecto no encontrado")
        return

    print("="*70)
    print("TEST: SISTEMA DE PESTAÑAS + SCORE POR ARCHIVO")
    print("="*70)
    print()

    user_config = load_user_config()
    active_sets = ['UiPath']

    print("⏳ Generando reporte con pestañas...")
    print()

    scanner = ProjectScanner(project_path, user_config, active_sets=active_sets)
    results = scanner.scan()

    if not results.get('success'):
        print(f"❌ Error: {results.get('error')}")
        return

    print("✅ Análisis completado")
    print()

    # Buscar el último reporte
    import glob
    html_reports = glob.glob(r"C:\Users\Imrik\Documents\Proyectos Git\AnalizadorBBPP_UiPath\output\HTML\REPORTE_*.html")

    if html_reports:
        latest_report = max(html_reports, key=lambda x: Path(x).stat().st_mtime)

        print("="*70)
        print("✅ REPORTE CON SISTEMA DE PESTAÑAS")
        print("="*70)
        print(f"📄 {latest_report}")
        print()
        print("🎯 NUEVAS FUNCIONALIDADES:")
        print()
        print("📑 SISTEMA DE PESTAÑAS:")
        print("   📊 Pestaña 'Resumen': Score global, estadísticas, dependencias")
        print("   📄 Pestaña 'Hallazgos': Hallazgos detallados con filtros")
        print("   📂 Pestaña 'Archivos': Score individual por archivo (NUEVO)")
        print()
        print("📂 SCORE POR ARCHIVO:")
        print("   • Score individual de 0-100 para cada archivo XAML")
        print("   • Clasificación: Excelente/Bueno/Mejorable/Crítico")
        print("   • Contador de hallazgos por severidad")
        print("   • Ordenados de peor a mejor score")
        print("   • Gradientes de color según calidad")
        print("   • Efecto hover con desplazamiento")
        print()
        print("💡 CÓMO USAR:")
        print("   1. Click en las pestañas para navegar")
        print("   2. Pestaña 'Archivos' muestra los archivos problemáticos primero")
        print("   3. Identifica rápidamente qué archivos necesitan atención")
        print()
        print("🌐 Abriendo en navegador...")
        print("="*70)

        import subprocess
        subprocess.Popen(['start', '', latest_report], shell=True)

if __name__ == '__main__':
    test_tabs()
