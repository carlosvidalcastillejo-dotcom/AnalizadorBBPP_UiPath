import tkinter as tk
from tkinter import ttk, messagebox
import threading
from src.updater import get_updater
from src.config import PRIMARY_COLOR, SECONDARY_COLOR, BG_COLOR, COLOR_SUCCESS

class UpdateDialog(tk.Toplevel):
    """Diálogo de actualización disponible"""
    
    def __init__(self, parent, release_info):
        super().__init__(parent)
        self.title("Actualización Disponible")
        self.geometry("600x450")
        self.resizable(False, False)
        self.configure(bg=BG_COLOR)
        
        self.release_info = release_info
        self.updater = get_updater()
        
        self.transient(parent)
        self.grab_set()
        
        self._create_ui()
        self._center_window()
        
    def _create_ui(self):
        # Título
        header_frame = tk.Frame(self, bg=PRIMARY_COLOR, height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame, 
            text="✨ ¡Nueva Versión Disponible!", 
            font=("Arial", 16, "bold"),
            bg=PRIMARY_COLOR, 
            fg="white"
        ).pack(centerY=True)
        
        content = tk.Frame(self, bg=BG_COLOR, padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        version = self.release_info.get('tag_name', 'Unknown')
        tk.Label(
            content,
            text=f"Versión {version} está lista para instalar.",
            font=("Arial", 12),
            bg=BG_COLOR
        ).pack(anchor="w", pady=(0, 10))
        
        # Changelog
        tk.Label(content, text="Novedades:", font=("Arial", 10, "bold"), bg=BG_COLOR).pack(anchor="w")
        
        text_frame = tk.Frame(content, bg="white", relief=tk.SUNKEN, bd=1)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.changelog = tk.Text(text_frame, height=10, font=("Consolas", 9), wrap=tk.WORD, bg="white", relief=tk.FLAT)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.changelog.yview)
        
        self.changelog.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.changelog.configure(yscrollcommand=scrollbar.set)
        self.changelog.insert("1.0", self.release_info.get('body', 'Sin detalles.'))
        self.changelog.configure(state="disabled")
        
        # ProgressBar
        self.progress = ttk.Progressbar(content, orient="horizontal", length=100, mode="determinate")
        self.progress.pack(fill=tk.X, pady=10)
        self.progress.pack_forget() # Ocultar inicialmente
        
        self.status_lbl = tk.Label(content, text="", bg=BG_COLOR, fg="gray", font=("Arial", 9))
        self.status_lbl.pack(pady=(0, 10))
        
        # Botones
        btn_frame = tk.Frame(self, bg=BG_COLOR, padx=20, pady=20)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        tk.Button(
            btn_frame,
            text="Más tarde",
            command=self.destroy,
            bg="#E0E0E0",
            relief=tk.FLAT,
            padx=15
        ).pack(side=tk.RIGHT)
        
        self.update_btn = tk.Button(
            btn_frame,
            text="⬇ Actualizar Ahora",
            command=self._start_update,
            bg=COLOR_SUCCESS,
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15
        )
        self.update_btn.pack(side=tk.RIGHT, padx=10)
        
    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f'{w}x{h}+{x}+{y}')
        
    def _start_update(self):
        self.update_btn.config(state="disabled", text="Descargando...")
        self.progress.pack(fill=tk.X, pady=10)
        self.status_lbl.config(text="Iniciando descarga...")
        
        def run_thread():
            success, result = self.updater.download_and_install(self._update_progress)
            
            if success:
                self.after(0, self._on_download_complete, result)
            else:
                self.after(0, self._on_error, result)
        
        threading.Thread(target=run_thread, daemon=True).start()
        
    def _update_progress(self, percent):
        self.after(0, lambda: self.progress.configure(value=percent))
        self.after(0, lambda: self.status_lbl.config(text=f"Descargando... {percent}%"))
        
    def _on_download_complete(self, path):
        self.status_lbl.config(text="Descarga completada. Iniciando instalador...")
        messagebox.showinfo(
            "Actualización Lista", 
            "La aplicación se cerrará para iniciar la instalación.",
            parent=self
        )
        self.quit()
        import sys
        sys.exit(0)
        
    def _on_error(self, error_msg):
        self.update_btn.config(state="normal", text="Reintentar")
        self.status_lbl.config(text="Error en la descarga")
        messagebox.showerror("Error", f"Fallo al actualizar: {error_msg}", parent=self)
