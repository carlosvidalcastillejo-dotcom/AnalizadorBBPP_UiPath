"""
Test para el detector de cambios automático
Verifica que el sistema detecte archivos modificados correctamente
"""

import sys
from pathlib import Path

# Añadir directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.change_detector import get_change_summary


def test_change_detection():
    """Test de detección de cambios"""
    print("=" * 70)
    print("TEST: Detector de Cambios Automático")
    print("=" * 70)
    print()
    
    # Obtener raíz del proyecto
    project_root = Path(__file__).parent.parent
    
    # Detectar cambios en últimas 24 horas
    summary = get_change_summary(project_root, hours=24)
    
    # Mostrar resultados
    print(f"📊 Archivos detectados: {summary['total_files']}")
    print(f"📈 Tipo de cambio sugerido: {summary['suggested_bump'].upper()}")
    print()
    
    if summary['total_files'] > 0:
        print("📋 Descripción generada:")
        print("=" * 70)
        print(summary['description'])
        print("=" * 70)
        print()
        
        # Mostrar algunos archivos detectados
        print("📁 Archivos modificados (primeros 10):")
        for i, file_info in enumerate(summary['files'][:10], 1):
            print(f"  {i}. {file_info['path']} ({file_info['modified_time']})")
        
        if summary['total_files'] > 10:
            print(f"  ... y {summary['total_files'] - 10} más")
    else:
        print("ℹ️  No se detectaron cambios en las últimas 24 horas")
    
    print()
    print("=" * 70)
    print("✅ Test completado")
    print("=" * 70)
    
    return summary


if __name__ == "__main__":
    test_change_detection()
