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
        
        # Frame de Gestión de Conjuntos
        sets_mgmt_frame = tk.LabelFrame(
            main_frame,
            text="Gestión de Conjuntos y Dependencias",
            font=("Arial", 10, "bold"),
            bg=BG_COLOR,
            padx=10,
            pady=10
        )
        sets_mgmt_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Obtener conjuntos disponibles
        sets_info = self.rules_manager.get_sets_info()
        
        for set_name, info in sets_info.items():
            set_frame = tk.Frame(sets_mgmt_frame, bg=BG_COLOR)
            set_frame.pack(fill=tk.X, pady=5)
            
            # Nombre del conjunto
            tk.Label(
                set_frame,
                text=f"🔹 {info.get('name', set_name)}",
                font=("Arial", 10, "bold"),
                bg=BG_COLOR,
                width=30,
                anchor="w"
            ).pack(side=tk.LEFT)
            
            # Botón Dependencias
            tk.Button(
                set_frame,
                text="📦 Dependencias",
                font=("Arial", 9),
                bg="#E3F2FD",
                fg=PRIMARY_COLOR,
                relief=tk.FLAT,
                cursor="hand2",
                command=lambda s=set_name: self._show_dependency_dialog(s)
            ).pack(side=tk.LEFT, padx=10)

        # Frame para tabla y panel de detalles
        content_frame = tk.Frame(main_frame, bg=BG_COLOR)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Frame de la tabla (izquierda)
        table_frame = tk.Frame(content_frame, bg=BG_COLOR)
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Crear Treeview
        columns = ("id", "name", "category", "severity", "penalty", "enabled", "uipath", "nttdata", "status")
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
        self.tree.heading("uipath", text="UiPath")
        self.tree.heading("nttdata", text="NTTData")
        self.tree.heading("status", text="Estado")
        
        # Anchos de columna
        self.tree.column("id", width=100, anchor="w")
        self.tree.column("name", width=250, anchor="w")
        self.tree.column("category", width=120, anchor="center")
        self.tree.column("severity", width=100, anchor="center")
        self.tree.column("penalty", width=100, anchor="center")
        self.tree.column("enabled", width=70, anchor="center")
        self.tree.column("uipath", width=80, anchor="center")
        self.tree.column("nttdata", width=80, anchor="center")
        self.tree.column("status", width=120, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind evento de doble-click para abrir diálogo de edición
        self.tree.bind("<Double-Button-1>", self._on_rule_double_click)
    
    
    def _load_rules(self):
        """Cargar reglas en la tabla"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener reglas
        rules = self.rules_manager.get_all_rules()
        
        # Insertar reglas
        for rule in rules:
            rule_id = rule.get('id', '')
            name = rule.get('name', '')
            category = rule.get('category', '')
            severity = rule.get('severity', 'warning').upper()
            penalty = f"{rule.get('penalty', 0)}%"
            
            # Estado enabled/disabled
            enabled = "✅" if rule.get('enabled', True) else "❌"
            
            # Checkmarks para conjuntos
            uipath = "✅" if "UiPath" in rule.get('sets', []) else "❌"
            nttdata = "✅" if "NTTData" in rule.get('sets', []) else "❌"
            
            # Estado de implementación
            status = rule.get('implementation_status', 'pending')
            status_text = {
                'implemented': '✅ Implementada',
                'pending': '⏳ Pendiente',
                'duplicate': '🔄 Duplicada',
                'manual': '👤 Manual'
            }.get(status, status)
            
            # Color según severidad
            tag = severity.lower()
            
            self.tree.insert(
                "",
                tk.END,
                values=(rule_id, name, category, severity, penalty, enabled, uipath, nttdata, status_text),
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
        
        # Penalización
        penalty_frame = tk.LabelFrame(
            content_frame,
            text="Penalización (%)",
            font=("Arial", 10, "bold"),
            bg="white",
            padx=10,
            pady=10
        )
        penalty_frame.pack(fill=tk.X, padx=padding, pady=10)
        
        penalty_var = tk.IntVar(value=rule.get('penalty', 0))
        penalty_spinbox = tk.Spinbox(
            penalty_frame,
            from_=0,
            to=100,
            textvariable=penalty_var,
            font=("Arial", 11),
            width=10
        )
        penalty_spinbox.pack(anchor="w")
        
        # Parámetros (si tiene)
        param_vars = {}
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
        
        current_sets = rule.get('sets', [])
        uipath_var = tk.BooleanVar(value="UiPath" in current_sets)
        nttdata_var = tk.BooleanVar(value="NTTData" in current_sets)
        
        uipath_check = tk.Checkbutton(
            sets_frame,
            text="☑ UiPath",
            variable=uipath_var,
            font=("Arial", 10),
            bg="white"
        )
        uipath_check.pack(anchor="w", pady=2)
        
        nttdata_check = tk.Checkbutton(
            sets_frame,
            text="☑ NTTData",
            variable=nttdata_var,
            font=("Arial", 10),
            bg="white"
        )
        nttdata_check.pack(anchor="w", pady=2)
        
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
            # Actualizar regla
            updates = {
                'enabled': active_var.get(),
                'severity': severity_var.get(),
                'penalty': penalty_var.get()
            }
            
            # Actualizar conjuntos
            sets = []
            if uipath_var.get():
                sets.append("UiPath")
            if nttdata_var.get():
                sets.append("NTTData")
            updates['sets'] = sets
            
            self.rules_manager.update_rule(rule_id, updates)
            
            # Actualizar parámetros
            for param_name, param_var in param_vars.items():
                self.rules_manager.update_rule_parameter(rule_id, param_name, param_var.get())
            
            self._load_rules()
            dialog.destroy()
            messagebox.showinfo("Éxito", "✅ Regla actualizada correctamente")
        
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


# Test standalone
if __name__ == '__main__':
    root = tk.Tk()
    root.title("Gestión de Reglas BBPP")
    root.geometry("1400x800")
    
    screen = RulesManagementScreen(root)
    
    root.mainloop()
