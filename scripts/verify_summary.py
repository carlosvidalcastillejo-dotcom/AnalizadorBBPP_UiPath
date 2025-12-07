
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.getcwd())

from src.project_scanner import ProjectScanner

def test_summary():
    # Mock project info with new dependency structure
    project_info = {
        'name': 'Test Project',
        'type': 'Test',
        'studio_version': '22.10.3',
        'dependencies': [
            {
                'name': 'UiPath.Excel.Activities',
                'installed_version': '2.12.3',
                'required_version': '2.12.3',
                'status': 'ok',
                'status_label': 'Actualizada'
            },
            {
                'name': 'UiPath.System.Activities',
                'installed_version': '22.4.0',
                'required_version': '22.10.3',
                'status': 'outdated',
                'status_label': 'Desactualizada'
            }
        ]
    }
    
    scanner = ProjectScanner(Path('.'))
    scanner.project_info = project_info
    scanner.parsed_files = [{'file_path': 'dummy.xaml', 'activities': []}] # Dummy file
    
    print("Generating summary...")
    try:
        summary = scanner.get_summary()
        print("Summary generated successfully!")
        print("-" * 20)
        print(summary)
        print("-" * 20)
    except Exception as e:
        print(f"❌ Error generating summary: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_summary()
