import json
import os
import sys
import urllib.request
import urllib.error
import subprocess
import threading
from pathlib import Path
from typing import Dict, Optional, Tuple, Callable

from src.config import APP_VERSION

class AppUpdater:
    """Gestor de actualizaciones de la aplicación"""
    
    GITHUB_REPO = "carlosvidalcastillejo-dotcom/AnalizadorBBPP_UiPath"
    GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    
    def __init__(self):
        self.latest_release = None
        self.update_available = False
        
    def check_for_updates(self) -> Tuple[bool, Optional[Dict]]:
        """
        Verificar si hay actualizaciones disponibles
        
        Returns:
            (Hay actualización?, Info de release)
        """
        try:
            print(f"Checking updates from: {self.GITHUB_API_URL}")
            with urllib.request.urlopen(self.GITHUB_API_URL, timeout=5) as response:
                if response.status != 200:
                    return False, None
                
                data = json.loads(response.read().decode())
                
                # Obtener versión remota (quitar 'v' si existe)
                remote_version = data.get('tag_name', '').lstrip('v')
                current_version = APP_VERSION.lstrip('v')
                
                print(f"Current: {current_version}, Remote: {remote_version}")
                
                # Comparación simple de versiones
                # TODO: Usar packaging.version para comparación semántica robusta
                if remote_version != current_version:
                    # Asumimos que si son diferentes y no es beta local, es update
                    # Una comparación real necesitaría parsear major.minor.patch
                    
                    # Hack simple: si remote > current lexicográficamente (funciona para 1.0.0 vs 1.0.1)
                    # Pero falla con 1.10.0 vs 1.2.0.
                    # Mejor dividir
                    curr_parts = [int(x) for x in current_version.split('.') if x.isdigit()]
                    rem_parts = [int(x) for x in remote_version.split('.') if x.isdigit()]
                    
                    # Pad con ceros
                    while len(curr_parts) < 3: curr_parts.append(0)
                    while len(rem_parts) < 3: rem_parts.append(0)
                    
                    is_newer = False
                    if rem_parts[0] > curr_parts[0]: is_newer = True
                    elif rem_parts[0] == curr_parts[0] and rem_parts[1] > curr_parts[1]: is_newer = True
                    elif rem_parts[0] == curr_parts[0] and rem_parts[1] == curr_parts[1] and rem_parts[2] > curr_parts[2]: is_newer = True
                    
                    if is_newer:
                        self.latest_release = data
                        self.update_available = True
                        return True, data
                        
            return False, None
            
        except Exception as e:
            print(f"Error checking updates: {e}")
            return False, None
            
    def download_and_install(self, progress_callback: Optional[Callable[[int], None]] = None):
        """
        Descargar instalador y ejecutarlo
        """
        if not self.latest_release:
            return False, "No update info"
            
        try:
            # Buscar asset .exe
            assets = self.latest_release.get('assets', [])
            exe_asset = next((a for a in assets if a['name'].endswith('.exe')), None)
            
            if not exe_asset:
                return False, "No se encontró instalador (.exe) en la release"
                
            download_url = exe_asset['browser_download_url']
            file_name = exe_asset['name']
            
            # Directorio temporal
            import tempfile
            temp_dir = tempfile.gettempdir()
            installer_path = os.path.join(temp_dir, file_name)
            
            # Descargar
            print(f"Downloading update from {download_url} to {installer_path}")
            
            def report_progress(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    percent = int((block_num * block_size / total_size) * 100)
                    progress_callback(min(percent, 100))
            
            urllib.request.urlretrieve(download_url, installer_path, report_progress)
            
            # Ejecutar instalador
            print("Running installer...")
            # Usar start para que no bloquee y salir
            subprocess.Popen([installer_path], shell=True)
            
            return True, installer_path
            
        except Exception as e:
            print(f"Error updating: {e}")
            return False, str(e)

# Singleton global
_updater = None

def get_updater():
    global _updater
    if _updater is None:
        _updater = AppUpdater()
    return _updater
