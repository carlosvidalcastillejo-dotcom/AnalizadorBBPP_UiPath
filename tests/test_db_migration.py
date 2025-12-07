"""
Script de prueba para verificar la migración de BD y los nuevos campos
"""

import sys
from pathlib import Path

# Añadir path para imports
sys.path.insert(0, str(Path(__file__).parent))

from src.database.metrics_db import get_metrics_db

def test_database_migration():
    """Probar que la migración de BD funciona correctamente"""
    print("=" * 60)
    print("PRUEBA DE MIGRACIÓN DE BASE DE DATOS")
    print("=" * 60)
    
    # Obtener instancia de BD
    db = get_metrics_db()
    
    # Verificar que las columnas existen
    cursor = db.conn.cursor()
    cursor.execute("PRAGMA table_info(analysis_history)")
    columns = {column[1]: column[2] for column in cursor.fetchall()}
    
    print("\n✅ Columnas en la tabla analysis_history:")
    for col_name, col_type in columns.items():
        print(f"   • {col_name}: {col_type}")
    
    # Verificar columnas específicas
    required_columns = ['version', 'bbpp_sets', 'html_report_path', 'excel_report_path']
    print("\n🔍 Verificando columnas requeridas:")
    for col in required_columns:
        if col in columns:
            print(f"   ✅ {col}: Existe")
        else:
            print(f"   ❌ {col}: NO EXISTE")
    
    # Obtener algunos análisis para verificar datos
    print("\n📊 Últimos 5 análisis en la base de datos:")
    history = db.get_analysis_history(limit=5)
    
    if history:
        for i, analysis in enumerate(history, 1):
            print(f"\n   {i}. Análisis ID: {analysis['id']}")
            print(f"      Proyecto: {analysis.get('project_name', 'N/A')}")
            print(f"      Versión Studio: {analysis.get('version', 'N/A')}")
            print(f"      Conjunto BBPP: {analysis.get('bbpp_sets', 'N/A')}")
            print(f"      Fecha: {analysis.get('analysis_date', 'N/A')}")
            print(f"      Score: {analysis.get('score', 0):.1f}")
    else:
        print("   ℹ️  No hay análisis en la base de datos todavía")
    
    db.close()
    print("\n" + "=" * 60)
    print("PRUEBA COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    test_database_migration()
