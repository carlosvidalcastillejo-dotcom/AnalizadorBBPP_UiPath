import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.getcwd())

from src.project_scanner import ProjectScanner

def test_config_002():
    project_path = Path(os.getcwd()) / "dummy_project"
    print(f"Analizando: {project_path}")
    print("="*60)
    
    scanner = ProjectScanner(project_path, active_sets=['UiPath', 'NTTData'])
    results = scanner.scan()
    
    if not results['success']:
        print(f"ERROR: {results.get('error')}")
        return
    
    # Buscar findings de CONFIGURACION_002
    all_findings = results.get('findings', [])
    config_002_findings = [f for f in all_findings if f['rule_id'] == 'CONFIGURACION_002']
    
    print(f"\nTotal findings: {len(all_findings)}")
    print(f"Findings CONFIGURACION_002: {len(config_002_findings)}")
    
    if config_002_findings:
        print("\nDetalles de CONFIGURACION_002:")
        for f in config_002_findings:
            print(f"  - Rule ID: {f['rule_id']}")
            print(f"  - Severity: {f['severity']}")
            print(f"  - Description: {f['description']}")
            print(f"  - Location: {f['location']}")
            print(f"  - File: {f['file_path']}")
            print(f"  - Details: {f['details']}")
    else:
        print("\n✗ No se encontró finding CONFIGURACION_002")
    
    # Verificar project_info
    project_info = results.get('project_info', {})
    print(f"\nStudio Version: {project_info.get('studio_version', 'Unknown')}")
    print(f"Archivos XAML: {len(results.get('files', []))}")

if __name__ == "__main__":
    test_config_002()
