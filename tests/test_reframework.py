import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.getcwd())

from src.project_scanner import ProjectScanner

def test_reframework():
    # Ruta al proyecto REFramework
    project_path = Path(r"C:\Users\Imrik\Documents\UiPath\RoboticEnterpriseFramework")
    
    if not project_path.exists():
        print(f"ERROR: El proyecto no existe en {project_path}")
        return
    
    print(f"Analizando proyecto: {project_path}")
    print("="*60)
    
    try:
        # Crear scanner con los sets activos
        scanner = ProjectScanner(project_path, active_sets=['UiPath', 'NTTData'])
        
        # Ejecutar scan
        results = scanner.scan()
        
        if not results['success']:
            print(f"ERROR en el análisis: {results.get('error')}")
            return
        
        print(f"✓ Análisis completado exitosamente")
        print(f"  - Archivos XAML: {len(results.get('files', []))}")
        print(f"  - Total findings: {len(results.get('findings', []))}")
        
        score = results.get('score', {})
        if isinstance(score, dict):
            print(f"  - Score: {score.get('final_score', 0):.2f}")
        else:
            print(f"  - Score: {score:.2f}")
        
        # Verificar si hay findings de CONFIGURACION_002
        config_002 = [f for f in results.get('findings', []) if f['rule_id'] == 'CONFIGURACION_002']
        if config_002:
            print(f"\n✓ Finding CONFIGURACION_002 detectado:")
            for f in config_002:
                print(f"  - Severidad: {f['severity']}")
                print(f"  - Detalles: {f['details']}")
        else:
            print(f"\n✗ No se detectó finding CONFIGURACION_002")
        
        # Mostrar info del proyecto
        project_info = results.get('project_info', {})
        print(f"\nInformación del proyecto:")
        print(f"  - Studio Version: {project_info.get('studio_version', 'Unknown')}")
        print(f"  - Dependencias: {len(project_info.get('dependencies', []))}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reframework()
