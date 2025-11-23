"""
Tests para el módulo de base de datos de métricas
"""

import sys
from pathlib import Path

# Añadir directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.metrics_db import MetricsDatabase
from datetime import datetime


def test_database_creation():
    """Test de creación de base de datos"""
    print("=" * 70)
    print("TEST: Creación de Base de Datos")
    print("=" * 70)
    
    # Crear BD en memoria para testing
    import tempfile
    temp_db = Path(tempfile.gettempdir()) / 'test_metrics.db'
    
    try:
        db = MetricsDatabase(temp_db)
        print("✅ Base de datos creada correctamente")
        
        # Verificar que las tablas existen
        cursor = db.conn.cursor()
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table'
        ''')
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['analysis_history', 'findings_detail', 'metrics_summary']
        for table in expected_tables:
            if table in tables:
                print(f"✅ Tabla '{table}' creada")
            else:
                print(f"❌ Tabla '{table}' NO encontrada")
        
        db.close()
        
        # Limpiar
        if temp_db.exists():
            temp_db.unlink()
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_save_and_retrieve():
    """Test de guardar y recuperar análisis"""
    print("=" * 70)
    print("TEST: Guardar y Recuperar Análisis")
    print("=" * 70)
    
    import tempfile
    temp_db = Path(tempfile.gettempdir()) / 'test_metrics.db'
    
    try:
        db = MetricsDatabase(temp_db)
        
        # Datos de prueba
        test_analysis = {
            'project_path': 'C:/Projects/TestProject',
            'version': '1.0.0',
            'total_files': 10,
            'analyzed_files': 8,
            'findings': [
                {'severity': 'HIGH', 'rule_id': 'R001', 'rule_name': 'Test Rule', 
                 'category': 'Test', 'file': 'test.xaml', 'location': 'Line 10',
                 'description': 'Test finding'},
                {'severity': 'MEDIUM', 'rule_id': 'R002', 'rule_name': 'Test Rule 2',
                 'category': 'Test', 'file': 'test2.xaml', 'location': 'Line 20',
                 'description': 'Test finding 2'}
            ],
            'score': {'score': 85.5},
            'execution_time': 1.5
        }
        
        # Guardar
        analysis_id = db.save_analysis(test_analysis)
        print(f"✅ Análisis guardado con ID: {analysis_id}")
        
        # Recuperar
        retrieved = db.get_analysis_by_id(analysis_id)
        if retrieved:
            print(f"✅ Análisis recuperado:")
            print(f"   - Proyecto: {retrieved['project_name']}")
            print(f"   - Score: {retrieved['score']}")
            print(f"   - Hallazgos: {retrieved['total_findings']}")
            print(f"   - Detalles: {len(retrieved.get('findings', []))} hallazgos")
        else:
            print("❌ No se pudo recuperar el análisis")
        
        # Obtener historial
        history = db.get_analysis_history()
        print(f"✅ Historial: {len(history)} análisis encontrados")
        
        db.close()
        
        # Limpiar
        if temp_db.exists():
            temp_db.unlink()
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_comparison():
    """Test de comparación de análisis"""
    print("=" * 70)
    print("TEST: Comparación de Análisis")
    print("=" * 70)
    
    import tempfile
    temp_db = Path(tempfile.gettempdir()) / 'test_metrics.db'
    
    try:
        db = MetricsDatabase(temp_db)
        
        # Crear dos análisis
        analysis1 = {
            'project_path': 'C:/Projects/TestProject',
            'version': '1.0.0',
            'total_files': 10,
            'analyzed_files': 8,
            'findings': [{'severity': 'HIGH'}] * 5,
            'score': {'score': 75.0},
            'execution_time': 1.5
        }
        
        analysis2 = {
            'project_path': 'C:/Projects/TestProject',
            'version': '1.1.0',
            'total_files': 10,
            'analyzed_files': 8,
            'findings': [{'severity': 'HIGH'}] * 3,
            'score': {'score': 85.0},
            'execution_time': 1.3
        }
        
        id1 = db.save_analysis(analysis1)
        id2 = db.save_analysis(analysis2)
        
        print(f"✅ Análisis 1 guardado (ID: {id1}, Score: 75.0)")
        print(f"✅ Análisis 2 guardado (ID: {id2}, Score: 85.0)")
        
        # Comparar
        comparison = db.compare_analyses(id1, id2)
        
        if comparison:
            print(f"✅ Comparación realizada:")
            print(f"   - Diferencia de score: {comparison['differences']['score_diff']:+.1f}")
            print(f"   - Diferencia de hallazgos: {comparison['differences']['findings_diff']:+d}")
        else:
            print("❌ No se pudo comparar")
        
        db.close()
        
        # Limpiar
        if temp_db.exists():
            temp_db.unlink()
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 TESTS DE BASE DE DATOS DE MÉTRICAS\n")
    
    results = []
    results.append(("Creación de BD", test_database_creation()))
    results.append(("Guardar/Recuperar", test_save_and_retrieve()))
    results.append(("Comparación", test_comparison()))
    
    print("=" * 70)
    print("RESUMEN DE TESTS")
    print("=" * 70)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    total = len(results)
    passed = sum(1 for _, r in results if r)
    
    print()
    print(f"Total: {passed}/{total} tests pasados ({passed/total*100:.0f}%)")
    print("=" * 70)
