
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.getcwd())

from src.analyzer import BBPPAnalyzer

def run_test(version, expected_severity, expected_issue_snippet):
    analyzer = BBPPAnalyzer()
    project_info = {'studio_version': version, 'dependencies': []}
    
    print(f"\nTesting version: {version}")
    findings = analyzer.analyze_project(project_info)
    
    found = False
    for f in findings:
        if f.rule_id == 'CONFIGURACION_002':
            print(f"  Found finding: [{f.severity}] {f.details.get('issue')}")
            if f.severity == expected_severity and expected_issue_snippet in f.details.get('issue', ''):
                print("  PASS: Expected result matches")
            else:
                print(f"  FAIL: Expected [{expected_severity}] with '{expected_issue_snippet}', got [{f.severity}] with '{f.details.get('issue')}'")
            found = True
            break
            
    if not found:
        if expected_severity is None:
            print("  PASS: No finding found (as expected)")
        else:
            print("  FAIL: No finding found, expected one")

def test_studio_version():
    print("Loading rules...")
    # Trigger rule loading once
    BBPPAnalyzer() 
    
    # 1. Warning: Patch outdated
    run_test('22.10.3', 'warning', 'Versión de parche desactualizada')
    
    # 2. Pass: Exact version
    run_test('22.10.8', None, None)
    
    # 3. Error: Very old version (not in table, e.g. 18.4)
    run_test('18.4.6', 'error', 'Versión no soportada')
    
    # 4. Warning: Newer major version (e.g. 25.10)
    run_test('25.10.0', 'warning', 'Versión superior')

if __name__ == "__main__":
    test_studio_version()
