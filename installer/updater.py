"""
Sistema de auto-actualización para la aplicación
"""
import os
import sys
import json
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Callable
from git_downloader import GitDownloader


class Updater:
    """Gestiona las actualizaciones de la aplicación"""
    
    def __init__(self, install_path: str, config_path: Optional[str] = None):
        """
        Inicializa el actualizador
        
        Args:
            install_path: Ruta de instalación de la aplicación
            config_path: Ruta al archivo de configuración del instalador
        """
        self.install_path = install_path
        
        # Cargar configuración
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            # Configuración por defecto
            self.config = {
                'git_config': {
                    'repository_url': 'https://github.com/carlosvidalcastillejo-dotcom/AnalizadorBBPP_UiPath.git',
                    'branch': 'main',
                    'use_releases': True
                }
            }
        
        # Cargar configuración de instalación
        self.installation_config_path = os.path.join(install_path, 'installation_config.json')
        self.installation_config = self.load_installation_config()
    
    def load_installation_config(self) -> dict:
        """Carga la configuración de la instalación"""
        if os.path.exists(self.installation_config_path):
            with open(self.installation_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'version': '0.0.0',
            'auto_update': False
        }
    
    def save_installation_config(self):
        """Guarda la configuración de la instalación"""
        with open(self.installation_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.installation_config, f, indent=2)
    
    def get_current_version(self) -> str:
        """Obtiene la versión actual instalada"""
        return self.installation_config.get('version', '0.0.0')
    
    def check_for_updates(self) -> Optional[dict]:
        """
        Verifica si hay actualizaciones disponibles
        
        Returns:
            Dict con información de la actualización o None si no hay
        """
        try:
            downloader = GitDownloader(self.config)
            current_version = self.get_current_version()
            
            update_info = downloader.check_for_updates(current_version)
            return update_info
            
        except Exception as e:
            print(f"Error verificando actualizaciones: {e}")
            return None
    
    def update(self, progress_callback: Optional[Callable] = None) -> bool:
        """
        Actualiza la aplicación a la última versión
        
        Args:
            progress_callback: Función callback para reportar progreso
            
        Returns:
            True si se actualizó exitosamente
        """
        try:
            if progress_callback:
                progress_callback("Verificando actualizaciones...", 5)
            
            # Verificar si hay actualizaciones
            update_info = self.check_for_updates()
            if not update_info:
                if progress_callback:
                    progress_callback("No hay actualizaciones disponibles", 100)
                return False
            
            if progress_callback:
                progress_callback(f"Descargando versión {update_info['version']}...", 10)
            
            # Crear directorio temporal
            temp_dir = tempfile.mkdtemp(prefix='bbpp_update_')
            
            try:
                # Descargar nueva versión
                downloader = GitDownloader(self.config, progress_callback)
                
                if not downloader.download(temp_dir):
                    return False
                
                if progress_callback:
                    progress_callback("Creando respaldo...", 70)
                
                # Crear backup de la instalación actual
                backup_dir = self.create_backup()
                
                try:
                    if progress_callback:
                        progress_callback("Instalando actualización...", 80)
                    
                    # Copiar archivos nuevos (excepto config y data)
                    self.copy_update_files(temp_dir)
                    
                    # Actualizar versión en configuración
                    self.installation_config['version'] = update_info['version']
                    self.save_installation_config()
                    
                    if progress_callback:
                        progress_callback("Actualización completada", 100)
                    
                    return True
                    
                except Exception as e:
                    # Si falla, restaurar backup
                    if progress_callback:
                        progress_callback("Error en actualización, restaurando...", 90)
                    
                    self.restore_backup(backup_dir)
                    raise e
                    
            finally:
                # Limpiar directorio temporal
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            
        except Exception as e:
            print(f"Error durante la actualización: {e}")
            return False
    
    def create_backup(self) -> str:
        """
        Crea un backup de la instalación actual
        
        Returns:
            Ruta del directorio de backup
        """
        backup_dir = os.path.join(
            os.path.dirname(self.install_path),
            f'backup_{self.get_current_version()}'
        )
        
        # Eliminar backup anterior si existe
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
        
        # Copiar instalación actual
        shutil.copytree(self.install_path, backup_dir)
        
        return backup_dir
    
    def restore_backup(self, backup_dir: str):
        """
        Restaura un backup
        
        Args:
            backup_dir: Ruta del directorio de backup
        """
        if not os.path.exists(backup_dir):
            raise FileNotFoundError(f"Backup no encontrado: {backup_dir}")
        
        # Eliminar instalación actual
        if os.path.exists(self.install_path):
            shutil.rmtree(self.install_path)
        
        # Restaurar backup
        shutil.copytree(backup_dir, self.install_path)
    
    def copy_update_files(self, source_dir: str):
        """
        Copia los archivos de actualización, preservando config y data
        
        Args:
            source_dir: Directorio con los archivos nuevos
        """
        # Directorios/archivos a preservar
        preserve = ['config', 'data', 'output', 'installation_config.json']
        
        for item in os.listdir(source_dir):
            source_path = os.path.join(source_dir, item)
            dest_path = os.path.join(self.install_path, item)
            
            # Saltar elementos a preservar
            if item in preserve:
                continue
            
            # Eliminar destino si existe
            if os.path.exists(dest_path):
                if os.path.isdir(dest_path):
                    shutil.rmtree(dest_path)
                else:
                    os.remove(dest_path)
            
            # Copiar nuevo archivo/directorio
            if os.path.isdir(source_path):
                shutil.copytree(source_path, dest_path)
            else:
                shutil.copy2(source_path, dest_path)
    
    def is_auto_update_enabled(self) -> bool:
        """Verifica si la auto-actualización está habilitada"""
        return self.installation_config.get('auto_update', False)
    
    def set_auto_update(self, enabled: bool):
        """Habilita o deshabilita la auto-actualización"""
        self.installation_config['auto_update'] = enabled
        self.save_installation_config()


