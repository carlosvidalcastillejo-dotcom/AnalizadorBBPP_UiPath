#!/usr/bin/env python3
"""
Script de prueba del analizador
Prueba el análisis sin necesidad de UI
"""

import sys
from pathlib import Path

# Agregar src al path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from src.project_scanner import ProjectScanner
from src.config import DEFAULT_CONFIG
from src.report_generator import HTMLReportGenerator


def test_analysis(project_path):
    """Probar análisis de un proyecto"""
    print("=" * 70)
    print("  TEST - Analizador de Buenas Prácticas UiPath")
    print("=" * 70)
    print()
    
    project_path = Path(project_path)
    
    if not project_path.exists():
        print(f"❌ Error: La carpeta {project_path} no existe")
        return
    
    print(f"📁 Proyecto: {project_path.name}")
    print(f"📂 Ruta: {project_path}")
    print()
    print("Iniciando análisis...")
    print()
    
    # Callback para mostrar progreso
    def progress_callback(file_name, percentage):
        print(f"[{int(percentage):3d}%] Analizando: {file_name}")
    
    # Crear escáner
    scanner = ProjectScanner(project_path, DEFAULT_CONFIG)
    
    # Ejecutar análisis
    results = scanner.scan(progress_callback)
    
    if not results.get('success'):
        print(f"\n❌ Error: {results.get('error')}")
        return
    
    # Mostrar resumen
    print()
    print(scanner.get_summary())
    
    # Generar reporte HTML
    print()
    print("📄 Generando reporte HTML...")
    
    timestamp = Path(__file__).stem
    output_file = ROOT_DIR / "output" / f"test_reporte_{project_path.name}.html"
    
    generator = HTMLReportGenerator(results, output_file)
    report_path = generator.generate()
    
    print(f"✅ Reporte generado: {report_path}")
    print()
    print(f"Abre el reporte en tu navegador:")
    print(f"  file://{report_path.absolute()}")
    print()
    
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_analysis.py <ruta_al_proyecto_uipath>")
        print()
        print("Ejemplo:")
        print("  python test_analysis.py /ruta/a/tu/proyecto/UiPath")
        sys.exit(1)
    
    project_path = sys.argv[1]
    test_analysis(project_path)
