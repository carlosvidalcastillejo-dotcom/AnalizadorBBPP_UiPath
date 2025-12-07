"""
Test para verificar el agrupamiento de hallazgos en reportes HTML
"""
import sys
from pathlib import Path

# Añadir ruta al proyecto
sys.path.insert(0, str(Path(__file__).parent))

from src.project_scanner import ProjectScanner
from src.config import load_user_config

def test_grouped_report():
    # Ruta al proyecto de prueba
    project_path = r"C:\Users\Imrik\Documents\UiPath\RoboticEnterpriseFramework"

    if not Path(project_path).exists():
        print(f"❌ Proyecto no encontrado: {project_path}")
        return

    print("="*60)
    print("TEST: REPORTE AGRUPADO")
    print("="*60)
    print(f"Proyecto: {project_path}")
    print()

    # Cargar configuración
    user_config = load_user_config()

    # Analizar solo con UiPath (para probar)
    active_sets = ['UiPath']

    print(f"Conjuntos BBPP activos: {active_sets}")
    print("Analizando proyecto...")
    print()

    # Ejecutar análisis
    scanner = ProjectScanner(project_path, user_config, active_sets=active_sets)
    results = scanner.scan()

    if not results.get('success'):
        print(f"❌ Error: {results.get('error')}")
        return

    # Mostrar resumen
    stats = results.get('statistics', {})
    findings = results.get('findings', [])

    print("✅ Análisis completado")
    print(f"Total hallazgos: {len(findings)}")
    print(f"  - Errores: {stats.get('by_severity', {}).get('error', 0)}")
    print(f"  - Warnings: {stats.get('by_severity', {}).get('warning', 0)}")
    print(f"  - Info: {stats.get('by_severity', {}).get('info', 0)}")
    print()

    # Agrupar para mostrar preview
    from collections import defaultdict
    grouped = defaultdict(list)

    for finding in findings:
        if finding.get('category') == 'dependencias':
            continue
        key = (finding.get('description'), finding.get('severity'))
        grouped[key].append(finding)

    print("📊 PREVIEW DEL AGRUPAMIENTO:")
    print("-" * 60)
    for (desc, severity), occurrences in sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True):
        count = len(occurrences)
        emoji = "❌" if severity == "error" else "⚠️" if severity == "warning" else "ℹ️"
        print(f"{emoji} [{severity.upper()}] {desc}")
        print(f"   📌 {count} ocurrencia{'s' if count > 1 else ''}")

        # Mostrar primeras 3 ocurrencias
        for occ in occurrences[:3]:
            file_name = Path(occ.get('file_path', '')).name
            location = occ.get('location', '')
            print(f"      📄 {file_name} → {location}")

        if len(occurrences) > 3:
            print(f"      ... y {len(occurrences) - 3} más")
        print()

    # Generar reporte HTML
    print("="*60)
    print("Generando reporte HTML agrupado...")

    from src.report_generator import HTMLReportGenerator

    output_dir = Path("c:/Users/Imrik/Documents/AnalizadorBBPP_UiPath/output")
    output_dir.mkdir(exist_ok=True)

    generator = HTMLReportGenerator(results)
    report_path = generator.generate(output_dir)

    print(f"✅ Reporte generado: {report_path}")
    print()
    print("Abre el reporte en tu navegador para ver el formato agrupado:")
    print(f"file:///{report_path}")
    print("="*60)

if __name__ == '__main__':
    test_grouped_report()
