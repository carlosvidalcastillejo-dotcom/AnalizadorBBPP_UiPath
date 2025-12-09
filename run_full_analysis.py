
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.getcwd())

from src.project_scanner import ProjectScanner
from src.report_generator import HTMLReportGenerator

def run_analysis():
    project_path = Path(os.getcwd()) / "dummy_project"
    print(f"Analyzing project at: {project_path}")
    
    # Initialize scanner
    scanner = ProjectScanner(project_path, active_sets=['UiPath', 'NTTData'])
    
    # Run scan
    print("Scanning...")
    results = scanner.scan()
    
    if not results['success']:
        print(f"Analysis failed: {results.get('error')}")
        return
        
    print("Analysis complete.")
    
    # Print findings
    print("\nFindings:")
    for finding in results.get('findings', []):
        print(f"[{finding['severity'].upper()}] {finding['rule_id']}: {finding['description']} - {finding['location']}")
        if finding.get('details'):
            print(f"  Details: {finding['details']}")
    print("\n")
    
    # Generate report
    print("Generating HTML report...")
    generator = HTMLReportGenerator(results)
    report_path = generator.generate()
    
    print(f"Report generated at: {report_path}")

if __name__ == "__main__":
    try:
        run_analysis()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
