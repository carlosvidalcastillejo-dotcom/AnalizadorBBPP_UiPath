import tkinter as tk
from tkinter import ttk, messagebox
from src.ai.ai_manager import get_ai_manager
from src.config import BG_COLOR, PRIMARY_COLOR, TEXT_COLOR, SECONDARY_COLOR, COLOR_SUCCESS

class AIConfigComponent:
    """Componente de interfaz para configuración de IA"""
    
    def __init__(self, parent):
        """
        Inicializar componente
        
        Args:
            parent: Widget padre donde se insertará el componente
        """
        self.parent = parent
        self.ai_manager = get_ai_manager()
        self.config = self.ai_manager.get_config()
        
        # Variables
        self.enabled_var = tk.BooleanVar(value=self.config.get('enabled', False))
        self.provider_var = tk.StringVar(value=self.config.get('provider', 'openai'))
        self.api_key_var = tk.StringVar(value=self.config.get('api_key', ''))
        self.model_var = tk.StringVar(value=self.config.get('model', ''))
        
        self._create_ui()
        
    def _create_ui(self):
        """Crear elementos de UI"""
        # Frame principal
        self.main_frame = tk.Frame(self.parent, bg=BG_COLOR)
        self.main_frame.pack(fill=tk.X, padx=40, pady=10)
        
        # Checkbox Habilitar
        self.enable_check = tk.Checkbutton(
            self.main_frame,
            text="🤖 Habilitar Integración con IA",
            variable=self.enabled_var,
            command=self._toggle_enabled,
            bg=BG_COLOR,
            font=("Arial", 11, "bold"),
            fg=PRIMARY_COLOR,
            selectcolor=BG_COLOR
        )
        self.enable_check.pack(anchor="w", pady=(0, 10))
        
        # Contenedor de opciones (deshabilitado si no está activo)
        self.options_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        self.options_frame.pack(fill=tk.X, padx=20)
        
        # Proveedor
        tk.Label(
            self.options_frame,
            text="Proveedor:",
            bg=BG_COLOR,
            font=("Arial", 10)
        ).grid(row=0, column=0, sticky="w", pady=5)
        
        providers = list(self.ai_manager.PROVIDERS.items())
        # Formato: "Nombre (ID)" para el usuario, pero guardamos ID
        provider_labels = [p[1] for p in providers]
        provider_ids = [p[0] for p in providers]
        
        self.provider_combo = ttk.Combobox(
            self.options_frame,
            state="readonly",
            values=provider_labels,
            width=40
        )
        
        # Seleccionar actual
        current_provider = self.provider_var.get()
        if current_provider in provider_ids:
            self.provider_combo.current(provider_ids.index(current_provider))
        else:
            self.provider_combo.current(0)
            
        self.provider_combo.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        self.provider_combo.bind("<<ComboboxSelected>>", self._on_provider_change)
        
        # Modelo
        tk.Label(
            self.options_frame,
            text="Modelo:",
            bg=BG_COLOR,
            font=("Arial", 10)
        ).grid(row=1, column=0, sticky="w", pady=5)
        
        self.model_combo = ttk.Combobox(
            self.options_frame,
            state="readonly", # O 'normal' para permitir custom
            textvariable=self.model_var,
            width=40
        )
        self.model_combo.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # API Key
        tk.Label(
            self.options_frame,
            text="API Key:",
            bg=BG_COLOR,
            font=("Arial", 10)
        ).grid(row=2, column=0, sticky="w", pady=5)
        
        key_frame = tk.Frame(self.options_frame, bg=BG_COLOR)
        key_frame.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        self.key_entry = tk.Entry(
            key_frame,
            textvariable=self.api_key_var,
            show="•",
            width=35,
            font=("Arial", 10)
        )
        self.key_entry.pack(side=tk.LEFT)
        
        self.show_key_btn = tk.Button(
            key_frame,
            text="👁",
            command=self._toggle_key_visibility,
            bg=SECONDARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            width=3
        )
        self.show_key_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón Probar Conexión
        self.test_btn = tk.Button(
            self.options_frame,
            text="🔌 Probar Conexión",
            command=self._test_connection,
            bg=SECONDARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=5
        )
        self.test_btn.grid(row=3, column=1, sticky="w", padx=10, pady=15)
        
        # Inicializar UI según estado
        self._toggle_enabled()
        self._update_models()
        
    def _toggle_enabled(self):
        """Habilitar/deshabilitar controles"""
        state = "normal" if self.enabled_var.get() else "disabled"
        
        for child in self.options_frame.winfo_children():
            try:
                child.configure(state=state)
            except:
                pass # Algunos widgets no soportan state en configure directo
                
        self.provider_combo.configure(state="readonly" if self.enabled_var.get() else "disabled")
        self.model_combo.configure(state="normal" if self.enabled_var.get() else "disabled")
        self.key_entry.configure(state=state)
        self.show_key_btn.configure(state=state)
        self.test_btn.configure(state=state)
        
    def _on_provider_change(self, event):
        """Actualizar lista de modelos al cambiar proveedor"""
        self._update_models()
        
    def _update_models(self):
        """Actualizar combobox de modelos"""
        # Obtener ID del proveedor seleccionado
        idx = self.provider_combo.current()
        if idx < 0: return
        
        provider_id = list(self.ai_manager.PROVIDERS.keys())[idx]
        self.provider_var.set(provider_id)
        
        models = self.ai_manager.MODELS.get(provider_id, [])
        self.model_combo['values'] = models
        
        if models:
            self.model_combo.current(0)
            self.model_var.set(models[0])
            
    def _toggle_key_visibility(self):
        """Mostrar/Ocultar API Key"""
        if self.key_entry['show'] == '•':
            self.key_entry.configure(show="")
        else:
            self.key_entry.configure(show="•")
            
    def _test_connection(self):
        """Probar conexión"""
        # Guardar temporalmente para probar
        temp_config = {
            'enabled': True,
            'provider': self.provider_var.get(),
            'api_key': self.api_key_var.get()
        }
        
        # Actualizar config en memoria del manager solo para el test
        # (Idealmente el manager debería aceptar params en test_connection)
        
        # Update: el manager lee de self.config. Inyectemoslo.
        self.ai_manager.config.update(temp_config)
        
        success, message = self.ai_manager.test_connection()
        
        if success:
            messagebox.showinfo("Conexión Exitosa", f"✅ {message}", parent=self.parent)
        else:
            messagebox.showerror("Error de Conexión", f"❌ {message}", parent=self.parent)

    def save(self):
        """Guardar configuración"""
        return self.ai_manager.save_config(
            enabled=self.enabled_var.get(),
            provider=self.provider_var.get(),
            api_key=self.api_key_var.get(),
            model=self.model_var.get()
        )
