import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from src.rules_manager import get_rules_manager

class BBPPSetCreatorDialog(tk.Toplevel):
    """Diálogo para crear nuevos conjuntos de BBPP"""
    
    def __init__(self, parent, on_create_callback: Optional[Callable] = None):
        super().__init__(parent)
        self.title("Crear Nuevo Conjunto BBPP")
        self.geometry("600x500")
        self.resizable(False, False)
        
        self.on_create_callback = on_create_callback
        self.rules_manager = get_rules_manager()
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        # UI
        self._create_widgets()
        self._center_window()
        
    def _create_widgets(self):
        """Crear elementos de la interfaz"""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="Nuevo Conjunto de Reglas", 
            font=("Segoe UI", 16, "bold")
        )
        title_label.pack(pady=(0, 20), anchor="w")
        
        # Formulario
        form_frame = ttk.LabelFrame(main_frame, text="Información General", padding="15")
        form_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Nombre
        ttk.Label(form_frame, text="Nombre del Conjunto:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(form_frame, textvariable=self.name_var, width=40)
        self.name_entry.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        ttk.Label(form_frame, text="(Solo letras, números y _)", font=("Segoe UI", 8)).grid(row=0, column=2, sticky="w")
        
        # Descripción
        ttk.Label(form_frame, text="Descripción:").grid(row=1, column=0, sticky="w", pady=5)
        self.desc_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.desc_var, width=40).grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # Autor
        ttk.Label(form_frame, text="Autor:").grid(row=2, column=0, sticky="w", pady=5)
        self.author_var = tk.StringVar(value="Usuario")
        ttk.Entry(form_frame, textvariable=self.author_var, width=40).grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        # Sección de Copia
        copy_frame = ttk.LabelFrame(main_frame, text="Reglas Iniciales", padding="15")
        copy_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Selector de Origen
        select_frame = ttk.Frame(copy_frame)
        select_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.copy_mode = tk.BooleanVar(value=True)
        ttk.Radiobutton(select_frame, text="Copiar de existente", variable=self.copy_mode, value=True, command=self._toggle_copy_mode).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(select_frame, text="Conjunto vacío", variable=self.copy_mode, value=False, command=self._toggle_copy_mode).pack(side=tk.LEFT)
        
        # Combo de conjuntos
        self.source_set_var = tk.StringVar()
        sets = list(self.rules_manager.get_sets_info().keys())
        self.source_combo = ttk.Combobox(select_frame, textvariable=self.source_set_var, values=sets, state="readonly", width=30)
        if sets:
            self.source_combo.current(0)
        self.source_combo.pack(side=tk.LEFT, padx=15)
        
        # Lista de reglas (placeholder visual por ahora, en v2 se podría seleccionar qué reglas copiar)
        self.rules_info_label = ttk.Label(copy_frame, text="Se copiarán todas las reglas del conjunto seleccionado.", foreground="gray")
        self.rules_info_label.pack(anchor="w", pady=10)
        
        # Botones de Acción
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Crear Conjunto", command=self._create_set, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)
        
    def _toggle_copy_mode(self):
        """Habilitar/deshabilitar selección de origen"""
        if self.copy_mode.get():
            self.source_combo.config(state="readonly")
            self.rules_info_label.config(text="Se copiarán todas las reglas del conjunto seleccionado.")
        else:
            self.source_combo.config(state="disabled")
            self.rules_info_label.config(text="Se creará un conjunto sin reglas.")
            
    def _create_set(self):
        """Validar y crear el conjunto"""
        name = self.name_var.get().strip()
        description = self.desc_var.get().strip()
        author = self.author_var.get().strip()
        
        if not name:
            messagebox.showerror("Error", "El nombre es obligatorio", parent=self)
            return
            
        if not description:
            messagebox.showerror("Error", "La descripción es obligatoria", parent=self)
            return
            
        # Preparar parámetros
        copy_from = None
        if self.copy_mode.get():
            copy_from = self.source_set_var.get()
            
        # Crear
        success = self.rules_manager.create_new_set(
            set_name=name,
            description=description,
            author=author,
            copy_from=copy_from
        )
        
        if success:
            messagebox.showinfo("Éxito", f"Conjunto '{name}' creado correctamente", parent=self)
            if self.on_create_callback:
                self.on_create_callback()
            self.destroy()
        else:
            messagebox.showerror("Error", "No se pudo crear el conjunto. Verifica que el nombre sea válido y no exista ya.", parent=self)

    def _center_window(self):
        """Centrar ventana en pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
