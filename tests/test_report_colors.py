"""
Script de prueba para verificar los cambios en los colores de severidad
en los reportes HTML y Excel
"""

import sys
from pathlib import Path

# Añadir path para imports
sys.path.insert(0, str(Path(__file__).parent))

from src.database.metrics_db import get_metrics_db
from src.report_generator import HTMLReportGenerator
from src.excel_report_generator import ExcelReportGenerator, OPENPYXL_AVAILABLE

def test_report_colors():
    """Probar que los colores de severidad son correctos en los reportes"""
    print("=" * 70)
    print("PRUEBA DE COLORES DE SEVERIDAD EN REPORTES")
    print("=" * 70)
    
    # Obtener el último análisis de la BD
    db = get_metrics_db()
    history = db.get_analysis_history(limit=1)
    
    if not history:
        print("\n❌ No hay análisis en la base de datos")
        print("   Por favor, ejecuta un análisis desde la aplicación primero")
        db.close()
        return
    
    last_analysis = history[0]
    analysis_id = last_analysis['id']
    
    # Obtener análisis completo
    full_analysis = db.get_analysis_by_id(analysis_id)
    db.close()
    
    if not full_analysis:
        print(f"\n❌ No se pudo recuperar el análisis {analysis_id}")
        return
    
    # Preparar datos para los generadores
    # Necesitamos convertir el formato de la BD al formato esperado por los generadores
    project_path = Path(full_analysis['project_path'])
    
    # Reconstruir el formato de resultados
    results = {
        'success': True,
        'project_path': str(project_path),
        'project_info': {
            'name': full_analysis['project_name'],
            'type': 'Unknown',
            'studio_version': full_analysis.get('version', 'Unknown'),
            'path': str(project_path)
        },
        'total_files': full_analysis.get('total_files', 0),
        'analyzed_files': full_analysis.get('analyzed_files', 0),
        'statistics': {
            'total_findings': full_analysis.get('total_findings', 0),
            'errors': full_analysis.get('high_findings', 0),
            'warnings': full_analysis.get('medium_findings', 0),
            'infos': full_analysis.get('low_findings', 0),
            'by_category': {},
            'total_activities': 0,
            'total_variables': 0,
            'total_arguments': 0,
        },
        'score': {
            'score': full_analysis.get('score', 0),
            'grade': 'A - Excelente' if full_analysis.get('score', 0) >= 90 else 'B - Bien',
            'color': 'green'
        },
        'findings': full_analysis.get('findings', []),
        'parsed_files': []
    }
    
    print(f"\n📁 Proyecto: {results['project_info']['name']}")
    print(f"   Versión Studio: {results['project_info']['studio_version']}")
    print(f"   Total hallazgos: {results['statistics']['total_findings']}")
    print(f"   - Errores: {results['statistics']['errors']}")
    print(f"   - Warnings: {results['statistics']['warnings']}")
    print(f"   - Info: {results['statistics']['infos']}")
    
    # Generar reporte HTML
    print("\n📄 Generando reporte HTML...")
    try:
        html_gen = HTMLReportGenerator(results, report_type="detallado")
        html_path = html_gen.generate()
        print(f"   ✅ HTML generado: {html_path}")
        print(f"   🎨 Colores aplicados:")
        print(f"      - Error: #dc3545 (Rojo) ✅")
        print(f"      - Warning: #ffc107 (Amarillo) ✅")
        print(f"      - Info: #0d6efd (Azul) ✅ ACTUALIZADO")
    except Exception as e:
        print(f"   ❌ Error al generar HTML: {e}")
    
    # Generar reporte Excel
    print("\n📊 Generando reporte Excel...")
    if OPENPYXL_AVAILABLE:
        try:
            excel_gen = ExcelReportGenerator(results, include_charts=True)
            excel_path = excel_gen.generate()
            print(f"   ✅ Excel generado: {excel_path}")
            print(f"   🎨 Colores aplicados:")
            print(f"      - Error: DC3545 (Rojo) ✅")
            print(f"      - Warning: FFC107 (Amarillo) ✅")
            print(f"      - Info: 0D6EFD (Azul) ✅ ACTUALIZADO")
            print(f"   📋 Mejoras de formato:")
            print(f"      - Filas alternadas en tabla de hallazgos ✅")
            print(f"      - Colores de fondo para severidades ✅")
            print(f"      - Bordes en todas las celdas ✅")
            print(f"      - Primera fila congelada ✅")
            print(f"      - Mejor alineación de texto ✅")
        except Exception as e:
            print(f"   ❌ Error al generar Excel: {e}")
    else:
        print(f"   ⚠️  openpyxl no disponible - Excel no generado")
    
    print("\n" + "=" * 70)
    print("PRUEBA COMPLETADA")
    print("=" * 70)
    print("\n💡 Abre los reportes generados para verificar los colores:")
    print(f"   HTML: {html_path if 'html_path' in locals() else 'No generado'}")
    print(f"   Excel: {excel_path if 'excel_path' in locals() else 'No generado'}")

if __name__ == "__main__":
    test_report_colors()
