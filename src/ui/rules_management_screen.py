"""
Pantalla de Gestión de Reglas BBPP
Permite ver, editar y gestionar todas las reglas de buenas prácticas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import sys

# Añadir el directorio src al path si es necesario
current_dir = Path(__file__).parent.parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

import json


try:
    from src.rules_manager import get_rules_manager
    from src.config import (
        PRIMARY_COLOR, SECONDARY_COLOR, BG_COLOR, TEXT_COLOR,
        ACCENT_COLOR, COLOR_SUCCESS, COLOR_WARNING, COLOR_ERROR
    )
    from src.ui.bbpp_set_creator import BBPPSetCreatorDialog
except ImportError:
    # Si falla, intentar import relativo
    from rules_manager import get_rules_manager
    from config import (
        PRIMARY_COLOR, SECONDARY_COLOR, BG_COLOR, TEXT_COLOR,
        ACCENT_COLOR, COLOR_SUCCESS, COLOR_WARNING, COLOR_ERROR
    )


class RulesManagementScreen:
    """Pantalla de gestión de reglas BBPP"""
    
    def __init__(self, parent):
        """
        Inicializar pantalla
        
        Args:
            parent: Frame padre donde se mostrará la pantalla
        """
        self.parent = parent
        self.rules_manager = get_rules_manager()
        self.selected_rule_id = None
        
        # Crear UI
        self._create_ui()
        self._load_rules()
    
    def _create_ui(self):
        """Crear interfaz de usuario"""
        # Frame principal con scroll
        main_frame = tk.Frame(self.parent, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_frame = tk.Frame(main_frame, bg=PRIMARY_COLOR, height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="⚙️ Gestión de Reglas BBPP",
            font=("Arial", 16, "bold"),
            bg=PRIMARY_COLOR,
            fg="white"
        )
        title_label.pack(pady=15)
        
        # Frame de estadísticas
        stats_frame = tk.Frame(main_frame, bg="#E3F2FD", height=50)
        stats_frame.pack(fill=tk.X, padx=20, pady=(10, 0))
        stats_frame.pack_propagate(False)
        
        self.stats_label = tk.Label(
            stats_frame,
            text="Cargando estadísticas...",
            font=("Arial", 9),
            bg="#E3F2FD",
            fg=PRIMARY_COLOR,
            anchor="w"
        )
        self.stats_label.pack(padx=10, pady=10, fill=tk.X)
        
        # Frame de botones superiores
        buttons_frame = tk.Frame(main_frame, bg=BG_COLOR)
        buttons_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Botón Guardar
        save_btn = tk.Button(
            buttons_frame,
            text="💾 Guardar Cambios",
            font=("Arial", 10, "bold"),
            bg=COLOR_SUCCESS,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._save_rules
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón Recargar
        reload_btn = tk.Button(
            buttons_frame,
            text="🔄 Recargar",
            font=("Arial", 10),
            bg=SECONDARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._reload_rules
        )
        reload_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón Activar Todas
        enable_all_btn = tk.Button(
            buttons_frame,
            text="✅ Activar Todas",
            font=("Arial", 10),
            bg=ACCENT_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._enable_all_rules
        )
        enable_all_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón Desactivar Todas
        disable_all_btn = tk.Button(
            buttons_frame,
            text="❌ Desactivar Todas",
            font=("Arial", 10),
            bg=COLOR_WARNING,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._disable_all_rules
        )
        disable_all_btn.pack(side=tk.LEFT, padx=5)

        # Botón Gestión de Conjuntos
        sets_mgmt_btn = tk.Button(
            buttons_frame,
            text="🔧 Gestión de Conjuntos",
            font=("Arial", 10),
            bg=ACCENT_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._show_sets_management_dialog
        )
        sets_mgmt_btn.pack(side=tk.LEFT, padx=5)

        # Botón Nuevo Conjunto
        new_set_btn = tk.Button(
            buttons_frame,
            text="➕ Nuevo Conjunto",
            font=("Arial", 10, "bold"),
            bg=COLOR_SUCCESS,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._show_create_set_dialog
        )
        new_set_btn.pack(side=tk.LEFT, padx=5)

        
        # Frame de Gestión de Dependencias
        sets_mgmt_frame = tk.LabelFrame(
            main_frame,
            text="Gestión de Dependencias por Conjunto",
            font=("Arial", 10, "bold"),
            bg=BG_COLOR,
            padx=10,
            pady=10
        )
        sets_mgmt_frame.pack(fill=tk.X, padx=20, pady=10)

        # Obtener conjuntos disponibles
        sets_info = self.rules_manager.get_sets_info()
        set_names = list(sets_info.keys())

        # Dropdown frame para dependencias
        dropdown_frame = tk.Frame(sets_mgmt_frame, bg=BG_COLOR)
        dropdown_frame.pack(fill=tk.X, pady=5)

        # Label
        tk.Label(
            dropdown_frame,
            text="Selecciona conjunto para gestionar dependencias:",
            font=("Arial", 9),
            bg=BG_COLOR,
            fg="gray"
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Dropdown de conjuntos para dependencias
        dependency_set_var = tk.StringVar(value=set_names[0] if set_names else "")
        sets_dropdown = ttk.Combobox(
            dropdown_frame,
            textvariable=dependency_set_var,
            values=set_names,
            state="readonly",
            width=30,
            font=("Arial", 10)
        )
        sets_dropdown.pack(side=tk.LEFT, padx=5)

        # Botón para editar dependencias del conjunto seleccionado
        def open_dependencies():
            selected = dependency_set_var.get()
            if selected:
                self._show_dependency_dialog(selected)

        tk.Button(
            dropdown_frame,
            text="📝 Editar Dependencias",
            font=("Arial", 9, "bold"),
            bg=SECONDARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=open_dependencies,
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=10)

        # Frame de Selección de Conjunto para Configurar
        config_set_frame = tk.LabelFrame(
            main_frame,
            text="Configuración de Reglas por Conjunto",
            font=("Arial", 10, "bold"),
            bg=BG_COLOR,
            padx=10,
            pady=10
        )
        config_set_frame.pack(fill=tk.X, padx=20, pady=10)

        # Dropdown frame para configuración
        config_dropdown_frame = tk.Frame(config_set_frame, bg=BG_COLOR)
        config_dropdown_frame.pack(fill=tk.X, pady=5)

        # Label
        tk.Label(
            config_dropdown_frame,
            text="Selecciona conjunto para configurar reglas:",
            font=("Arial", 9),
            bg=BG_COLOR,
            fg="gray"
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Dropdown de conjuntos para configuración (este es el que filtra la tabla)
        self.selected_set_var = tk.StringVar(value=set_names[0] if set_names else "")
        self.selected_set_var.trace_add("write", lambda *args: self._on_set_changed())
        config_sets_dropdown = ttk.Combobox(
            config_dropdown_frame,
            textvariable=self.selected_set_var,
            values=set_names,
            state="readonly",
            width=30,
            font=("Arial", 10)
        )
        config_sets_dropdown.pack(side=tk.LEFT, padx=5)

        # Descripción
        tk.Label(
            config_dropdown_frame,
            text="← Las reglas mostradas abajo corresponden a este conjunto",
            font=("Arial", 8),
            bg=BG_COLOR,
            fg="gray"
        ).pack(side=tk.LEFT, padx=10)

        # Frame para tabla y panel de detalles
        content_frame = tk.Frame(main_frame, bg=BG_COLOR)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Frame de la tabla (izquierda)
        table_frame = tk.Frame(content_frame, bg=BG_COLOR)
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Crear Treeview (sin columna "status")
        columns = ("id", "name", "category", "severity", "penalty", "enabled")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=20
        )

        # Configurar columnas
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Nombre de la Regla")
        self.tree.heading("category", text="Categoría")
        self.tree.heading("severity", text="Severidad")
        self.tree.heading("penalty", text="Penalización")
        self.tree.heading("enabled", text="Activa")

        # Anchos de columna (optimizados para mejor visualización)
        self.tree.column("id", width=160, minwidth=120, anchor="w", stretch=False)
        self.tree.column("name", width=350, minwidth=250, anchor="w", stretch=True)
        self.tree.column("category", width=140, minwidth=100, anchor="center", stretch=False)
        self.tree.column("severity", width=110, minwidth=90, anchor="center", stretch=False)
        self.tree.column("penalty", width=220, minwidth=180, anchor="center", stretch=False)
        self.tree.column("enabled", width=80, minwidth=70, anchor="center", stretch=False)

        # Scrollbars (vertical y horizontal)
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Layout con ambas scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        # Configurar grid para que sea responsive
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Bind eventos
        self.tree.bind("<Double-Button-1>", self._on_rule_double_click)
        self.tree.bind("<Button-1>", self._on_tree_click)
    
    
    def _on_set_changed(self):
        """Callback cuando cambia el conjunto seleccionado"""
        self._load_rules()

    def _load_rules(self):
        """Cargar reglas en la tabla del conjunto seleccionado"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Obtener conjunto seleccionado
        selected_set = getattr(self, 'selected_set_var', None)
        if not selected_set:
            return
        
        set_name = selected_set.get()
        if not set_name:
            return

        # Obtener reglas del conjunto con su configuración específica
        rules = self.rules_manager.get_rules_by_set(set_name)
        
        # Insertar TODAS las reglas del conjunto
        for rule in rules:
            rule_id = rule.get('id', '')
            name = rule.get('name', '')
            category = rule.get('category', '')
            severity = rule.get('severity', 'warning').upper()

            # Construir texto de penalización descriptivo
            params = rule.get('parameters', {})
            penalty_mode = params.get('penalty_mode', 'severity_default')
            penalty_value = params.get('penalty_value', rule.get('penalty', 0))
            use_cap = params.get('use_penalty_cap', False)
            penalty_cap = params.get('penalty_cap', 10)

            if penalty_mode == 'severity_default':
                penalty_text = "Predeterminado"
            elif penalty_mode == 'global':
                penalty_text = f"{penalty_value}% Global"
            elif penalty_mode == 'individual':
                if use_cap:
                    penalty_text = f"{penalty_value}%/hallazgo (Límite {penalty_cap}%)"
                else:
                    penalty_text = f"{penalty_value}%/hallazgo"
            else:
                penalty_text = f"{penalty_value}%"

            # Estado enabled/disabled
            enabled = "✅" if rule.get('enabled', True) else "❌"

            # Color según severidad
            tag = severity.lower()

            self.tree.insert(
                "",
                tk.END,
                values=(rule_id, name, category, severity, penalty_text, enabled),
                tags=(tag,)
            )
        
        # Configurar colores por severidad
        self.tree.tag_configure('error', background='#FFEBEE')
        self.tree.tag_configure('warning', background='#FFF3E0')
        self.tree.tag_configure('info', background='#E3F2FD')
        
        # Actualizar estadísticas
        self._update_statistics()
    
    def _update_statistics(self):
        """Actualizar estadísticas en el header"""
        stats = self.rules_manager.get_statistics()
        
        text = (
            f"📊 Total: {stats['total_rules']} reglas  |  "
            f"✅ Activas: {stats['enabled_rules']}  |  "
            f"✔️ Implementadas: {stats['implemented_rules']}  |  "
            f"⏳ Pendientes: {stats['pending_rules']}"
        )
        
        self.stats_label.config(text=text)
    
    
    def _on_tree_click(self, event):
        """Manejar clic simple en la tabla para toggle enabled/disabled"""
        # Identificar qué columna se clickeó
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return

        column = self.tree.identify_column(event.x)
        # Columna "enabled" es la #6 (índice comienza en #1)
        if column != "#6":
            return

        # Obtener regla clickeada
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        item = self.tree.item(item_id)
        rule_id = item['values'][0]
        
        # Obtener conjunto seleccionado
        set_name = self.selected_set_var.get()
        if not set_name:
            return

        # Obtener regla del conjunto específico
        rules = self.rules_manager.get_rules_by_set(set_name)
        rule = next((r for r in rules if r.get('id') == rule_id), None)
        
        if rule:
            new_enabled = not rule.get('enabled', True)
            # Actualizar solo en el conjunto seleccionado
            self.rules_manager.update_rule(rule_id, {'enabled': new_enabled}, set_name=set_name)
            self._load_rules()  # Recargar tabla

    def _on_rule_double_click(self, event):
        """Manejar doble-click en una regla para abrir diálogo de edición"""
        selection = self.tree.selection()
        if not selection:
            return

        # Obtener ID de la regla seleccionada
        item = self.tree.item(selection[0])
        rule_id = item['values'][0]

        self._show_edit_dialog(rule_id)
    
    def _show_edit_dialog(self, rule_id):
        """Mostrar diálogo modal para editar una regla"""
        rule = self.rules_manager.get_rule_by_id(rule_id)
        if not rule:
            return
        
        # Crear ventana modal
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Editar Regla: {rule.get('name', '')}")
        dialog.geometry("600x800")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Centrar ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (800 // 2)
        dialog.geometry(f"600x800+{x}+{y}")
        
        # Frame principal con scroll
        main_frame = tk.Frame(dialog, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Botones Aceptar/Cancelar (PRIMERO, para que queden abajo)
        buttons_frame = tk.Frame(dialog, bg="white", height=60)
        buttons_frame.pack(fill=tk.X, side=tk.BOTTOM)
        buttons_frame.pack_propagate(False)
        
        # Canvas para scroll
        canvas = tk.Canvas(main_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        content_frame = tk.Frame(canvas, bg="white")
        
        content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=content_frame, anchor="nw", width=580)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Habilitar scroll con rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Contenido del diálogo
        padding = 20
        
        # Nombre de la regla
        name_label = tk.Label(
            content_frame,
            text=rule.get('name', ''),
            font=("Arial", 14, "bold"),
            bg="white",
            fg=PRIMARY_COLOR,
            wraplength=540,
            justify=tk.LEFT
        )
        name_label.pack(anchor="w", padx=padding, pady=(padding, 10))
        
        # ID de la regla
        id_label = tk.Label(
            content_frame,
            text=f"ID: {rule.get('id', '')}",
            font=("Arial", 9),
            bg="white",
            fg="gray"
        )
        id_label.pack(anchor="w", padx=padding, pady=(0, 10))
        
        # Descripción
        desc_frame = tk.LabelFrame(
            content_frame,
            text="Descripción",
            font=("Arial", 10, "bold"),
            bg="white",
            padx=10,
            pady=10
        )
        desc_frame.pack(fill=tk.X, padx=padding, pady=10)
        
        desc_text = tk.Text(
            desc_frame,
            height=4,
            font=("Arial", 10),
            wrap=tk.WORD,
            relief=tk.FLAT,
            bg="#F9F9F9"
        )
        desc_text.pack(fill=tk.X)
        desc_text.insert("1.0", rule.get('description', 'Sin descripción'))
        desc_text.config(state=tk.DISABLED)
        
        # Activo
        active_var = tk.BooleanVar(value=rule.get('enabled', True))
        active_check = tk.Checkbutton(
            content_frame,
            text="✅ Regla Activa",
            variable=active_var,
            font=("Arial", 11, "bold"),
            bg="white",
            fg=COLOR_SUCCESS,
            selectcolor="white"
        )
        active_check.pack(anchor="w", padx=padding, pady=10)
        
        # Severidad
        sev_frame = tk.LabelFrame(
            content_frame,
            text="Severidad",
            font=("Arial", 10, "bold"),
            bg="white",
            padx=10,
            pady=10
        )
        sev_frame.pack(fill=tk.X, padx=padding, pady=10)
        
        severity_var = tk.StringVar(value=rule.get('severity', 'warning'))
        for sev in ["error", "warning", "info"]:
            rb = tk.Radiobutton(
                sev_frame,
                text=sev.upper(),
                variable=severity_var,
                value=sev,
                font=("Arial", 10),
                bg="white"
            )
            rb.pack(anchor="w", pady=2)
        
        # Penalización (Sistema Personalizable)
        penalty_frame = tk.LabelFrame(
            content_frame,
            text="Configuración de Penalización",
            font=("Arial", 10, "bold"),
            bg="white",
            padx=10,
            pady=10
        )
        penalty_frame.pack(fill=tk.X, padx=padding, pady=10)

        # Obtener parámetros de penalización actuales
        penalty_params = self.rules_manager.get_rule_parameters(rule_id)
        penalty_mode = penalty_params.get('penalty_mode', 'severity_default')
        penalty_value = penalty_params.get('penalty_value', rule.get('penalty', 2))
        use_penalty_cap = penalty_params.get('use_penalty_cap', False)
        penalty_cap = penalty_params.get('penalty_cap', 10)

        # Modo de penalización
        mode_label = tk.Label(
            penalty_frame,
            text="Modo de Penalización:",
            font=("Arial", 10, "bold"),
            bg="white"
        )
        mode_label.pack(anchor="w", pady=(0, 5))

        penalty_mode_var = tk.StringVar(value=penalty_mode)

        modes = [
            ("Usar predeterminado de severidad (ERROR=10pts, WARNING=3pts, INFO=0.5pts)", "severity_default"),
            ("Individual (cada hallazgo penaliza)", "individual"),
            ("Global (penalización fija total)", "global")
        ]

        for text, value in modes:
            rb = tk.Radiobutton(
                penalty_frame,
                text=text,
                variable=penalty_mode_var,
                value=value,
                font=("Arial", 9),
                bg="white",
                wraplength=520,
                justify=tk.LEFT
            )
            rb.pack(anchor="w", pady=2)

        # Valor de penalización
        value_frame = tk.Frame(penalty_frame, bg="white")
        value_frame.pack(fill=tk.X, pady=(10, 5))

        value_label = tk.Label(
            value_frame,
            text="Valor de Penalización (%):",
            font=("Arial", 10, "bold"),
            bg="white"
        )
        value_label.pack(side=tk.LEFT, padx=(0, 10))

        penalty_value_var = tk.DoubleVar(value=penalty_value)
        penalty_value_spinbox = tk.Spinbox(
            value_frame,
            from_=0,
            to=100,
            increment=0.5,
            textvariable=penalty_value_var,
            font=("Arial", 11),
            width=10
        )
        penalty_value_spinbox.pack(side=tk.LEFT)

        # Límite máximo
        cap_frame = tk.Frame(penalty_frame, bg="white")
        cap_frame.pack(fill=tk.X, pady=(10, 0))

        use_cap_var = tk.BooleanVar(value=use_penalty_cap)
        cap_check = tk.Checkbutton(
            cap_frame,
            text="Límite máximo de penalización:",
            variable=use_cap_var,
            font=("Arial", 10, "bold"),
            bg="white"
        )
        cap_check.pack(side=tk.LEFT, padx=(0, 10))

        penalty_cap_var = tk.DoubleVar(value=penalty_cap)
        penalty_cap_spinbox = tk.Spinbox(
            cap_frame,
            from_=0,
            to=100,
            increment=0.5,
            textvariable=penalty_cap_var,
            font=("Arial", 11),
            width=10,
            state='normal' if use_penalty_cap else 'disabled'
        )
        penalty_cap_spinbox.pack(side=tk.LEFT, padx=(0, 5))

        cap_percent_label = tk.Label(
            cap_frame,
            text="%",
            font=("Arial", 10),
            bg="white"
        )
        cap_percent_label.pack(side=tk.LEFT)

        # Habilitar/deshabilitar cap spinbox según checkbox
        def toggle_cap():
            penalty_cap_spinbox.config(state='normal' if use_cap_var.get() else 'disabled')

        cap_check.config(command=toggle_cap)

        # Descripción explicativa
        desc_label = tk.Label(
            penalty_frame,
            text="• Predeterminado: Usa pesos globales según severidad\n• Individual: Cada hallazgo suma el valor especificado\n• Global: Penalización fija sin importar cantidad de hallazgos\n• Límite máximo: Solo aplica a modos Predeterminado e Individual",
            font=("Arial", 8),
            bg="white",
            fg="gray",
            justify=tk.LEFT
        )
        desc_label.pack(anchor="w", pady=(10, 0))
        
        # Parámetros (si tiene)
        param_vars = {}
        type_prefixes_list = []  # Para almacenar la lista de prefijos
        allow_type_prefixes_var = None  # Para el checkbox

        parameters = self.rules_manager.get_rule_parameters(rule_id)
        if parameters:
            params_frame = tk.LabelFrame(
                content_frame,
                text="Parámetros de la Regla",
                font=("Arial", 10, "bold"),
                bg="white",
                padx=10,
                pady=10
            )
            params_frame.pack(fill=tk.X, padx=padding, pady=10)

            # Verificar si esta regla soporta prefijos de tipo (NOMENCLATURA_001, 003, 005)
            supports_type_prefixes = rule_id in ['NOMENCLATURA_001', 'NOMENCLATURA_003', 'NOMENCLATURA_005']

            for param_name, param_data in parameters.items():
                # Solo procesar parámetros que son diccionarios con 'type'
                if not isinstance(param_data, dict):
                    continue
                if param_data.get('type') == 'number':
                    # Descripción del parámetro
                    param_desc = tk.Label(
                        params_frame,
                        text=param_data.get('description', param_name),
                        font=("Arial", 10),
                        bg="white",
                        wraplength=520,
                        justify=tk.LEFT
                    )
                    param_desc.pack(anchor="w", pady=(5, 3))

                    # Frame para valor
                    value_frame = tk.Frame(params_frame, bg="white")
                    value_frame.pack(fill=tk.X, pady=(0, 10))

                    value_label = tk.Label(
                        value_frame,
                        text="Valor:",
                        font=("Arial", 10, "bold"),
                        bg="white"
                    )
                    value_label.pack(side=tk.LEFT, padx=(0, 5))

                    param_var = tk.IntVar(value=param_data.get('value', 0))
                    param_vars[param_name] = param_var

                    param_spinbox = tk.Spinbox(
                        value_frame,
                        from_=param_data.get('min', 0),
                        to=param_data.get('max', 100),
                        textvariable=param_var,
                        font=("Arial", 11, "bold"),
                        width=10
                    )
                    param_spinbox.pack(side=tk.LEFT)

                    range_label = tk.Label(
                        value_frame,
                        text=f"  (rango: {param_data.get('min', 0)}-{param_data.get('max', 100)})",
                        font=("Arial", 9),
                        bg="white",
                        fg="gray"
                    )
                    range_label.pack(side=tk.LEFT)

            # Agregar controles para prefijos de tipo (si aplica)
            if supports_type_prefixes:
                # Separador
                ttk.Separator(params_frame, orient='horizontal').pack(fill=tk.X, pady=10)

                # Checkbox para permitir prefijos de tipo
                allow_type_prefixes_var = tk.BooleanVar(value=parameters.get('allow_type_prefixes', False))

                allow_check_frame = tk.Frame(params_frame, bg="white")
                allow_check_frame.pack(fill=tk.X, pady=5)

                allow_check = tk.Checkbutton(
                    allow_check_frame,
                    text="☑ Permitir prefijos de tipo de variable",
                    variable=allow_type_prefixes_var,
                    font=("Arial", 10, "bold"),
                    bg="white",
                    fg=PRIMARY_COLOR
                )
                allow_check.pack(side=tk.LEFT)

                # Botón para gestionar prefijos
                def show_prefixes_dialog():
                    """Mostrar diálogo para editar lista de prefijos"""
                    prefix_dialog = tk.Toplevel(dialog)
                    prefix_dialog.title("Gestionar Prefijos de Tipo")
                    prefix_dialog.geometry("400x500")
                    prefix_dialog.transient(dialog)
                    prefix_dialog.grab_set()

                    # Centrar ventana
                    prefix_dialog.update_idletasks()
                    px = (prefix_dialog.winfo_screenwidth() // 2) - (200)
                    py = (prefix_dialog.winfo_screenheight() // 2) - (250)
                    prefix_dialog.geometry(f"400x500+{px}+{py}")

                    # Título
                    title_label = tk.Label(
                        prefix_dialog,
                        text="Prefijos de Tipo de Variable",
                        font=("Arial", 12, "bold"),
                        bg="white",
                        fg=PRIMARY_COLOR
                    )
                    title_label.pack(pady=10)

                    # Descripción
                    desc_label = tk.Label(
                        prefix_dialog,
                        text="Ejemplos: dt_Excel, int_contador, str_nombre",
                        font=("Arial", 9),
                        bg="white",
                        fg="gray",
                        wraplength=360
                    )
                    desc_label.pack(pady=(0, 10))

                    # Frame para lista
                    list_frame = tk.Frame(prefix_dialog, bg="white")
                    list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

                    # Listbox con scrollbar
                    scrollbar = tk.Scrollbar(list_frame)
                    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                    listbox = tk.Listbox(
                        list_frame,
                        font=("Arial", 10),
                        yscrollcommand=scrollbar.set,
                        selectmode=tk.SINGLE
                    )
                    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                    scrollbar.config(command=listbox.yview)

                    # Cargar prefijos actuales
                    current_prefixes = parameters.get('type_prefixes', [])
                    type_prefixes_list.clear()
                    type_prefixes_list.extend(current_prefixes)

                    for prefix in type_prefixes_list:
                        listbox.insert(tk.END, prefix)

                    # Frame para botones de gestión
                    btn_frame = tk.Frame(prefix_dialog, bg="white")
                    btn_frame.pack(fill=tk.X, padx=20, pady=10)

                    # Entry para nuevo prefijo
                    entry_frame = tk.Frame(btn_frame, bg="white")
                    entry_frame.pack(fill=tk.X, pady=5)

                    new_prefix_var = tk.StringVar()
                    entry = tk.Entry(
                        entry_frame,
                        textvariable=new_prefix_var,
                        font=("Arial", 10),
                        width=15
                    )
                    entry.pack(side=tk.LEFT, padx=(0, 10))

                    def add_prefix():
                        prefix = new_prefix_var.get().strip()
                        if prefix and prefix not in type_prefixes_list:
                            if not prefix.endswith('_'):
                                prefix += '_'
                            type_prefixes_list.append(prefix)
                            listbox.insert(tk.END, prefix)
                            new_prefix_var.set('')

                    add_btn = tk.Button(
                        entry_frame,
                        text="➕ Agregar",
                        command=add_prefix,
                        bg=PRIMARY_COLOR,
                        fg="white",
                        font=("Arial", 9, "bold"),
                        padx=10
                    )
                    add_btn.pack(side=tk.LEFT)

                    def remove_prefix():
                        selection = listbox.curselection()
                        if selection:
                            index = selection[0]
                            prefix = listbox.get(index)
                            type_prefixes_list.remove(prefix)
                            listbox.delete(index)

                    remove_btn = tk.Button(
                        btn_frame,
                        text="➖ Eliminar Seleccionado",
                        command=remove_prefix,
                        bg="#DC3545",
                        fg="white",
                        font=("Arial", 9, "bold"),
                        padx=10
                    )
                    remove_btn.pack(pady=5)

                    # Botón cerrar
                    close_btn = tk.Button(
                        prefix_dialog,
                        text="✓ Aceptar",
                        command=prefix_dialog.destroy,
                        bg=COLOR_SUCCESS,
                        fg="white",
                        font=("Arial", 10, "bold"),
                        padx=20
                    )
                    close_btn.pack(pady=10)

                prefixes_btn = tk.Button(
                    allow_check_frame,
                    text="⚙ Prefijos",
                    command=show_prefixes_dialog,
                    bg="#6C757D",
                    fg="white",
                    font=("Arial", 9, "bold"),
                    padx=15,
                    pady=5
                )
                prefixes_btn.pack(side=tk.LEFT, padx=10)

                # Descripción de la funcionalidad
                prefix_desc = tk.Label(
                    params_frame,
                    text="Al activar esta opción, el analizador reconocerá prefijos de tipo como dt_, str_, int_, etc. antes del nombre de la variable. Ejemplo: dt_Excel (dt_ + Excel), io_dt_TransactionData (io_ + dt_ + TransactionData).",
                    font=("Arial", 9),
                    bg="white",
                    fg="gray",
                    wraplength=520,
                    justify=tk.LEFT
                )
                prefix_desc.pack(anchor="w", pady=(5, 10))
            
            # NUEVA SECCIÓN: Excepciones (REFramework)
            # Verificar si esta regla soporta excepciones
            supports_exceptions = rule_id in [
                'NOMENCLATURA_001',
                'NOMENCLATURA_002',
                'NOMENCLATURA_003',
                'NOMENCLATURA_004',
                'NOMENCLATURA_005'
            ]
            
            exceptions_list = []  # Lista mutable para excepciones
            
            if supports_exceptions:
                # Separador
                ttk.Separator(params_frame, orient='horizontal').pack(fill=tk.X, pady=15)
                
                # Título de la sección
                tk.Label(
                    params_frame,
                    text="Excepciones de la Regla (REFramework)",
                    font=("Arial", 11, "bold"),
                    bg="white",
                    fg=PRIMARY_COLOR
                ).pack(anchor="w", pady=(10, 5))
                
                # Descripción
                tk.Label(
                    params_frame,
                    text="Variables o argumentos que deben ignorarse durante la validación de esta regla. Útil para nombres estándar del REFramework como Config, TransactionItem, etc.",
                    font=("Arial", 9),
                    bg="white",
                    fg="gray",
                    wraplength=520,
                    justify=tk.LEFT
                ).pack(anchor="w", pady=(0, 10))
                
                # Frame para la lista de excepciones
                exceptions_frame = tk.Frame(params_frame, bg="white")
                exceptions_frame.pack(fill=tk.BOTH, expand=True, pady=10)
                
                # Listbox con scrollbar
                exceptions_list_frame = tk.Frame(exceptions_frame, bg="white")
                exceptions_list_frame.pack(fill=tk.BOTH, expand=True)
                
                exceptions_scrollbar = tk.Scrollbar(exceptions_list_frame)
                exceptions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                exceptions_listbox = tk.Listbox(
                    exceptions_list_frame,
                    font=("Arial", 10),
                    yscrollcommand=exceptions_scrollbar.set,
                    selectmode=tk.SINGLE,
                    height=8,
                    bg="#F9F9F9"
                )
                exceptions_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                exceptions_scrollbar.config(command=exceptions_listbox.yview)
                
                # Cargar excepciones actuales
                current_exceptions = parameters.get('exceptions', [])
                exceptions_list = list(current_exceptions)  # Copia mutable
                
                for exc in exceptions_list:
                    exceptions_listbox.insert(tk.END, exc)
                
                # Frame para botones de gestión
                exceptions_buttons_frame = tk.Frame(params_frame, bg="white")
                exceptions_buttons_frame.pack(fill=tk.X, pady=10)
                
                # Entry para nueva excepción
                new_exception_var = tk.StringVar()
                new_exception_entry = tk.Entry(
                    exceptions_buttons_frame,
                    textvariable=new_exception_var,
                    font=("Arial", 10),
                    width=30
                )
                new_exception_entry.pack(side=tk.LEFT, padx=(0, 10))
                
                def add_exception():
                    """Agregar nueva excepción a la lista"""
                    exception_name = new_exception_var.get().strip()
                    
                    if not exception_name:
                        messagebox.showwarning(
                            "Campo Vacío",
                            "Por favor ingrese un nombre de excepción",
                            parent=dialog
                        )
                        return
                    
                    if exception_name in exceptions_list:
                        messagebox.showwarning(
                            "Duplicado",
                            f"La excepción '{exception_name}' ya existe en la lista",
                            parent=dialog
                        )
                        return
                    
                    # Agregar a lista y listbox
                    exceptions_list.append(exception_name)
                    exceptions_listbox.insert(tk.END, exception_name)
                    new_exception_var.set('')  # Limpiar campo
                
                def remove_exception():
                    """Eliminar excepción seleccionada"""
                    selection = exceptions_listbox.curselection()
                    if not selection:
                        messagebox.showwarning(
                            "Sin Selección",
                            "Por favor seleccione una excepción para eliminar",
                            parent=dialog
                        )
                        return
                    
                    index = selection[0]
                    exception_name = exceptions_listbox.get(index)
                    
                    # Confirmar eliminación
                    if messagebox.askyesno(
                        "Confirmar Eliminación",
                        f"¿Eliminar la excepción '{exception_name}'?",
                        parent=dialog
                    ):
                        exceptions_list.remove(exception_name)
                        exceptions_listbox.delete(index)
                
                # Botón Agregar
                add_exception_btn = tk.Button(
                    exceptions_buttons_frame,
                    text="➕ Agregar",
                    command=add_exception,
                    bg=PRIMARY_COLOR,
                    fg="white",
                    font=("Arial", 9, "bold"),
                    padx=15,
                    pady=5
                )
                add_exception_btn.pack(side=tk.LEFT, padx=5)
                
                # Botón Eliminar
                remove_exception_btn = tk.Button(
                    exceptions_buttons_frame,
                    text="➖ Eliminar Seleccionado",
                    command=remove_exception,
                    bg="#DC3545",
                    fg="white",
                    font=("Arial", 9, "bold"),
                    padx=15,
                    pady=5
                )
                remove_exception_btn.pack(side=tk.LEFT, padx=5)
                
                # Permitir agregar con Enter
                new_exception_entry.bind('<Return>', lambda e: add_exception())
        
        # Conjuntos
        sets_frame = tk.LabelFrame(
            content_frame,
            text="Conjuntos de Reglas",
            font=("Arial", 10, "bold"),
            bg="white",
            padx=10,
            pady=10
        )
        sets_frame.pack(fill=tk.X, padx=padding, pady=10)

        # Obtener todos los conjuntos disponibles
        available_sets = list(self.rules_manager.sets.keys())
        current_sets = rule.get('sets', [])

        # Label explicativo
        tk.Label(
            sets_frame,
            text="Selecciona los conjuntos a los que pertenece esta regla:",
            font=("Arial", 9),
            bg="white",
            fg="gray"
        ).pack(anchor="w", pady=(0, 5))

        # Listbox con selección múltiple
        sets_listbox_frame = tk.Frame(sets_frame, bg="white")
        sets_listbox_frame.pack(fill=tk.BOTH, pady=5)

        sets_listbox = tk.Listbox(
            sets_listbox_frame,
            selectmode=tk.MULTIPLE,
            height=min(len(available_sets), 4),
            font=("Arial", 10),
            relief=tk.SUNKEN,
            bd=1
        )
        sets_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar si hay muchos conjuntos
        if len(available_sets) > 4:
            sets_scrollbar = tk.Scrollbar(sets_listbox_frame, orient=tk.VERTICAL)
            sets_scrollbar.config(command=sets_listbox.yview)
            sets_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            sets_listbox.config(yscrollcommand=sets_scrollbar.set)

        # Llenar listbox y seleccionar los actuales
        for idx, set_name in enumerate(available_sets):
            sets_listbox.insert(tk.END, set_name)
            if set_name in current_sets:
                sets_listbox.selection_set(idx)
        
        # Estado de implementación
        status_frame = tk.LabelFrame(
            content_frame,
            text="Estado de Implementación",
            font=("Arial", 10, "bold"),
            bg="white",
            padx=10,
            pady=10
        )
        status_frame.pack(fill=tk.X, padx=padding, pady=10)
        
        status = rule.get('implementation_status', 'pending')
        status_text = {
            'implemented': '✅ Implementada y funcional',
            'pending': '⏳ Pendiente de implementar',
            'duplicate': '🔄 Duplicada (revisar)',
            'manual': '👤 Requiere revisión manual'
        }.get(status, status)
        
        status_label = tk.Label(
            status_frame,
            text=status_text,
            font=("Arial", 10),
            bg="white"
        )
        status_label.pack(anchor="w")
        
        # Definir funciones de botones
        
        def on_accept():
            # Obtener conjunto seleccionado
            set_name = self.selected_set_var.get()
            if not set_name:
                messagebox.showerror("Error", "No hay conjunto seleccionado")
                return
            
            # Actualizar regla
            updates = {
                'enabled': active_var.get(),
                'severity': severity_var.get(),
                'penalty': penalty_value_var.get()  # Usar penalty_value en lugar del antiguo penalty_var
            }

            # Actualizar conjuntos desde Listbox
            selected_indices = sets_listbox.curselection()
            sets = [available_sets[i] for i in selected_indices]
            updates['sets'] = sets

            # Actualizar solo en el conjunto seleccionado
            self.rules_manager.update_rule(rule_id, updates, set_name=set_name)

            # Actualizar parámetros de penalización personalizada
            rules = self.rules_manager.get_rules_by_set(set_name)
            rule_obj = next((r for r in rules if r.get('id') == rule_id), None)

            if rule_obj:
                # Asegurar que existe el diccionario parameters
                if 'parameters' not in rule_obj:
                    rule_obj['parameters'] = {}

                rule_obj['parameters']['penalty_mode'] = penalty_mode_var.get()
                rule_obj['parameters']['penalty_value'] = penalty_value_var.get()
                rule_obj['parameters']['use_penalty_cap'] = use_cap_var.get()
                rule_obj['parameters']['penalty_cap'] = penalty_cap_var.get()

            # Actualizar parámetros numéricos
            for param_name, param_var in param_vars.items():
                self.rules_manager.update_rule_parameter(rule_id, param_name, param_var.get())

            # Actualizar parámetros de prefijos de tipo (si aplica)
            if allow_type_prefixes_var is not None:
                # Actualizar allow_type_prefixes
                if rule_obj and 'parameters' in rule_obj:
                    rule_obj['parameters']['allow_type_prefixes'] = allow_type_prefixes_var.get()
                    rule_obj['parameters']['type_prefixes'] = type_prefixes_list.copy()

            # Actualizar excepciones (si aplica)
            if supports_exceptions and exceptions_list is not None:
                if rule_obj and 'parameters' in rule_obj:
                    rule_obj['parameters']['exceptions'] = exceptions_list.copy()

            # Guardar solo el conjunto seleccionado
            self.rules_manager.save_rules(set_name=set_name)

            self._load_rules()
            dialog.destroy()
            messagebox.showinfo("Éxito", f"✅ Regla actualizada en conjunto '{set_name}'")
        
        def on_copy_to_other_set():
            """Copiar configuración actual a otro conjunto"""
            # Obtener conjunto actual
            current_set = self.selected_set_var.get()
            if not current_set:
                return
            
            # Obtener otros conjuntos disponibles
            all_sets = list(self.rules_manager.sets.keys())
            other_sets = [s for s in all_sets if s != current_set]
            
            if not other_sets:
                messagebox.showinfo("Info", "No hay otros conjuntos disponibles")
                return
            
            # Crear diálogo de selección
            copy_dialog = tk.Toplevel(dialog)
            copy_dialog.title("Copiar Configuración")
            copy_dialog.geometry("400x300")
            copy_dialog.transient(dialog)
            copy_dialog.grab_set()
            
            # Centrar
            copy_dialog.update_idletasks()
            x = (copy_dialog.winfo_screenwidth() // 2) - 200
            y = (copy_dialog.winfo_screenheight() // 2) - 150
            copy_dialog.geometry(f"400x300+{x}+{y}")
            
            tk.Label(
                copy_dialog,
                text=f"Copiar configuración de '{rule.get('name')}'\ndesde '{current_set}' a:",
                font=("Arial", 11, "bold"),
                bg="white",
                wraplength=360,
                justify=tk.CENTER
            ).pack(pady=20)
            
            # Listbox para seleccionar conjuntos destino
            listbox_frame = tk.Frame(copy_dialog, bg="white")
            listbox_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            scrollbar = tk.Scrollbar(listbox_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            dest_listbox = tk.Listbox(
                listbox_frame,
                selectmode=tk.MULTIPLE,
                font=("Arial", 10),
                yscrollcommand=scrollbar.set
            )
            dest_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=dest_listbox.yview)
            
            for s in other_sets:
                dest_listbox.insert(tk.END, s)
            
            def do_copy():
                selected_indices = dest_listbox.curselection()
                if not selected_indices:
                    messagebox.showwarning("Advertencia", "Selecciona al menos un conjunto destino")
                    return
                
                dest_sets = [other_sets[i] for i in selected_indices]
                
                # Obtener configuración actual de la regla
                current_rules = self.rules_manager.get_rules_by_set(current_set)
                current_rule = next((r for r in current_rules if r.get('id') == rule_id), None)
                
                if not current_rule:
                    messagebox.showerror("Error", "No se pudo obtener la configuración actual")
                    return
                
                # Copiar a cada conjunto destino
                for dest_set in dest_sets:
                    self.rules_manager.update_rule(rule_id, current_rule, set_name=dest_set)
                    self.rules_manager.save_rules(set_name=dest_set)
                
                copy_dialog.destroy()
                messagebox.showinfo("Éxito", f"✅ Configuración copiada a {len(dest_sets)} conjunto(s)")
            
            # Botones
            btn_frame = tk.Frame(copy_dialog, bg="white")
            btn_frame.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Button(
                btn_frame,
                text="✅ Copiar",
                command=do_copy,
                bg=COLOR_SUCCESS,
                fg="white",
                font=("Arial", 10, "bold"),
                padx=20,
                pady=5
            ).pack(side=tk.LEFT, padx=5)
            
            tk.Button(
                btn_frame,
                text="❌ Cancelar",
                command=copy_dialog.destroy,
                bg=COLOR_ERROR,
                fg="white",
                font=("Arial", 10),
                padx=20,
                pady=5
            ).pack(side=tk.LEFT, padx=5)
        
        def on_cancel():
            dialog.destroy()
        
        cancel_btn = tk.Button(
            buttons_frame,
            text="❌ Cancelar",
            command=on_cancel,
            bg="#DC3545",
            fg="white",
            font=("Arial", 11),
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8
        )
        cancel_btn.pack(side=tk.RIGHT, padx=padding, pady=10)
        
        # Botón Copiar a otro conjunto
        copy_btn = tk.Button(
            buttons_frame,
            text="📋 Copiar a Otro Conjunto",
            command=on_copy_to_other_set,
            bg=ACCENT_COLOR,
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=8
        )
        copy_btn.pack(side=tk.LEFT, padx=padding, pady=10)
        
        accept_btn = tk.Button(
            buttons_frame,
            text="✅ Aceptar",
            command=on_accept,
            bg=COLOR_SUCCESS,
            fg="white",
            font=("Arial", 11, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8
        )
        accept_btn.pack(side=tk.RIGHT, padx=5, pady=10)
    
    def _update_rule_field(self, field, value):
        """Actualizar un campo de la regla seleccionada"""
        if not self.selected_rule_id:
            return
        
        self.rules_manager.update_rule(self.selected_rule_id, {field: value})
    
    def _update_sets(self):
        """Actualizar conjuntos de la regla seleccionada"""
        if not self.selected_rule_id:
            return
        
        sets = []
        if self.uipath_var.get():
            sets.append("UiPath")
        if self.nttdata_var.get():
            sets.append("NTTData")
        
        self.rules_manager.update_rule(self.selected_rule_id, {'sets': sets})
        self._load_rules()  # Recargar tabla
    
    def _update_parameter(self, param_name):
        """Actualizar un parámetro de la regla seleccionada"""
        if not self.selected_rule_id:
            return
        
        if param_name not in self.param_vars:
            return
        
        value = self.param_vars[param_name].get()
        self.rules_manager.update_rule_parameter(self.selected_rule_id, param_name, value)
    
    def _save_rules(self):
        """Guardar cambios en el archivo"""
        if self.rules_manager.save_rules():
            messagebox.showinfo("Éxito", "✅ Reglas guardadas correctamente")
        else:
            messagebox.showerror("Error", "❌ Error al guardar las reglas")
    
    def _reload_rules(self):
        """Recargar reglas desde el archivo"""
        if messagebox.askyesno("Confirmar", "¿Recargar reglas desde el archivo?\nSe perderán los cambios no guardados."):
            self.rules_manager.load_rules()
            self._load_rules()
            messagebox.showinfo("Éxito", "✅ Reglas recargadas")
    
    def _enable_all_rules(self):
        """Activar todas las reglas"""
        for rule in self.rules_manager.get_all_rules():
            self.rules_manager.update_rule(rule['id'], {'enabled': True})
        self.rules_manager.save_rules()
        self._load_rules()
        messagebox.showinfo("Éxito", "✅ Todas las reglas activadas")
    
    def _disable_all_rules(self):
        """Desactivar todas las reglas"""
        if messagebox.askyesno("Confirmar", "¿Desactivar TODAS las reglas?"):
            for rule in self.rules_manager.get_all_rules():
                self.rules_manager.update_rule(rule['id'], {'enabled': False})
            self.rules_manager.save_rules()
            self._load_rules()
            messagebox.showinfo("Éxito", "❌ Todas las reglas desactivadas")
    
    def _save_company_settings(self):
        """Guardar configuración de empresa"""
        try:
            # Obtener valores de los campos
            company_name = self.company_name_var.get().strip()
            company_short_name = self.company_short_name_var.get().strip()
            
            # Validar que no estén vacíos
            if not company_name:
                messagebox.showwarning("Advertencia", "El nombre de empresa no puede estar vacío")
                return
            
            if not company_short_name:
                messagebox.showwarning("Advertencia", "El nombre corto no puede estar vacío")
                return
            
            # Guardar en branding_manager
            success_name = self.branding_manager.set_company_name(company_name)
            success_short = self.branding_manager.set_company_short_name(company_short_name)
            
            if success_name and success_short:
                messagebox.showinfo(
                    "✅ Configuración Guardada",
                    f"La configuración de empresa se ha guardado correctamente:\n\n"
                    f"Nombre: {company_name}\n"
                    f"Nombre Corto: {company_short_name}\n\n"
                    f"El sidebar se actualizará ahora."
                )
                
                # Refrescar sidebar para mostrar cambios inmediatamente
                try:
                    # Obtener la ventana raíz (Tk)
                    root = self.parent.winfo_toplevel()
                    
                    # Acceder a MainWindow a través de la referencia guardada en root
                    if hasattr(root, 'main_window'):
                        root.main_window.refresh_sidebar()
                        print("✅ Sidebar refrescado correctamente")
                    else:
                        print("⚠️ No se encontró la referencia a MainWindow")
                        messagebox.showinfo(
                            "Información",
                            "Los cambios se aplicarán al reiniciar la aplicación."
                        )
                except Exception as e:
                    print(f"⚠️ No se pudo refrescar el sidebar automáticamente: {e}")
                    import traceback
                    traceback.print_exc()
                    messagebox.showinfo(
                        "Información",
                        "Los cambios se aplicarán al reiniciar la aplicación."
                    )
            else:
                messagebox.showerror(
                    "❌ Error",
                    "No se pudo guardar la configuración de empresa."
                )
        except Exception as e:
            messagebox.showerror(
                "❌ Error",
                f"Error al guardar la configuración:\n{str(e)}"
            )






    def _show_dependency_dialog(self, set_name):
        """Mostrar diálogo para editar dependencias de un conjunto"""
        current_deps = self.rules_manager.get_set_dependencies(set_name)
        
        # Crear ventana modal
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Dependencias: {set_name}")
        dialog.geometry("600x500")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Centrar ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"600x500+{x}+{y}")
        
        # Contenido
        main_frame = tk.Frame(dialog, bg="white", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            main_frame,
            text=f"Configuración de Dependencias para {set_name}",
            font=("Arial", 12, "bold"),
            bg="white",
            fg=PRIMARY_COLOR
        ).pack(anchor="w", pady=(0, 10))
        
        tk.Label(
            main_frame,
            text="Pega aquí el bloque 'dependencies' del project.json:",
            font=("Arial", 10),
            bg="white"
        ).pack(anchor="w", pady=(0, 5))
        
        # Área de texto
        text_area = tk.Text(
            main_frame,
            font=("Consolas", 10),
            height=15,
            relief=tk.SUNKEN
        )
        text_area.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Cargar valor actual formateado
        if current_deps:
            text_area.insert("1.0", json.dumps(current_deps, indent=4))
        else:
            text_area.insert("1.0", "{\n    \"UiPath.System.Activities\": \"22.10.3\",\n    \"UiPath.Excel.Activities\": \"2.12.3\"\n}")
            
        # Botones
        buttons_frame = tk.Frame(main_frame, bg="white")
        buttons_frame.pack(fill=tk.X, pady=10)
        
        def validate_and_save():
            content = text_area.get("1.0", tk.END).strip()
            if not content:
                messagebox.showwarning("Advertencia", "El contenido no puede estar vacío", parent=dialog)
                return
                
            try:
                deps = json.loads(content)
                if not isinstance(deps, dict):
                    raise ValueError("El JSON debe ser un objeto (diccionario)")
                
                # Guardar
                if self.rules_manager.set_set_dependencies(set_name, deps):
                    self.rules_manager.save_rules()
                    messagebox.showinfo("Éxito", "✅ Dependencias guardadas correctamente", parent=dialog)
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo guardar la configuración", parent=dialog)
                    
            except json.JSONDecodeError as e:
                messagebox.showerror("JSON Inválido", f"Error de sintaxis JSON:\n{e}", parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", f"Error al procesar:\n{e}", parent=dialog)
        
        tk.Button(
            buttons_frame,
            text="✅ Guardar",
            bg=COLOR_SUCCESS,
            fg="white",
            font=("Arial", 10, "bold"),
            command=validate_and_save
        ).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="❌ Cancelar",
            bg="#DC3545",
            fg="white",
            font=("Arial", 10),
            command=dialog.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="🔍 Validar JSON",
            bg=SECONDARY_COLOR,
            fg="white",
            font=("Arial", 10),
            command=lambda: self._validate_json(text_area.get("1.0", tk.END), dialog)
        ).pack(side=tk.LEFT, padx=5)

    def _validate_json(self, content, parent):
        try:
            json.loads(content)
            messagebox.showinfo("Validación", "✅ JSON Válido", parent=parent)
        except Exception as e:
            messagebox.showerror("Validación", f"❌ JSON Inválido:\n{e}", parent=parent)

    def _show_sets_management_dialog(self):
        """
        Mostrar diálogo para gestionar conjuntos de BBPP
        Permite seleccionar un conjunto y gestionar qué reglas pertenecen a él
        """
        # Crear ventana modal
        dialog = tk.Toplevel(self.parent)
        dialog.title("🔧 Gestión de Conjuntos de Buenas Prácticas")
        dialog.geometry("800x700")
        dialog.transient(self.parent)
        dialog.grab_set()

        # Centrar ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 400
        y = (dialog.winfo_screenheight() // 2) - 350
        dialog.geometry(f"800x700+{x}+{y}")

        # Frame principal
        main_frame = tk.Frame(dialog, bg="white", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        tk.Label(
            main_frame,
            text="Gestión de Conjuntos de Buenas Prácticas",
            font=("Arial", 14, "bold"),
            bg="white",
            fg=PRIMARY_COLOR
        ).pack(pady=(0, 20))

        # Descripción
        tk.Label(
            main_frame,
            text="Seleccione un conjunto y marque las reglas que desea incluir en él.",
            font=("Arial", 9),
            bg="white",
            fg="gray",
            wraplength=750
        ).pack(pady=(0, 10))

        # Frame de selección de conjunto
        select_frame = tk.Frame(main_frame, bg="white")
        select_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            select_frame,
            text="Seleccionar Conjunto:",
            font=("Arial", 10, "bold"),
            bg="white"
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Obtener conjuntos dinámicamente desde rules_manager
        available_sets = list(self.rules_manager.sets.keys())
        if not available_sets:
            messagebox.showwarning(
                "Sin Conjuntos",
                "No hay conjuntos configurados en BBPP_Master.json",
                parent=dialog
            )
            dialog.destroy()
            return

        selected_set = tk.StringVar(value=available_sets[0])

        set_combo = ttk.Combobox(
            select_frame,
            textvariable=selected_set,
            values=available_sets,
            state="readonly",
            width=30,
            font=("Arial", 10)
        )
        set_combo.pack(side=tk.LEFT, padx=10)

        # Variables para UI
        set_enabled_var = tk.BooleanVar()
        rules_checkboxes = {}  # {rule_id: BooleanVar}

        # Frame de información del conjunto
        info_frame = tk.LabelFrame(
            main_frame,
            text="Información del Conjunto",
            font=("Arial", 10, "bold"),
            bg="white",
            padx=10,
            pady=10
        )
        info_frame.pack(fill=tk.X, pady=10)

        # Checkbox conjunto activo
        enabled_check = tk.Checkbutton(
            info_frame,
            text="☑ Conjunto Activo",
            variable=set_enabled_var,
            font=("Arial", 10, "bold"),
            bg="white",
            fg=COLOR_SUCCESS
        )
        enabled_check.pack(anchor="w", pady=5)

        # Label de info de dependencias
        deps_label = tk.Label(
            info_frame,
            text="",
            font=("Arial", 9),
            bg="white",
            fg="gray"
        )
        deps_label.pack(anchor="w", pady=5)

        # Botón para editar dependencias (reutiliza función existente)
        def edit_dependencies():
            """Abrir diálogo de dependencias para el conjunto seleccionado"""
            self._show_dependency_dialog(selected_set.get())
            # Recargar info después de editar
            load_set_info()

        deps_btn = tk.Button(
            info_frame,
            text="📝 Editar Dependencias",
            command=edit_dependencies,
            bg=SECONDARY_COLOR,
            fg="white",
            font=("Arial", 9),
            padx=10,
            pady=5
        )
        deps_btn.pack(anchor="w", pady=5)

        # Frame de reglas con scroll
        rules_frame = tk.LabelFrame(
            main_frame,
            text="Reglas en este Conjunto",
            font=("Arial", 10, "bold"),
            bg="white",
            padx=10,
            pady=10
        )
        rules_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Canvas para scroll
        rules_canvas = tk.Canvas(rules_frame, bg="white", highlightthickness=0)
        rules_scrollbar = ttk.Scrollbar(rules_frame, orient=tk.VERTICAL, command=rules_canvas.yview)
        rules_content = tk.Frame(rules_canvas, bg="white")

        rules_content.bind(
            "<Configure>",
            lambda e: rules_canvas.configure(scrollregion=rules_canvas.bbox("all"))
        )

        rules_canvas.create_window((0, 0), window=rules_content, anchor="nw", width=730)
        rules_canvas.configure(yscrollcommand=rules_scrollbar.set)

        # Habilitar scroll con rueda del mouse
        def _on_mousewheel(event):
            rules_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        rules_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        rules_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        rules_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def load_set_info():
            """
            Cargar información del conjunto seleccionado:
            - Estado activo/inactivo
            - Número de dependencias
            - Checkboxes de reglas
            """
            set_name = selected_set.get()
            if not set_name:
                return

            # Obtener datos del conjunto
            set_data = self.rules_manager.sets.get(set_name, {})

            # Actualizar checkbox de activo
            set_enabled_var.set(set_data.get('enabled', True))

            # Actualizar label de dependencias
            deps = set_data.get('dependencies', {})
            deps_count = len(deps)
            deps_label.config(text=f"📦 {deps_count} dependencia{'s' if deps_count != 1 else ''} configurada{'s' if deps_count != 1 else ''}")

            # Limpiar widgets anteriores
            for widget in rules_content.winfo_children():
                widget.destroy()
            rules_checkboxes.clear()

            # Obtener TODAS las reglas
            all_rules = self.rules_manager.get_all_rules()

            # Crear Listbox con selección múltiple (más compacto que checkboxes individuales)
            rules_listbox = tk.Listbox(
                rules_content,
                selectmode=tk.MULTIPLE,
                font=("Arial", 9),
                relief=tk.FLAT,
                bg="white",
                highlightthickness=0
            )
            rules_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Almacenar referencia al listbox para acceder desde save_changes()
            rules_checkboxes['_listbox'] = rules_listbox
            rules_checkboxes['_all_rules'] = all_rules

            # Llenar listbox y seleccionar reglas que pertenecen al conjunto
            for idx, rule in enumerate(all_rules):
                rule_id = rule.get('id', '')
                rule_name = rule.get('name', '')

                # Insertar regla en listbox
                rules_listbox.insert(tk.END, f"{rule_id} - {rule_name}")

                # Seleccionar si pertenece al conjunto
                is_in_set = set_name in rule.get('sets', [])
                if is_in_set:
                    rules_listbox.selection_set(idx)

        def on_set_changed(*args):
            """Evento cuando se cambia el conjunto seleccionado en el dropdown"""
            load_set_info()

        # Vincular evento de cambio de conjunto
        selected_set.trace('w', on_set_changed)

        # Cargar información inicial
        load_set_info()

        # Botones de acción
        buttons_frame = tk.Frame(main_frame, bg="white")
        buttons_frame.pack(fill=tk.X, pady=10)

        def save_changes():
            """
            Guardar cambios del conjunto:
            1. Actualizar estado activo/inactivo del conjunto
            2. Actualizar qué reglas pertenecen al conjunto
            3. Guardar a BBPP_Master.json
            """
            set_name = selected_set.get()
            if not set_name:
                return

            # 1. Actualizar enabled del conjunto
            self.rules_manager.sets[set_name]['enabled'] = set_enabled_var.get()

            # 2. Actualizar reglas: añadir/quitar del conjunto según Listbox
            rules_listbox = rules_checkboxes.get('_listbox')
            all_rules = rules_checkboxes.get('_all_rules', [])

            if rules_listbox and all_rules:
                # Obtener índices seleccionados
                selected_indices = rules_listbox.curselection()

                # Iterar sobre TODAS las reglas y actualizar su pertenencia al conjunto
                for idx, rule in enumerate(all_rules):
                    rule_id = rule.get('id', '')
                    rule_obj = self.rules_manager.get_rule_by_id(rule_id)
                    if not rule_obj:
                        continue

                    current_sets = rule_obj.get('sets', []).copy()
                    is_selected = idx in selected_indices

                    # Añadir al conjunto si está seleccionado y no está
                    if is_selected and set_name not in current_sets:
                        current_sets.append(set_name)
                    # Quitar del conjunto si no está seleccionado pero está
                    elif not is_selected and set_name in current_sets:
                        current_sets.remove(set_name)

                    # Actualizar regla
                    self.rules_manager.update_rule(rule_id, {'sets': current_sets})

            # 3. Guardar a archivo
            if self.rules_manager.save_rules():
                messagebox.showinfo(
                    "Éxito",
                    f"✅ Conjunto '{set_name}' actualizado correctamente",
                    parent=dialog
                )
                # Recargar tabla principal para reflejar cambios
                self._load_rules()
            else:
                messagebox.showerror(
                    "Error",
                    "❌ Error al guardar cambios",
                    parent=dialog
                )

        # Botón Guardar
        tk.Button(
            buttons_frame,
            text="💾 Guardar Cambios",
            command=save_changes,
            bg=COLOR_SUCCESS,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        # Botón Cerrar
        tk.Button(
            buttons_frame,
            text="❌ Cerrar",
            command=dialog.destroy,
            bg="#DC3545",
            fg="white",
            font=("Arial", 10),
            padx=20,
            pady=8
        ).pack(side=tk.RIGHT, padx=5)

    def _save_rules(self):
        """Guardar cambios del conjunto seleccionado"""
        set_name = self.selected_set_var.get()
        if not set_name:
            messagebox.showerror("Error", "No hay conjunto seleccionado")
            return
        
        self.rules_manager.save_rules(set_name=set_name)
        messagebox.showinfo("Éxito", f"✅ Cambios guardados en conjunto '{set_name}'")
    
    def _reload_rules(self):
        """Recargar reglas desde archivos"""
        self.rules_manager.load_rules()
        self._load_rules()
        messagebox.showinfo("Info", "🔄 Reglas recargadas desde archivos")
    
    def _enable_all_rules(self):
        """Activar todas las reglas del conjunto seleccionado"""
        set_name = self.selected_set_var.get()
        if not set_name:
            messagebox.showerror("Error", "No hay conjunto seleccionado")
            return
        
        rules = self.rules_manager.get_rules_by_set(set_name)
        for rule in rules:
            self.rules_manager.update_rule(rule.get('id'), {'enabled': True}, set_name=set_name)
        
        self._load_rules()
        messagebox.showinfo("Éxito", f"✅ Todas las reglas de '{set_name}' activadas")
    
    def _disable_all_rules(self):
        """Desactivar todas las reglas del conjunto seleccionado"""
        set_name = self.selected_set_var.get()
        if not set_name:
            messagebox.showerror("Error", "No hay conjunto seleccionado")
            return
        
        rules = self.rules_manager.get_rules_by_set(set_name)
        for rule in rules:
            self.rules_manager.update_rule(rule.get('id'), {'enabled': False}, set_name=set_name)
        
        self._load_rules()
        messagebox.showinfo("Éxito", f"❌ Todas las reglas de '{set_name}' desactivadas")


# Test standalone
    def _show_create_set_dialog(self):
        """Mostrar diálogo para crear nuevo conjunto"""
        try:
            # Importación local para evitar problemas circulares si falla arriba
            from src.ui.bbpp_set_creator import BBPPSetCreatorDialog
            
            BBPPSetCreatorDialog(
                self.parent,
                on_create_callback=self._on_set_created
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el diálogo: {e}", parent=self.parent)
    
    def _on_set_created(self):
        """Callback cuando se crea un conjunto"""
        # Recargar la pantalla completa para actualizar listas
        for widget in self.parent.winfo_children():
            widget.destroy()
        self.__init__(self.parent)


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Gestión de Reglas BBPP")
    root.geometry("1400x800")
    
    screen = RulesManagementScreen(root)
    
    root.mainloop()
