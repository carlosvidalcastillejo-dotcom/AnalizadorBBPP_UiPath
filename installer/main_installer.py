"""
Script principal del instalador
Punto de entrada para el instalador de Analizador BBPP UiPath
"""
import sys
import os

# Añadir el directorio actual al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from installer_gui import InstallerGUI


def main():
    """Función principal del instalador"""
    try:
        # Crear y ejecutar la interfaz del instalador
        app = InstallerGUI()
        app.run()
        
    except Exception as e:
        import traceback
        error_msg = f"Error fatal en el instalador:\n{str(e)}\n\n{traceback.format_exc()}"
        
        try:
            from tkinter import messagebox
            messagebox.showerror("Error Fatal", error_msg)
        except:
            print(error_msg)
        
        sys.exit(1)


if __name__ == "__main__":
    main()
