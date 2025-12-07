"""
Test de hallazgos colapsables
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.project_scanner import ProjectScanner
from src.config import load_user_config

def test_collapsible():
    project_path = r"C:\Users\Imrik\Documents\UiPath\RoboticEnterpriseFramework"

    if not Path(project_path).exists():
        print(f"❌ Proyecto no encontrado")
        return

    print("="*70)
    print("TEST: HALLAZGOS COLAPSABLES")
    print("="*70)
    print()

    user_config = load_user_config()
    active_sets = ['UiPath']

    print("⏳ Generando reporte con hallazgos colapsables...")
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
        print("✅ REPORTE GENERADO CON HALLAZGOS COLAPSABLES")
        print("="*70)
        print(f"📄 {latest_report}")
        print()
        print("🎯 FUNCIONALIDADES IMPLEMENTADAS:")
        print("   ▶️ Click en el título del hallazgo para colapsar/expandir")
        print("   ▶️ Flecha (▼/▶) indica el estado")
        print("   ▶️ Botones 'Expandir Todos' / 'Colapsar Todos'")
        print("   ▶️ Hover sobre título muestra efecto visual")
        print()
        print("🌐 Abriendo en navegador...")
        print("="*70)

        import subprocess
        subprocess.Popen(['start', '', latest_report], shell=True)

if __name__ == '__main__':
    test_collapsible()