class UpdateDialog:
    """Diálogo para notificar y gestionar actualizaciones"""
    
    def __init__(self, update_info: dict, updater: Updater):
        """
        Inicializa el diálogo de actualización
        
        Args:
            update_info: Información de la actualización disponible
            updater: Instancia del actualizador
        """
        import tkinter as tk
        from tkinter import messagebox, scrolledtext
        
        self.update_info = update_info
        self.updater = updater
        
        # Crear ventana
        self.root = tk.Tk()
        self.root.title("Actualización Disponible")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Colores
        self.colors = {
            'bg': '#F5F7FA',
            'primary': '#4A90E2',
            'card_bg': 'white',
            'text_dark': '#2C3E50'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        self.create_ui()
        self.center_window()
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_ui(self):
        """Crea la interfaz del diálogo"""
        import tkinter as tk
        from tkinter import scrolledtext
        
        # Header
        header = tk.Frame(self.root, bg=self.colors['primary'], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="🔄 Nueva Versión Disponible",
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['primary'],
            fg='white'
        )
        title.pack(pady=25)
        
        # Contenido
        content = tk.Frame(self.root, bg=self.colors['card_bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Información de versión
        version_frame = tk.Frame(content, bg=self.colors['card_bg'])
        version_frame.pack(pady=10)
        
        current_label = tk.Label(
            version_frame,
            text=f"Versión actual: {self.updater.get_current_version()}",
            font=('Segoe UI', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text_dark']
        )
        current_label.pack()
        
        new_label = tk.Label(
            version_frame,
            text=f"Nueva versión: {self.update_info['version']}",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['primary']
        )
        new_label.pack()
        
        # Notas de la versión
        notes_label = tk.Label(
            content,
            text="📝 Novedades:",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_dark']
        )
        notes_label.pack(anchor='w', pady=(15, 5))
        
        notes_text = scrolledtext.ScrolledText(
            content,
            height=10,
            font=('Segoe UI', 9),
            wrap=tk.WORD,
            bg='#F8F9FA'
        )
        notes_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        notes_text.insert('1.0', self.update_info.get('body', 'Sin notas de versión'))
        notes_text.config(state=tk.DISABLED)
        
        # Botones
        button_frame = tk.Frame(self.root, bg=self.colors['bg'])
        button_frame.pack(side=tk.BOTTOM, pady=15)
        
        update_btn = tk.Button(
            button_frame,
            text="Actualizar Ahora",
            command=self.start_update,
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['primary'],
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        update_btn.pack(side=tk.LEFT, padx=5)
        
        later_btn = tk.Button(
            button_frame,
            text="Más Tarde",
            command=self.root.destroy,
            font=('Segoe UI', 10),
            bg='#7F8C8D',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        later_btn.pack(side=tk.LEFT, padx=5)
    
    def start_update(self):
        """Inicia el proceso de actualización"""
        import tkinter as tk
        from tkinter import messagebox
        import threading
        
        # Cerrar diálogo
        self.root.destroy()
        
        # Crear ventana de progreso
        progress_window = tk.Tk()
        progress_window.title("Actualizando...")
        progress_window.geometry("400x150")
        progress_window.resizable(False, False)
        
        status_label = tk.Label(
            progress_window,
            text="Iniciando actualización...",
            font=('Segoe UI', 11)
        )
        status_label.pack(pady=20)
        
        from tkinter import ttk
        progress_bar = ttk.Progressbar(
            progress_window,
            length=350,
            mode='determinate'
        )
        progress_bar.pack(pady=10)
        
        def update_progress(message, percentage):
            status_label.config(text=message)
            progress_bar['value'] = percentage
            progress_window.update()
        
        def do_update():
            success = self.updater.update(update_progress)
            progress_window.destroy()
            
            if success:
                messagebox.showinfo(
                    "Actualización Completada",
                    "La aplicación se ha actualizado correctamente.\n"
                    "Por favor, reinicia la aplicación para aplicar los cambios."
                )
            else:
                messagebox.showerror(
                    "Error",
                    "No se pudo completar la actualización."
                )
        
        # Ejecutar actualización en thread
        thread = threading.Thread(target=do_update, daemon=True)
        thread.start()
        
        progress_window.mainloop()
    
    def show(self):
        """Muestra el diálogo"""
        self.root.mainloop()


if __name__ == "__main__":
    # Test básico
    install_path = r"C:\Program Files\AnalizadorBBPP"
    
    updater = Updater(install_path)
    
    print(f"Versión actual: {updater.get_current_version()}")
    print("Verificando actualizaciones...")
    
    update_info = updater.check_for_updates()
    
    if update_info:
        print(f"Nueva versión disponible: {update_info['version']}")
        print(f"Nombre: {update_info['name']}")
    else:
        print("No hay actualizaciones disponibles")
