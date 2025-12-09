"""
Test de filtros interactivos
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.project_scanner import ProjectScanner
from src.config import load_user_config

def test_filters():
    project_path = r"C:\Users\Imrik\Documents\UiPath\RoboticEnterpriseFramework"

    if not Path(project_path).exists():
        print(f"❌ Proyecto no encontrado")
        return

    print("="*70)
    print("TEST: FILTROS INTERACTIVOS")
    print("="*70)
    print()

    user_config = load_user_config()
    active_sets = ['UiPath']

    print("⏳ Generando reporte con filtros interactivos...")
    print()

    scanner = ProjectScanner(project_path, user_config, active_sets=active_sets)
    results = scanner.scan()

    if not results.get('success'):
        print(f"❌ Error: {results.get('error')}")
        return

    stats = results.get('statistics', {})
    print("✅ Análisis completado")
    print(f"   Total hallazgos: {len(results.get('findings', []))}")
    print(f"   Por severidad: {stats.get('by_severity', {})}")
    print(f"   Por categoría: {stats.get('by_category', {})}")
    print()

    # Buscar el último reporte
    import glob
    html_reports = glob.glob(r"C:\Users\Imrik\Documents\Proyectos Git\AnalizadorBBPP_UiPath\output\HTML\REPORTE_*.html")

    if html_reports:
        latest_report = max(html_reports, key=lambda x: Path(x).stat().st_mtime)

        print("="*70)
        print("✅ REPORTE CON FILTROS INTERACTIVOS")
        print("="*70)
        print(f"📄 {latest_report}")
        print()
        print("🎯 FUNCIONALIDADES IMPLEMENTADAS:")
        print()
        print("📊 PANEL DE FILTROS:")
        print("   ☑️ Filtrar por Severidad (Errores/Warnings/Info)")
        print("   ☑️ Filtrar por Categoría (Nomenclatura/Try-Catch/etc.)")
        print("   ☑️ Contador dinámico de hallazgos visibles")
        print("   ↺  Botón 'Resetear' para volver a mostrar todos")
        print()
        print("💡 CÓMO USAR:")
        print("   1. Desmarca checkboxes para ocultar hallazgos")
        print("   2. Marca/desmarca para filtrar en tiempo real")
        print("   3. El contador muestra cuántos hallazgos están visibles")
        print("   4. Combina filtros (ej: solo errores de nomenclatura)")
        print()
        print("🌐 Abriendo en navegador...")
        print("="*70)

        import subprocess
        subprocess.Popen(['start', '', latest_report], shell=True)

if __name__ == '__main__':
    test_filters()
