"""
Test del agrupamiento multinivel: Regla → Archivo → Ubicaciones
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.project_scanner import ProjectScanner
from src.config import load_user_config

def test_multilevel():
    project_path = r"C:\Users\Imrik\Documents\UiPath\RoboticEnterpriseFramework"

    if not Path(project_path).exists():
        print(f"❌ Proyecto no encontrado: {project_path}")
        return

    print("="*70)
    print("TEST: AGRUPAMIENTO MULTINIVEL (Regla → Archivo → Ubicaciones)")
    print("="*70)
    print()

    user_config = load_user_config()
    active_sets = ['UiPath']

    print(f"📂 Proyecto: {Path(project_path).name}")
    print(f"📋 Conjuntos BBPP: {', '.join(active_sets)}")
    print()
    print("⏳ Analizando proyecto...")
    print()

    scanner = ProjectScanner(project_path, user_config, active_sets=active_sets)
    results = scanner.scan()

    if not results.get('success'):
        print(f"❌ Error: {results.get('error')}")
        return

    findings = results.get('findings', [])
    stats = results.get('statistics', {})

    print("✅ Análisis completado")
    print(f"   Total hallazgos: {len(findings)}")
    print(f"   Errores: {stats.get('by_severity', {}).get('error', 0)}")
    print(f"   Warnings: {stats.get('by_severity', {}).get('warning', 0)}")
    print(f"   Info: {stats.get('by_severity', {}).get('info', 0)}")
    print()

    # Preview del agrupamiento multinivel
    from collections import defaultdict

    grouped_by_rule = defaultdict(list)
    for finding in findings:
        if finding.get('category') == 'dependencias':
            continue
        key = (finding.get('description'), finding.get('severity'))
        grouped_by_rule[key].append(finding)

    print("="*70)
    print("📊 PREVIEW DEL AGRUPAMIENTO MULTINIVEL")
    print("="*70)
    print()

    # Mostrar solo las primeras 2 reglas para preview
    for idx, ((desc, severity), occurrences) in enumerate(list(grouped_by_rule.items())[:2]):
        emoji = "❌" if severity == "error" else "⚠️" if severity == "warning" else "ℹ️"

        print(f"{emoji} [{severity.upper()}] {desc}")
        print(f"   📌 {len(occurrences)} ocurrencias encontradas")
        print()

        # Agrupar por archivo
        by_file = defaultdict(list)
        for occ in occurrences:
            file_name = Path(occ.get('file_path', '')).name
            by_file[file_name].append(occ)

        # Mostrar agrupamiento por archivo
        for file_name, file_occs in sorted(by_file.items())[:3]:  # Primeros 3 archivos
            print(f"   📄 {file_name} ({len(file_occs)} ocurrencia{'s' if len(file_occs) > 1 else ''})")

            for occ in file_occs[:5]:  # Primeras 5 ubicaciones
                location = occ.get('location', '')
                if location:
                    print(f"      📍 {location}")

            if len(file_occs) > 5:
                print(f"      ... y {len(file_occs) - 5} más")

            print()

        if len(by_file) > 3:
            remaining_files = len(by_file) - 3
            remaining_occs = sum(len(occs) for file_name, occs in list(by_file.items())[3:])
            print(f"   ... y {remaining_files} archivos más con {remaining_occs} ocurrencias")

        print()

    if len(grouped_by_rule) > 2:
        print(f"... y {len(grouped_by_rule) - 2} reglas más")
        print()

    # Buscar el último reporte generado
    import glob
    html_reports = glob.glob(r"C:\Users\Imrik\Documents\Proyectos Git\AnalizadorBBPP_UiPath\output\HTML\REPORTE_*.html")

    if html_reports:
        latest_report = max(html_reports, key=lambda x: Path(x).stat().st_mtime)
        print("="*70)
        print("✅ REPORTE HTML GENERADO")
        print("="*70)
        print(f"📄 Ruta: {latest_report}")
        print()
        print("🌐 Abriendo en navegador...")

        import subprocess
        subprocess.Popen(['start', '', latest_report], shell=True)

        print()
        print("✨ Verifica el nuevo formato jerárquico:")
        print("   Regla → Archivo (con contador) → Lista de ubicaciones")
        print("="*70)

if __name__ == '__main__':
    test_multilevel()
