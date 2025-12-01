"""
Script para integrar el sistema de auto-actualización en la aplicación principal
"""
import os
import sys
import shutil
from pathlib import Path


def integrate_updater():
    """Integra el módulo de actualización en la aplicación principal"""
    
    print("🔄 Integrando sistema de auto-actualización...")
    
    # Rutas
    installer_dir = Path(__file__).parent
    src_dir = installer_dir.parent / 'src'
    
    # Copiar módulo updater a src
    updater_source = installer_dir / 'updater.py'
    updater_dest = src_dir / 'updater.py'
    
    shutil.copy2(updater_source, updater_dest)
    print(f"✓ Copiado updater.py a {updater_dest}")
    
    # Copiar git_downloader a src
    downloader_source = installer_dir / 'git_downloader.py'
    downloader_dest = src_dir / 'git_downloader.py'
    
    shutil.copy2(downloader_source, downloader_dest)
    print(f"✓ Copiado git_downloader.py a {downloader_dest}")
    
    # Copiar configuración del instalador
    config_source = installer_dir / 'config_installer.json'
    config_dest = src_dir.parent / 'config' / 'installer_config.json'
    
    shutil.copy2(config_source, config_dest)
    print(f"✓ Copiado config_installer.json a {config_dest}")
    
    print("\n✅ Integración completada")
    print("\n📝 Próximos pasos:")
    print("   1. Añade el código de verificación de actualizaciones en main.py")
    print("   2. Añade un menú 'Ayuda > Buscar actualizaciones' en la UI")
    print("   3. Opcionalmente, verifica actualizaciones al iniciar la app")


def create_update_menu_example():
    """Crea un ejemplo de código para añadir al menú de la aplicación"""
    
    example_code = '''
# Ejemplo de código para añadir al menú de la aplicación principal
# Añadir en src/ui/main_window.py

def create_help_menu(self):
    """Crea el menú de Ayuda"""
    help_menu = tk.Menu(self.menubar, tearoff=0)
    self.menubar.add_cascade(label="Ayuda", menu=help_menu)
    
    help_menu.add_command(label="Buscar actualizaciones", command=self.check_for_updates)
    help_menu.add_separator()
    help_menu.add_command(label="Acerca de", command=self.show_about)

def check_for_updates(self):
    """Verifica si hay actualizaciones disponibles"""
    try:
        from updater import Updater, UpdateDialog
        import os
        
        # Obtener ruta de instalación
        install_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Crear actualizador
        updater = Updater(install_path)
        
        # Verificar actualizaciones
        update_info = updater.check_for_updates()
        
        if update_info:
            # Mostrar diálogo de actualización
            dialog = UpdateDialog(update_info, updater)
            dialog.show()
        else:
            from tkinter import messagebox
            messagebox.showinfo(
                "Actualizaciones",
                "Ya tienes la última versión instalada."
            )
    
    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror(
            "Error",
            f"No se pudo verificar actualizaciones:\\n{str(e)}"
        )

# Opcionalmente, verificar actualizaciones al iniciar
def check_updates_on_startup(self):
    """Verifica actualizaciones al iniciar (si está habilitado)"""
    try:
        from updater import Updater
        import os
        
        install_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        updater = Updater(install_path)
        
        # Solo verificar si está habilitado
        if updater.is_auto_update_enabled():
            # Verificar en segundo plano
            import threading
            
            def check():
                update_info = updater.check_for_updates()
                if update_info:
                    # Mostrar notificación
                    self.show_update_notification(update_info, updater)
            
            thread = threading.Thread(target=check, daemon=True)
            thread.start()
    
    except Exception as e:
        print(f"Error verificando actualizaciones: {e}")

def show_update_notification(self, update_info, updater):
    """Muestra una notificación de actualización disponible"""
    from tkinter import messagebox
    
    result = messagebox.askyesno(
        "Actualización Disponible",
        f"Hay una nueva versión disponible: {update_info['version']}\\n\\n"
        f"¿Deseas actualizar ahora?\\n\\n"
        f"Nota: La aplicación se cerrará y reiniciará después de actualizar."
    )
    
    if result:
        from updater import UpdateDialog
        dialog = UpdateDialog(update_info, updater)
        dialog.show()
'''
    
    example_file = Path(__file__).parent / 'integration_example.py'
    with open(example_file, 'w', encoding='utf-8') as f:
        f.write(example_code)
    
    print(f"\n✓ Ejemplo de integración guardado en: {example_file}")


def main():
    """Función principal"""
    print("=" * 60)
    print("🔧 INTEGRACIÓN DE AUTO-ACTUALIZACIÓN")
    print("=" * 60)
    print()
    
    try:
        # Integrar módulos
        integrate_updater()
        
        # Crear ejemplo de código
        create_update_menu_example()
        
        print("\n" + "=" * 60)
        print("✅ INTEGRACIÓN COMPLETADA")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
