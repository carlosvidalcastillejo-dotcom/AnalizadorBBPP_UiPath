"""
Módulo para descargar y gestionar el repositorio desde Git/GitHub
"""
import os
import sys
import json
import zipfile
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Callable
import urllib.request
import urllib.error


class GitDownloader:
    """Gestiona la descarga del repositorio desde GitHub"""
    
    def __init__(self, config: dict, progress_callback: Optional[Callable] = None):
        """
        Inicializa el descargador
        
        Args:
            config: Configuración del instalador
            progress_callback: Función callback para reportar progreso (mensaje, porcentaje)
        """
        self.config = config
        self.git_config = config.get('git_config', {})
        self.progress_callback = progress_callback or self._default_progress
        
    def _default_progress(self, message: str, percentage: int):
        """Callback de progreso por defecto"""
        print(f"[{percentage}%] {message}")
    
    def _report_progress(self, message: str, percentage: int):
        """Reporta progreso usando el callback"""
        try:
            self.progress_callback(message, percentage)
        except Exception as e:
            print(f"Error en callback de progreso: {e}")
    
    def check_git_installed(self) -> bool:
        """Verifica si Git está instalado en el sistema"""
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def download_from_github_release(self, install_path: str) -> bool:
        """
        Descarga la última release desde GitHub (sin autenticación)
        
        Args:
            install_path: Ruta donde instalar
            
        Returns:
            True si se descargó exitosamente
        """
        try:
            self._report_progress("Obteniendo información de la última versión...", 10)
            
            # Extraer owner y repo de la URL
            repo_url = self.git_config.get('repository_url', '')
            if 'github.com' not in repo_url:
                return False
            
            # Parsear URL: https://github.com/owner/repo.git
            parts = repo_url.replace('.git', '').split('/')
            owner = parts[-2]
            repo = parts[-1]
            
            # API de GitHub para obtener la última release
            api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
            
            self._report_progress("Conectando con GitHub...", 20)
            
            with urllib.request.urlopen(api_url, timeout=30) as response:
                release_data = json.loads(response.read().decode())
            
            # Buscar el archivo ZIP del código fuente
            zipball_url = release_data.get('zipball_url')
            if not zipball_url:
                return False
            
            self._report_progress("Descargando archivos...", 30)
            
            # Descargar el ZIP
            zip_path = os.path.join(os.path.dirname(install_path), 'temp_download.zip')
            
            def download_progress(block_num, block_size, total_size):
                """Callback para progreso de descarga"""
                if total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(int((downloaded / total_size) * 40) + 30, 70)
                    self._report_progress(
                        f"Descargando... {downloaded // 1024 // 1024}MB / {total_size // 1024 // 1024}MB",
                        percent
                    )
            
            urllib.request.urlretrieve(zipball_url, zip_path, download_progress)
            
            self._report_progress("Extrayendo archivos...", 75)
            
            # Extraer el ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # GitHub crea una carpeta con el nombre owner-repo-commit
                # Necesitamos extraer y mover los archivos
                temp_extract = os.path.join(os.path.dirname(install_path), 'temp_extract')
                zip_ref.extractall(temp_extract)
                
                # Encontrar la carpeta extraída (primera carpeta en temp_extract)
                extracted_folders = [f for f in os.listdir(temp_extract) 
                                   if os.path.isdir(os.path.join(temp_extract, f))]
                
                if extracted_folders:
                    source_folder = os.path.join(temp_extract, extracted_folders[0])
                    
                    # Crear directorio de instalación si no existe
                    os.makedirs(install_path, exist_ok=True)
                    
                    # Mover archivos
                    for item in os.listdir(source_folder):
                        src = os.path.join(source_folder, item)
                        dst = os.path.join(install_path, item)
                        
                        if os.path.exists(dst):
                            if os.path.isdir(dst):
                                shutil.rmtree(dst)
                            else:
                                os.remove(dst)
                        
                        shutil.move(src, dst)
            
            # Limpiar archivos temporales
            self._report_progress("Limpiando archivos temporales...", 90)
            
            if os.path.exists(zip_path):
                os.remove(zip_path)
            if os.path.exists(temp_extract):
                shutil.rmtree(temp_extract)
            
            self._report_progress("Descarga completada", 100)
            return True
            
        except Exception as e:
            print(f"Error descargando desde GitHub Release: {e}")
            return False

    def download_from_branch_zip(self, install_path: str) -> bool:
        """
        Descarga el ZIP directamente desde una rama específica (sin usar API de releases)

        Args:
            install_path: Ruta donde instalar

        Returns:
            True si se descargó exitosamente
        """
        try:
            self._report_progress("Descargando desde GitHub...", 10)

            # Extraer owner y repo de la URL
            repo_url = self.git_config.get('repository_url', '')
            if 'github.com' not in repo_url:
                return False

            # Parsear URL: https://github.com/owner/repo.git
            parts = repo_url.replace('.git', '').split('/')
            owner = parts[-2]
            repo = parts[-1]
            branch = self.git_config.get('branch', 'main')

            # URL directa del ZIP de la rama
            zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"

            self._report_progress(f"Conectando con GitHub (rama {branch})...", 20)

            # Descargar el ZIP en carpeta temporal del sistema
            import tempfile
            temp_dir = tempfile.gettempdir()
            zip_path = os.path.join(temp_dir, 'analizador_bbpp_download.zip')

            def download_progress(block_num, block_size, total_size):
                """Callback para progreso de descarga"""
                if total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(int((downloaded / total_size) * 40) + 30, 70)
                    self._report_progress(
                        f"Descargando... {downloaded // 1024 // 1024}MB / {total_size // 1024 // 1024}MB",
                        percent
                    )

            urllib.request.urlretrieve(zip_url, zip_path, download_progress)

            self._report_progress("Extrayendo archivos...", 75)

            # Extraer el ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # GitHub crea una carpeta con el nombre repo-branch
                temp_extract = os.path.join(temp_dir, 'analizador_bbpp_extract')
                os.makedirs(temp_extract, exist_ok=True)
                zip_ref.extractall(temp_extract)

                # Encontrar la carpeta extraída (repo-branch)
                extracted_folders = [f for f in os.listdir(temp_extract)
                                    if os.path.isdir(os.path.join(temp_extract, f))]

                if not extracted_folders:
                    raise Exception("No se encontró carpeta extraída")

                source_folder = os.path.join(temp_extract, extracted_folders[0])

                # Mover contenidos al path de instalación
                if os.path.exists(install_path):
                    shutil.rmtree(install_path)

                # Crear directorio padre solo si install_path tiene ruta
                parent_dir = os.path.dirname(install_path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)

                shutil.move(source_folder, install_path)

            # Limpiar archivos temporales
            self._report_progress("Limpiando archivos temporales...", 90)

            if os.path.exists(zip_path):
                os.remove(zip_path)
            if os.path.exists(temp_extract):
                shutil.rmtree(temp_extract)

            self._report_progress("Descarga completada", 100)
            return True

        except Exception as e:
            print(f"Error descargando desde rama ZIP: {e}")
            return False

    def download_with_git_clone(self, install_path: str) -> bool:
        """
        Clona el repositorio usando Git
        
        Args:
            install_path: Ruta donde clonar
            
        Returns:
            True si se clonó exitosamente
        """
        try:
            if not self.check_git_installed():
                self._report_progress("Git no está instalado en el sistema", 0)
                return False
            
            self._report_progress("Clonando repositorio con Git...", 20)
            
            repo_url = self.git_config.get('repository_url', '')
            # En producción, siempre intentar usar main a menos que se fuerce otra cosa explícitamente
            branch = self.git_config.get('branch', 'main')
            
            self._report_progress(f"Configurando descarga desde rama: {branch}", 25)

            
            # Crear directorio padre si no existe
            os.makedirs(os.path.dirname(install_path), exist_ok=True)
            
            # Clonar repositorio
            cmd = [
                'git', 'clone',
                '--branch', branch,
                '--depth', '1',  # Solo última versión
                repo_url,
                install_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos máximo
            )
            
            if result.returncode == 0:
                self._report_progress("Repositorio clonado exitosamente", 100)
                return True
            else:
                print(f"Error clonando: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error en git clone: {e}")
            return False
    
    def download(self, install_path: str) -> bool:
        """
        Descarga el repositorio usando el mejor método disponible
        
        Args:
            install_path: Ruta donde instalar
            
        Returns:
            True si se descargó exitosamente
        """
        self._report_progress("Iniciando descarga...", 5)

        # Intentar primero con GitHub Release (no requiere Git ni autenticación)
        if self.git_config.get('use_releases', True):
            if self.download_from_github_release(install_path):
                return True

        # Fallback 1: Descargar ZIP directo de la rama (no requiere Git, siempre usa código actual)
        try:
            if self.download_from_branch_zip(install_path):
                return True
        except Exception as e:
            print(f"Error con descarga directa de rama: {e}")

        # Fallback 2: git clone si está habilitado (requiere Git instalado)
        if self.git_config.get('fallback_to_clone', True):
            if self.download_with_git_clone(install_path):
                return True

        self._report_progress("Error: No se pudo descargar el repositorio", 0)
        return False
    
    def check_for_updates(self, current_version: str) -> Optional[dict]:
        """
        Verifica si hay actualizaciones disponibles
        
        Args:
            current_version: Versión actual instalada
            
        Returns:
            Dict con información de la actualización o None si no hay
        """
        try:
            repo_url = self.git_config.get('repository_url', '')
            if 'github.com' not in repo_url:
                return None
            
            parts = repo_url.replace('.git', '').split('/')
            owner = parts[-2]
            repo = parts[-1]
            
            api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
            
            with urllib.request.urlopen(api_url, timeout=10) as response:
                release_data = json.loads(response.read().decode())
            
            latest_version = release_data.get('tag_name', '').replace('v', '')
            
            if latest_version and latest_version != current_version:
                return {
                    'version': latest_version,
                    'name': release_data.get('name', ''),
                    'body': release_data.get('body', ''),
                    'url': release_data.get('html_url', ''),
                    'published_at': release_data.get('published_at', '')
                }
            
            return None
            
        except Exception as e:
            print(f"Error verificando actualizaciones: {e}")
            return None


if __name__ == "__main__":
    # Test básico
    with open('config_installer.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    downloader = GitDownloader(config)
    
    print("Verificando Git instalado:", downloader.check_git_installed())
    print("\nVerificando actualizaciones...")
    
    update_info = downloader.check_for_updates("1.0.0")
    if update_info:
        print(f"Nueva versión disponible: {update_info['version']}")
    else:
        print("No hay actualizaciones disponibles")
