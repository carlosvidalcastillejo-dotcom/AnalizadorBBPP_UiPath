"""
Script de prueba para verificar que los nuevos campos se guardan correctamente
en un análisis nuevo
"""

import sys
from pathlib import Path

# Añadir path para imports
sys.path.insert(0, str(Path(__file__).parent))

from src.project_scanner import ProjectScanner
from src.database.metrics_db import get_metrics_db

def test_new_analysis():
    """Probar un análisis completo con los nuevos campos"""
    print("=" * 60)
    print("PRUEBA DE ANÁLISIS CON NUEVOS CAMPOS")
    print("=" * 60)
    
    # Ruta a un proyecto de prueba (ajusta según tus proyectos)
    # Usaremos el último proyecto analizado
    db = get_metrics_db()
    history = db.get_analysis_history(limit=1)
    
    if not history:
        print("\n❌ No hay análisis previos en la BD")
        print("   Por favor, ejecuta un análisis desde la aplicación primero")
        db.close()
        return
    
    last_analysis = history[0]
    project_path = Path(last_analysis['project_path'])
    
    print(f"\n📁 Proyecto de prueba: {project_path.name}")
    print(f"   Ruta: {project_path}")
    
    if not project_path.exists():
        print(f"\n❌ El proyecto no existe en: {project_path}")
        db.close()
        return
    
    # Realizar análisis con conjuntos de BBPP específicos
    print("\n🔍 Ejecutando análisis con conjuntos: ['UiPath', 'NTTData']")
    
    scanner = ProjectScanner(
        project_path=project_path,
        active_sets=['UiPath', 'NTTData']
    )
    
    result = scanner.scan()
    
    if result.get('success'):
        print("\n✅ Análisis completado exitosamente")
        
        # Verificar que se guardó en la BD
        analysis_id = result.get('analysis_id')
        if analysis_id:
            print(f"\n📊 Análisis guardado con ID: {analysis_id}")
            
            # Recuperar el análisis de la BD
            saved_analysis = db.get_analysis_by_id(analysis_id)
            
            if saved_analysis:
                print("\n🔍 Verificando campos guardados:")
                print(f"   • Proyecto: {saved_analysis.get('project_name', 'N/A')}")
                print(f"   • Versión Studio: {saved_analysis.get('version', 'N/A')}")
                print(f"   • Conjunto BBPP: {saved_analysis.get('bbpp_sets', 'N/A')}")
                print(f"   • Score: {saved_analysis.get('score', 0):.1f}")
                print(f"   • Total hallazgos: {saved_analysis.get('total_findings', 0)}")
                print(f"   • Fecha: {saved_analysis.get('analysis_date', 'N/A')}")
                
                # Verificar que los campos nuevos tienen valores
                version = saved_analysis.get('version', '')
                bbpp_sets = saved_analysis.get('bbpp_sets', '')
                
                print("\n✅ VERIFICACIÓN FINAL:")
                if version and version != 'Unknown':
                    print(f"   ✅ Versión Studio guardada correctamente: {version}")
                else:
                    print(f"   ⚠️  Versión Studio: {version} (puede ser 'Unknown' si no está en project.json)")
                
                if bbpp_sets and bbpp_sets != 'N/A':
                    print(f"   ✅ Conjunto BBPP guardado correctamente: {bbpp_sets}")
                else:
                    print(f"   ❌ Conjunto BBPP no guardado: {bbpp_sets}")
            else:
                print(f"\n❌ No se pudo recuperar el análisis con ID {analysis_id}")
        else:
            print("\n⚠️  El análisis no tiene ID (no se guardó en BD)")
    else:
        print(f"\n❌ Error en el análisis: {result.get('error', 'Error desconocido')}")
    
    db.close()
    print("\n" + "=" * 60)
    print("PRUEBA COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    test_new_analysis()
