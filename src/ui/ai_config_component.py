"""
Componente de Configuración de IA
Maneja la interfaz de configuración para la integración con IA
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from src.config import PRIMARY_COLOR, SECONDARY_COLOR, BG_COLOR, COLOR_SUCCESS
from src.ai.ai_manager import get_ai_manager

class AIConfigComponent:
    """Componente modificado para Configuración de IA simplificada"""
    
    def __init__(self, parent):
        self.parent = parent
        self.ai_manager = get_ai_manager()
        self._create_ui()
        
    def _create_ui(self):
        """Crear UI simplificada incrustada en Configuración"""
        # Frame principal
        self.main_frame = tk.LabelFrame(
            self.parent, 
            text="Inteligencia Artificial",
            font=("Arial", 12, "bold"),
            bg="white", 
            fg=PRIMARY_COLOR,
            padx=20, pady=20
        )
        self.main_frame.pack(fill=tk.X, pady=10)
        
        # 1. Checkbox "Utilizar IA"
        self.enable_var = tk.BooleanVar(value=self.ai_manager.config.get('enabled', False))
        
        chk_frame = tk.Frame(self.main_frame, bg="white")
        chk_frame.pack(fill=tk.X)
        
        self.enable_check = tk.Checkbutton(
            chk_frame,
            text="Utilizar Inteligencia Artificial (Análisis adicional tras BBPP)",
            variable=self.enable_var,
            bg="white",
            font=("Arial", 11),
            command=self._on_toggle_enable
        )
        self.enable_check.pack(side=tk.LEFT)
        
        # 2. Botón de Configuración Avanzada
        self.config_btn = tk.Button(
            self.main_frame,
            text="⚙️ Configuración de IA y Prompts",
            command=self._open_advanced_config,
            bg=SECONDARY_COLOR,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15, pady=8
        )
        self.config_btn.pack(anchor="w", pady=(15, 0))
        
    def _on_toggle_enable(self):
        """Guardar estado de habilitación"""
        self.ai_manager.save_config(enabled=self.enable_var.get())

    def _open_advanced_config(self):
        """Abrir modal de configuración avanzada"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Configuración Avanzada de IA")
        dialog.geometry("900x700")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Centrar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (900 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f"900x700+{x}+{y}")
        
        main_container = tk.Frame(dialog, bg="white", padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # --- DIVISIÓN EN DOS PANELES ---
        # Panel Izquierdo: Conexión
        left_panel = tk.LabelFrame(main_container, text="Conexión API", bg="white", font=("Arial", 10, "bold"), padx=15, pady=15)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Panel Derecho: Prompts
        right_panel = tk.LabelFrame(main_container, text="Gestión de Prompts", bg="white", font=("Arial", 10, "bold"), padx=15, pady=15)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self._build_connection_panel(left_panel, dialog)
        self._build_prompts_panel(right_panel, dialog)

        # Botón cerrar inferior
        tk.Button(main_container, text="Cerrar", command=dialog.destroy, padx=20).pack(side=tk.BOTTOM, pady=10)

    def _build_connection_panel(self, parent, dialog):
        """Panel de configuración de API (Izquierda)"""
        # Provider
        tk.Label(parent, text="Proveedor de IA:", bg="white", font=("Arial", 9, "bold")).pack(anchor="w")
        self.provider_var = tk.StringVar(value=self.ai_manager.config.get('provider', 'gemini'))
        
        # Mapeo visual
        display_providers = ["Google Gemini (Recomendado)", "OpenAI GPT", "Anthropic Claude", "Local LLM"]
        value_map = {
            "Google Gemini (Recomendado)": "gemini", 
            "OpenAI GPT": "openai", 
            "Anthropic Claude": "claude", 
            "Local LLM": "local"
        }
        reverse_map = {v: k for k, v in value_map.items()}
        
        current_display = reverse_map.get(self.provider_var.get(), "Google Gemini (Recomendado)")
        
        self.provider_combo = ttk.Combobox(parent, values=display_providers, state="readonly")
        self.provider_combo.set(current_display)
        self.provider_combo.pack(fill=tk.X, pady=(5, 15))
        
        # API Key
        tk.Label(parent, text="API Key:", bg="white", font=("Arial", 9, "bold")).pack(anchor="w")
        self.api_key_var = tk.StringVar(value=self.ai_manager.get_api_key() or "")
        entry = tk.Entry(parent, textvariable=self.api_key_var, show="*", bg="#f8f9fa")
        entry.pack(fill=tk.X, pady=(5, 15))
        
        # Model
        tk.Label(parent, text="Modelo:", bg="white", font=("Arial", 9, "bold")).pack(anchor="w")
        self.model_var = tk.StringVar(value=self.ai_manager.config.get('model', 'gemini-1.5-flash'))
        # Usar Combobox para permitir escribir O seleccionar de la lista detectada
        self.model_entry = ttk.Combobox(parent, textvariable=self.model_var)
        self.model_entry.pack(fill=tk.X, pady=(5, 15))

        # Evento cambio de proveedor para sugerir modelo
        def on_provider_changed(event):
            selected_label = self.provider_combo.get()
            provider_val = value_map.get(selected_label, 'gemini')
            
            # Modelos por defecto
            defaults = {
                'gemini': 'gemini-1.5-flash-001', # O 'gemini-pro' si flash falla
                'openai': 'gpt-3.5-turbo',
                'claude': 'claude-3-5-sonnet-20240620',
                'local': 'llama3'
            }
            if provider_val in defaults:
                self.model_var.set(defaults[provider_val])
        
        self.provider_combo.bind("<<ComboboxSelected>>", on_provider_changed)

        # Test Connection button
        def test_conn():
            # Guardar config temporal para test
            provider_val = value_map.get(self.provider_combo.get())
            
            # Hacer backup de config y forzar enabled=True en memoria para que el test pase
            original_config = self.ai_manager.config.copy()
            
            try:
                self.ai_manager.config['provider'] = provider_val
                self.ai_manager.config['api_key'] = self.api_key_var.get().strip()
                self.ai_manager.config['model'] = self.model_var.get().strip()
                self.ai_manager.config['enabled'] = True
                
                # Ejecutar prueba
                result_tuple = self.ai_manager.test_connection()
                
                # Desempaquetar flexiblemente (2 o 3 valores)
                if len(result_tuple) == 3:
                    success, msg, models = result_tuple
                else:
                    success, msg = result_tuple
                    models = []
                
                # Si hay modelos detectados, actualizar el desplegable
                if models:
                    self.model_entry['values'] = models
                    msg += f"\n\n▼ Se ha actualizado la lista de modelos disponibles."
                    
                    # Si el modelo actual no es válido, sugerir el primero
                    current_model = self.model_var.get()
                    if current_model not in models:
                        msg += f"\n(Sugerencia: Cambia a '{models[0]}')"
                
                if success:
                    messagebox.showinfo("Éxito", f"✅ {msg}", parent=dialog)
                else:
                    messagebox.showerror("Error", f"❌ {msg}", parent=dialog)
            finally:
                # Restaurar enabled original si era False?
                # En realidad, si el usuario está testeando, probablemente querrá habilitarlo después.
                # Dejamos la config modificada en memoria pero NO guardada en disco aún (eso lo hace el botón Guardar o Save global)
                if not original_config.get('enabled'):
                    # Si estaba apagado, lo dejamos apagado en disco hasta que pulse Guardar Connection
                    pass

        tk.Button(parent, text="🔌 Probar Conexión", command=test_conn, bg="#17a2b8", fg="white").pack(fill=tk.X, pady=(0, 10))
        
        # Save Connection Button
        def save_connection():
            provider = value_map.get(self.provider_combo.get())
            if self.ai_manager.save_config(
                enabled=True,
                provider=provider,
                api_key=self.api_key_var.get().strip(),
                model=self.model_var.get().strip()
            ):
                messagebox.showinfo("Guardado", "✅ Configuración de conexión actualizada", parent=dialog)
                self.enable_var.set(True) # Actualizar UI principal

        tk.Button(parent, text="💾 Guardar Conexión", command=save_connection, bg=PRIMARY_COLOR, fg="white", font=("Arial", 10, "bold")).pack(fill=tk.X, pady=5)

    def _build_prompts_panel(self, parent, dialog):
        """Panel de gestión de prompts (Derecha)"""
        # Selector de Prompt Activo
        top_frame = tk.Frame(parent, bg="white")
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(top_frame, text="Prompt Activo:", bg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        self.prompts_dict = self.ai_manager.get_all_prompts()
        self.prompt_names = list(self.prompts_dict.keys())
        current_active = self.ai_manager.get_active_prompt_name()
        
        self.active_prompt_combo = ttk.Combobox(top_frame, values=self.prompt_names, state="readonly", width=25)
        self.active_prompt_combo.set(current_active)
        self.active_prompt_combo.pack(side=tk.LEFT, padx=10)
        
        def on_select(event):
            name = self.active_prompt_combo.get()
            self.ai_manager.set_active_prompt(name) # Auto-activar al seleccionar
            self._load_prompt_content(name)
            
        self.active_prompt_combo.bind("<<ComboboxSelected>>", on_select)
        
        # Botones de Acción (Create, Delete)
        action_frame = tk.Frame(parent, bg="white")
        action_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(action_frame, text="➕ Nuevo Prompt", command=lambda: self._create_new_prompt(dialog), bg="#28a745", fg="white", font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
        tk.Button(action_frame, text="🗑️ Borrar", command=lambda: self._delete_current_prompt(dialog), bg="#dc3545", fg="white", font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
        
        # Botón de Guardar Contenido (Grande)
        tk.Button(action_frame, text="💾 Guardar Cambios Texto", command=lambda: self._save_current_prompt_content(dialog), bg=SECONDARY_COLOR, fg="white", font=("Arial", 8, "bold")).pack(side=tk.RIGHT)

        # Editor de Texto
        tk.Label(parent, text="Contenido del Prompt:", bg="white", font=("Arial", 9)).pack(anchor="w", pady=(10, 0))
        
        # Instrucciones de placeholders
        tk.Label(
            parent,
            text="Variables: {filename}, {project_type}, {findings_count}, {findings_list}, {xaml_content}",
            font=("Arial", 8), bg="#e9ecef", fg="#495057", padx=5
        ).pack(fill=tk.X)
        
        self.prompt_text = tk.Text(parent, font=("Consolas", 9), wrap=tk.WORD, bg="#f8f9fa", height=20)
        self.prompt_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Cargar contenido inicial
        self._load_prompt_content(current_active)

    def _load_prompt_content(self, name):
        content = self.prompts_dict.get(name, "")
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", content)

    def _save_current_prompt_content(self, parent_dialog):
        name = self.active_prompt_combo.get()
        content = self.prompt_text.get("1.0", tk.END).strip()
        
        if not content:
            messagebox.showerror("Error", "El prompt no puede estar vacío", parent=parent_dialog)
            return

        if self.ai_manager.save_prompt(name, content):
            # Recargar dict local
            self.prompts_dict = self.ai_manager.get_all_prompts()
            messagebox.showinfo("Guardado", f"Prompt '{name}' actualizado correctamente", parent=parent_dialog)

    def _create_new_prompt(self, parent_dialog):
        """Diálogo para crear nuevo prompt"""
        name = simpledialog.askstring("Nuevo Prompt", "Nombre del nuevo prompt (ej: Auditoría Estricta):", parent=parent_dialog)
        if name:
            if name in self.prompts_dict:
                messagebox.showerror("Error", "Ya existe un prompt con ese nombre", parent=parent_dialog)
                return
            
            # Crear clonando el actual 
            current_content = self.prompt_text.get("1.0", tk.END).strip()
            self.ai_manager.save_prompt(name, current_content)
            
            # Actualizar lista y seleccionar
            self.prompts_dict = self.ai_manager.get_all_prompts()
            self.prompt_names = list(self.prompts_dict.keys())
            self.active_prompt_combo['values'] = self.prompt_names
            self.active_prompt_combo.set(name)
            self._load_prompt_content(name)

    def _delete_current_prompt(self, parent_dialog):
        name = self.active_prompt_combo.get()
        if name == 'Default':
            messagebox.showwarning("Aviso", "No puedes borrar el prompt por defecto", parent=parent_dialog)
            return
            
        if messagebox.askyesno("Confirmar", f"¿Eliminar el prompt '{name}'?", parent=parent_dialog):
            self.ai_manager.delete_prompt(name)
            
            # Actualizar lista
            self.prompts_dict = self.ai_manager.get_all_prompts()
            self.prompt_names = list(self.prompts_dict.keys())
            self.active_prompt_combo['values'] = self.prompt_names
            
            # Seleccionar Default
            self.active_prompt_combo.set('Default')
            self._load_prompt_content('Default')

    def save(self):
        """Método público para guardar configuración desde la pantalla principal"""
        # Guardar solo el estado enabled, el resto se gestiona en modal
        self.ai_manager.save_config(enabled=self.enable_var.get())
        return True
