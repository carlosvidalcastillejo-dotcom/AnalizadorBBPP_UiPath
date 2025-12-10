"""
Test directo del instalador para debug
"""
import sys
import json
from pathlib import Path

# Añadir installer al path
sys.path.insert(0, 'installer')

from git_downloader import GitDownloader

# Cargar config
with open('installer/config_installer.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

print("="*80)
print("TEST INSTALADOR - Descarga desde GitHub")
print("="*80)
print(f"\nConfiguración:")
print(f"  Repository: {config['git_config']['repository_url']}")
print(f"  Branch: {config['git_config']['branch']}")
print(f"  Use releases: {config['git_config']['use_releases']}")
print(f"  Fallback to clone: {config['git_config']['fallback_to_clone']}")

# Crear downloader
def progress_callback(msg, pct):
    print(f"[{pct}%] {msg}")

downloader = GitDownloader(config, progress_callback)

# Probar descarga
test_path = Path("temp_test_install")
if test_path.exists():
    import shutil
    shutil.rmtree(test_path)

print(f"\n{'='*80}")
print("Iniciando descarga...")
print(f"{'='*80}\n")

try:
    result = downloader.download(str(test_path))
    if result:
        print(f"\n{'='*80}")
        print("SUCCESS: Descarga exitosa!")
        print(f"{'='*80}")

        # Ver qué se descargó
        if test_path.exists():
            files = list(test_path.rglob("*"))
            print(f"\nArchivos descargados: {len(files)}")
            print(f"Carpeta: {test_path.absolute()}")

            # Ver primeros 10 archivos
            print("\nPrimeros 10 archivos:")
            for f in files[:10]:
                print(f"  - {f.relative_to(test_path)}")
    else:
        print(f"\n{'='*80}")
        print("ERROR: Descarga falló")
        print(f"{'='*80}")

except Exception as e:
    print(f"\n{'='*80}")
    print(f"EXCEPTION: {type(e).__name__}")
    print(f"Message: {e}")
    print(f"{'='*80}")
    import traceback
    traceback.print_exc()
