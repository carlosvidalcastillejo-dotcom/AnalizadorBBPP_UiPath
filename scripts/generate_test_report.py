"""
Script para generar un reporte de prueba con el gráfico de colores actualizado
"""

import sys
from pathlib import Path

# Añadir path para imports
sys.path.insert(0, str(Path(__file__).parent))

from src.database.metrics_db import get_metrics_db
from src.project_scanner import ProjectScanner

def generate_test_report():
    """Generar un nuevo análisis y reporte para verificar los colores del gráfico"""
    print("=" * 70)
    print("GENERACIÓN DE REPORTE DE PRUEBA CON COLORES ACTUALIZADOS")
    print("=" * 70)
    
    # Obtener el último proyecto analizado
    db = get_metrics_db()
    history = db.get_analysis_history(limit=1)
    
    if not history:
        print("\n❌ No hay análisis en la base de datos")
        print("   Por favor, ejecuta un análisis desde la aplicación primero")
        db.close()
        return
    
    last_analysis = history[0]
    project_path = Path(last_analysis['project_path'])
    db.close()
    
    print(f"\n📁 Proyecto: {project_path.name}")
    print(f"   Ruta: {project_path}")
    
    if not project_path.exists():
        print(f"\n❌ El proyecto no existe en: {project_path}")
        return
    
    # Realizar nuevo análisis
    print("\n🔍 Ejecutando análisis completo...")
    print("   Conjuntos BBPP: UiPath, NTTData")
    
    scanner = ProjectScanner(
        project_path=project_path,
        active_sets=['UiPath', 'NTTData']
    )
    
    def progress_callback(file_name, percentage):
        """Mostrar progreso del análisis"""
        print(f"   Analizando: {file_name} ({percentage:.1f}%)", end='\r')
    
    result = scanner.scan(progress_callback=progress_callback)
    
    print("\n")  # Nueva línea después del progreso
    
    if result.get('success'):
        print("✅ Análisis completado exitosamente")
        
        # Información del análisis
        stats = result.get('statistics', {})
        score = result.get('score', {})
        
        print(f"\n📊 Resultados:")
        print(f"   Score: {score.get('score', 0):.1f}/100 - {score.get('grade', 'N/A')}")
        print(f"   Total hallazgos: {stats.get('total_findings', 0)}")
        print(f"   - ❌ Errores: {stats.get('errors', 0)}")
        print(f"   - ⚠️  Warnings: {stats.get('warnings', 0)}")
        print(f"   - ℹ️  Info: {stats.get('infos', 0)}")
        
        # Obtener rutas de reportes generados
        analysis_id = result.get('analysis_id')
        
        if analysis_id:
            print(f"\n📄 Reportes generados (ID: {analysis_id}):")
            
            # Buscar reportes en la carpeta output
            from src.config import OUTPUT_DIR
            
            html_dir = OUTPUT_DIR / 'HTML'
            excel_dir = OUTPUT_DIR / 'Excel'
            
            # Buscar el reporte más reciente
            if html_dir.exists():
                html_files = sorted(html_dir.glob('*.html'), key=lambda x: x.stat().st_mtime, reverse=True)
                if html_files:
                    print(f"   📄 HTML: {html_files[0]}")
            
            if excel_dir.exists():
                excel_files = sorted(excel_dir.glob('*.xlsx'), key=lambda x: x.stat().st_mtime, reverse=True)
                if excel_files:
                    excel_path = excel_files[0]
                    print(f"   📊 Excel: {excel_path}")
                    print(f"\n🎨 GRÁFICO DE COLORES ACTUALIZADO:")
                    print(f"   ✅ Abre el archivo Excel y ve a la hoja 'Resumen'")
                    print(f"   ✅ El gráfico 'Distribución por Severidad' mostrará:")
                    print(f"      🔴 Errores en ROJO")
                    print(f"      🟡 Warnings en AMARILLO")
                    print(f"      🔵 Info en AZUL")
                    
                    # Intentar abrir el archivo Excel automáticamente
                    print(f"\n💡 Abriendo Excel automáticamente...")
                    try:
                        import os
                        import platform
                        
                        if platform.system() == 'Windows':
                            os.startfile(str(excel_path))
                            print(f"   ✅ Excel abierto correctamente")
                        else:
                            print(f"   ⚠️  Abre manualmente: {excel_path}")
                    except Exception as e:
                        print(f"   ⚠️  No se pudo abrir automáticamente: {e}")
                        print(f"   💡 Abre manualmente: {excel_path}")
        else:
            print("\n⚠️  No se guardó el ID del análisis")
    else:
        print(f"\n❌ Error en el análisis: {result.get('error', 'Error desconocido')}")
    
    print("\n" + "=" * 70)
    print("GENERACIÓN COMPLETADA")
    print("=" * 70)

if __name__ == "__main__":
    generate_test_report()
