"""
Ventana principal de la aplicación
UI con Tkinter (sin necesidad de instalación adicional)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import sys

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import (
    WINDOW_TITLE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    PRIMARY_COLOR, SECONDARY_COLOR, BG_COLOR, TEXT_COLOR,
    APP_VERSION, APP_VERSION_TYPE, APP_AUTHOR, COMPANY,
    load_user_config, save_user_config, reset_to_defaults,
    get_threshold, set_threshold, get_validation_option, set_validation_option,
    get_output_option, set_output_option, get_custom_logo, set_custom_logo,
    DEFAULT_CONFIG, COLOR_SUCCESS
)


class MainWindow:
    """Ventana principal de la aplicación"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_MIN_WIDTH}x{WINDOW_MIN_HEIGHT}")
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        # Guardar referencia a MainWindow en el root para acceso desde widgets hijos
        self.root.main_window = self
        
        self.project_path = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Barra de estado (primero para que quede abajo)
        self._create_status_bar()
        
        # Menú lateral
        self._create_sidebar()
        
        # Área principal
        self._create_main_area()
        
    def _create_sidebar(self):
        """Crear menú lateral"""
        self.sidebar = tk.Frame(self.root, bg=PRIMARY_COLOR, width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        # Título de la aplicación
        title_label = tk.Label(
            self.sidebar,
            text="Analizador BBPP\nUiPath",
            bg=PRIMARY_COLOR,
            fg="white",
            font=("Arial", 16, "bold"),
            pady=20
        )
        title_label.pack()
        
        # Versión
        version_label = tk.Label(
            self.sidebar,
            text=f"v{APP_VERSION} {APP_VERSION_TYPE}",
            bg=PRIMARY_COLOR,
            fg="white",
            font=("Arial", 9)
        )
        version_label.pack()
        
        # Separador
        separator = tk.Frame(self.sidebar, bg="white", height=2)
        separator.pack(fill=tk.X, padx=20, pady=20)
        
        # Botones del menú
        self._create_menu_button(self.sidebar, "📊 Análisis", self._show_analysis_screen)
        self._create_menu_button(self.sidebar, "📋 Gestión de BBPP", self._show_bbpp_management_screen)
        self._create_menu_button(self.sidebar, "⚙️ Configuración", self._show_config_screen)
        self._create_menu_button(self.sidebar, "📈 Métricas", self._show_metrics_dashboard)
        self._create_menu_button(self.sidebar, "📝 Notas de Versión", self._show_version_notes)
        
        # Espaciador
        tk.Frame(self.sidebar, bg=PRIMARY_COLOR).pack(fill=tk.BOTH, expand=True)
        
        # Botón salir al final
        exit_btn = tk.Button(
            self.sidebar,
            text="🚪 Salir",
            command=self.root.quit,
            bg="#DC3545",
            fg="white",
            font=("Arial", 11),
            relief=tk.FLAT,
            cursor="hand2",
            pady=10
        )
        exit_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        # Logo y nombre de empresa
        self._create_company_branding()
    
    def _create_company_branding(self):
        """Crear sección de branding (logo + nombre de empresa)"""
        try:
            from src.branding_manager import get_branding_manager
            branding = get_branding_manager()
            
            # Frame contenedor para logo y nombre
            branding_frame = tk.Frame(self.sidebar, bg=PRIMARY_COLOR)
            branding_frame.pack(side=tk.BOTTOM, pady=10)
            
            # Intentar cargar y mostrar logo si está configurado
            logo_path = branding.get_logo_path()
            if logo_path and logo_path.exists() and branding.use_logo_in_ui():
                try:
                    from PIL import Image, ImageTk
                    
                    # Cargar imagen
                    img = Image.open(logo_path)
                    
                    # Obtener dimensiones configuradas
                    logo_width, logo_height = branding.get_logo_dimensions()
                    
                    # Redimensionar manteniendo aspecto
                    img.thumbnail((logo_width, logo_height), Image.Resampling.LANCZOS)
                    
                    # Convertir a PhotoImage
                    photo = ImageTk.PhotoImage(img)
                    
                    # Crear label con imagen
                    logo_label = tk.Label(
                        branding_frame,
                        image=photo,
                        bg=PRIMARY_COLOR
                    )
                    logo_label.image = photo  # Mantener referencia
                    logo_label.pack(pady=(0, 5))
                    
                except Exception as e:
                    print(f"⚠️ No se pudo cargar el logo: {e}")
                    # Continuar sin logo
            
            # Nombre de empresa (siempre se muestra)
            company_name = branding.get_company_name()
            self.company_label = tk.Label(
                branding_frame,
                text=company_name,
                bg=PRIMARY_COLOR,
                fg="white",
                font=("Arial", 10, "bold")
            )
            self.company_label.pack()
            
        except Exception as e:
            print(f"⚠️ Error al cargar branding: {e}")
            # Fallback: mostrar solo el nombre de empresa por defecto
            self.company_label = tk.Label(
                self.sidebar,
                text=COMPANY,
                bg=PRIMARY_COLOR,
                fg="white",
                font=("Arial", 10, "bold")
            )
            self.company_label.pack(side=tk.BOTTOM, pady=10)
    
    def refresh_sidebar(self):
        """Refrescar sidebar para mostrar cambios de branding"""
        try:
            from src.branding_manager import get_branding_manager
            branding = get_branding_manager()
            
            # Solo actualizar el texto del label de empresa si existe
            if hasattr(self, 'company_label') and self.company_label.winfo_exists():
                new_company_name = branding.get_company_name()
                self.company_label.config(text=new_company_name)
                print(f"✅ Nombre de empresa actualizado a: {new_company_name}")
            else:
                print("⚠️ No se encontró el label de empresa para actualizar")
        except Exception as e:
            print(f"⚠️ Error al refrescar sidebar: {e}")
            import traceback
            traceback.print_exc()
        
    def _create_menu_button(self, parent, text, command):
        """Crear botón del menú"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=SECONDARY_COLOR,
            fg="white",
            font=("Arial", 11),
            relief=tk.FLAT,
            cursor="hand2",
            pady=10,
            anchor="w",
            padx=20
        )
        btn.pack(fill=tk.X, padx=10, pady=5)
        
        # Efecto hover
        btn.bind("<Enter>", lambda e: btn.config(bg="#0090D1"))
        btn.bind("<Leave>", lambda e: btn.config(bg=SECONDARY_COLOR))
        
        return btn
    
    def _create_main_area(self):
        """Crear área principal"""
        self.main_area = tk.Frame(self.root, bg=BG_COLOR)
        self.main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Por defecto, mostrar pantalla de análisis
        self._show_analysis_screen()
        
    def _create_status_bar(self):
        """Crear barra de estado"""
        self.status_bar = tk.Label(
            self.root,
            text="Listo",
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#E5E5E5",
            padx=10,
            pady=5
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _clear_main_area(self):
        """Limpiar área principal"""
        for widget in self.main_area.winfo_children():
            widget.destroy()
    
    # ========================================================================
    # PANTALLAS
    # ========================================================================
    
    def _show_analysis_screen(self):
        """Mostrar pantalla de análisis"""
        self._clear_main_area()
        
        # Título
        title = tk.Label(
            self.main_area,
            text="Análisis de Buenas Prácticas",
            font=("Arial", 18, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        title.pack(pady=20)
        
        # Frame para selección de proyecto
        project_frame = tk.LabelFrame(
            self.main_area,
            text="Seleccionar Proyecto UiPath",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            padx=20,
            pady=20
        )
        project_frame.pack(padx=20, pady=10, fill=tk.X)
        
        # Entrada de ruta
        path_frame = tk.Frame(project_frame, bg=BG_COLOR)
        path_frame.pack(fill=tk.X)
        
        self.path_entry = tk.Entry(
            path_frame,
            font=("Arial", 11),
            width=50
        )
        self.path_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        browse_btn = tk.Button(
            path_frame,
            text="Examinar...",
            command=self._browse_project,
            bg=SECONDARY_COLOR,
            fg="white",
            font=("Arial", 10),
            cursor="hand2",
            padx=20
        )
        browse_btn.pack(side=tk.LEFT)
        
        # Botón de analizar
        analyze_btn = tk.Button(
            self.main_area,
            text="🔍 Analizar Proyecto",
            command=self._start_analysis,
            bg=PRIMARY_COLOR,
            fg="white",
            font=("Arial", 14, "bold"),
            cursor="hand2",
            pady=15,
            padx=40
        )
        analyze_btn.pack(pady=30)
        
        # Frame para botones de reportes
        reports_frame = tk.Frame(self.main_area, bg=BG_COLOR)
        reports_frame.pack(pady=5)
        
        # Botón para generar reporte HTML
        self.report_btn = tk.Button(
            reports_frame,
            text="📄 Generar HTML",
            command=self._generate_report,
            bg=SECONDARY_COLOR,
            fg="white",
            font=("Arial", 11, "bold"),
            cursor="hand2",
            pady=8,
            padx=20,
            state=tk.DISABLED
        )
        self.report_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón para generar reporte Excel
        self.excel_btn = tk.Button(
            reports_frame,
            text="📊 Generar Excel",
            command=self._generate_excel_report,
            bg="#217346",  # Verde Excel
            fg="white",
            font=("Arial", 11, "bold"),
            cursor="hand2",
            pady=8,
            padx=20,
            state=tk.DISABLED
        )
        self.excel_btn.pack(side=tk.LEFT, padx=5)
        
        # Variable para almacenar resultados
        self.last_results = None
        
        # Área de resultados (placeholder)
        results_frame = tk.LabelFrame(
            self.main_area,
            text="Resultados",
            font=("Arial", 12, "bold"),
            bg=BG_COLOR,
            padx=20,
            pady=20
        )
        results_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        self.results_text = tk.Text(
            results_frame,
            font=("Courier", 10),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(results_frame, command=self.results_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=scrollbar.set)
        
    def _show_config_screen(self):
        """Mostrar pantalla de configuración"""
        self._clear_main_area()
        
        # Contenedor principal con scroll
        canvas = tk.Canvas(self.main_area, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_area, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Título
        title = tk.Label(
            scrollable_frame,
            text="⚙️ Configuración",
            font=("Arial", 20, "bold"),
            bg=BG_COLOR,
            fg=PRIMARY_COLOR
        )
        title.pack(pady=20)
        
        # Cargar configuración actual
        config = load_user_config()
        
        # Variables para los controles
        self.config_vars = {}
        
        # ========== SECCIÓN 1: UMBRALES ==========
        self._create_config_section(
            scrollable_frame,
            "📊 Umbrales de Análisis",
            "Configura los límites para las reglas de análisis"
        )
        
        # Frame para umbrales
        thresholds_frame = tk.Frame(scrollable_frame, bg=BG_COLOR)
        thresholds_frame.pack(padx=40, pady=10, fill=tk.X)
        
        # Umbral: Actividades máximas por Sequence
        self._create_threshold_input(
            thresholds_frame,
            "max_activities_sequence",
            "Máximo de actividades por Sequence:",
            config.get("thresholds", {}).get("max_activities_sequence", 20),
            "Número máximo de actividades permitidas en un Sequence"
        )
        
        # Umbral: IFs anidados
        self._create_threshold_input(
            thresholds_frame,
            "max_nested_ifs",
            "Máximo de IFs anidados:",
            config.get("thresholds", {}).get("max_nested_ifs", 3),
            "Nivel máximo de anidamiento de IFs permitido"
        )
        
        # Umbral: Código comentado
        self._create_threshold_input(
            thresholds_frame,
            "max_commented_code_percent",
            "Máximo % de código comentado:",
            config.get("thresholds", {}).get("max_commented_code_percent", 5),
            "Porcentaje máximo de código comentado permitido"
        )
        
        # ========== SECCIÓN 2: VALIDACIONES ==========
        self._create_config_section(
            scrollable_frame,
            "✅ Opciones de Validación",
            "Activa o desactiva validaciones específicas"
        )
        
        # Frame para validaciones
        validations_frame = tk.Frame(scrollable_frame, bg=BG_COLOR)
        validations_frame.pack(padx=40, pady=10, fill=tk.X)
        
        # Validaciones opcionales
        self._create_validation_checkbox(
            validations_frame,
            "validate_variable_prefixes",
            "Validar prefijos in_/out_/io_ en argumentos",
            config.get("validations", {}).get("validate_variable_prefixes", True)
        )
        
        self._create_validation_checkbox(
            validations_frame,
            "validate_argument_descriptions",
            "Validar descripciones en argumentos",
            config.get("validations", {}).get("validate_argument_descriptions", True)
        )
        
        self._create_validation_checkbox(
            validations_frame,
            "validate_init_end_pattern",
            "Validar patrón Init/End en States",
            config.get("validations", {}).get("validate_init_end_pattern", False)
        )
        
        # ========== SECCIÓN 3: OPCIONES DE SALIDA ==========
        self._create_config_section(
            scrollable_frame,
            "📄 Opciones de Reportes",
            "Configura el formato y contenido de los reportes"
        )
        
        # Frame para opciones de salida
        output_frame = tk.Frame(scrollable_frame, bg=BG_COLOR)
        output_frame.pack(padx=40, pady=10, fill=tk.X)
        
        # AUTO-GENERACIÓN DE REPORTES (NUEVO)
        self._create_output_checkbox(
            output_frame,
            "auto_generate_reports",
            "✨ Generar reportes automáticamente (recomendado)",
            config.get("output", {}).get("auto_generate_reports", True)
        )
        
        # Nota informativa
        info_frame = tk.Frame(output_frame, bg="#E3F2FD", relief=tk.FLAT, bd=1)
        info_frame.pack(fill=tk.X, pady=(0, 10), padx=20)
        
        info_label = tk.Label(
            info_frame,
            text="ℹ️  Recomendable dejarlo activado para poder acceder siempre al reporte.\n"
                 "   En caso contrario, pulsar 'Generar Reporte' en el análisis.",
            font=("Arial", 8),
            bg="#E3F2FD",
            fg="#1976D2",
            justify=tk.LEFT,
            anchor="w",
            padx=10,
            pady=5
        )
        info_label.pack(fill=tk.X)
        
        # Opciones de formato
        self._create_output_checkbox(
            output_frame,
            "generate_html",
            "Generar reporte HTML",
            config.get("output", {}).get("generate_html", True)
        )
        
        self._create_output_checkbox(
            output_frame,
            "generate_excel",
            "Generar reporte Excel",
            config.get("output", {}).get("generate_excel", False)
        )
        
        self._create_output_checkbox(
            output_frame,
            "include_charts",
            "Incluir gráficos en reportes",
            config.get("output", {}).get("include_charts", True)
        )
        
        # ========== SECCIÓN 4: LOGO PERSONALIZADO ==========
        self._create_config_section(
            scrollable_frame,
            "🎨 Logo Personalizado",
            "Configura el logo que aparece en los reportes"
        )
        
        # Frame para logo
        logo_frame = tk.Frame(scrollable_frame, bg=BG_COLOR)
        logo_frame.pack(padx=40, pady=10, fill=tk.X)
        
        # Label con ruta actual del logo
        logo_path = config.get("custom_logo", "Logo por defecto")
        self.logo_path_label = tk.Label(
            logo_frame,
            text=f"Logo actual: {logo_path}",
            font=("Arial", 10),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            anchor="w"
        )
        self.logo_path_label.pack(fill=tk.X, pady=5)
        
        # Botones para logo
        logo_buttons_frame = tk.Frame(logo_frame, bg=BG_COLOR)
        logo_buttons_frame.pack(pady=5)
        
        select_logo_btn = tk.Button(
            logo_buttons_frame,
            text="📁 Seleccionar Logo",
            command=self._select_custom_logo,
            bg=PRIMARY_COLOR,
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=5
        )
        select_logo_btn.pack(side=tk.LEFT, padx=5)
        
        reset_logo_btn = tk.Button(
            logo_buttons_frame,
            text="🔄 Restaurar Logo",
            command=self._reset_logo,
            bg=SECONDARY_COLOR,
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=5
        )
        reset_logo_btn.pack(side=tk.LEFT, padx=5)
        
        # ========== SECCIÓN 5: CONFIGURACIÓN DE EMPRESA ==========
        self._create_config_section(
            scrollable_frame,
            "🏢 Configuración de Empresa",
            "Configura el nombre de tu empresa que aparece en la aplicación"
        )
        
        # Frame para configuración de empresa
        company_frame = tk.Frame(scrollable_frame, bg=BG_COLOR)
        company_frame.pack(padx=40, pady=10, fill=tk.X)
        
        # Importar branding_manager
        try:
            from src.branding_manager import get_branding_manager
            branding = get_branding_manager()
            
            # Nombre de Empresa
            name_row = tk.Frame(company_frame, bg=BG_COLOR)
            name_row.pack(fill=tk.X, pady=5)
            
            tk.Label(
                name_row,
                text="Nombre de Empresa:",
                font=("Arial", 10),
                bg=BG_COLOR,
                fg=TEXT_COLOR,
                width=25,
                anchor="w"
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            self.company_name_var = tk.StringVar(value=branding.get_company_name())
            company_name_entry = tk.Entry(
                name_row,
                textvariable=self.company_name_var,
                font=("Arial", 10)
            )
            company_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Nombre Corto
            short_name_row = tk.Frame(company_frame, bg=BG_COLOR)
            short_name_row.pack(fill=tk.X, pady=5)
            
            tk.Label(
                short_name_row,
                text="Nombre Corto:",
                font=("Arial", 10),
                bg=BG_COLOR,
                fg=TEXT_COLOR,
                width=25,
                anchor="w"
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            self.company_short_name_var = tk.StringVar(value=branding.get_company_short_name())
            short_name_entry = tk.Entry(
                short_name_row,
                textvariable=self.company_short_name_var,
                font=("Arial", 10)
            )
            short_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Botón Guardar Configuración de Empresa
            save_company_btn = tk.Button(
                company_frame,
                text="💾 Guardar Configuración de Empresa",
                command=self._save_company_settings,
                bg=COLOR_SUCCESS,
                fg="white",
                font=("Arial", 10, "bold"),
                relief=tk.FLAT,
                cursor="hand2",
                padx=15,
                pady=8
            )
            save_company_btn.pack(pady=(10, 0))
            
        except Exception as e:
            error_label = tk.Label(
                company_frame,
                text=f"⚠️ Error al cargar configuración de empresa: {e}",
                font=("Arial", 9),
                bg=BG_COLOR,
                fg="red"
            )
            error_label.pack()
        
        # ========== BOTONES DE ACCIÓN ==========
        buttons_frame = tk.Frame(scrollable_frame, bg=BG_COLOR)
        buttons_frame.pack(pady=30)
        
        # Botón Guardar
        save_btn = tk.Button(
            buttons_frame,
            text="💾 Guardar Configuración",
            command=self._save_configuration,
            bg=COLOR_SUCCESS,
            fg="white",
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=10
        )
        save_btn.pack(side=tk.LEFT, padx=10)
        
        # Botón Restaurar Valores por Defecto
        reset_btn = tk.Button(
            buttons_frame,
            text="🔄 Restaurar Valores por Defecto",
            command=self._reset_configuration,
            bg="#FFC107",
            fg="white",
            font=("Arial", 12),
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=10
        )
        reset_btn.pack(side=tk.LEFT, padx=10)
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def _create_config_section(self, parent, title, description):
        """Crear sección de configuración con título y descripción"""
        section_frame = tk.Frame(parent, bg=BG_COLOR)
        section_frame.pack(padx=20, pady=(20, 5), fill=tk.X)
        
        # Título de sección
        title_label = tk.Label(
            section_frame,
            text=title,
            font=("Arial", 14, "bold"),
            bg=BG_COLOR,
            fg=PRIMARY_COLOR,
            anchor="w"
        )
        title_label.pack(fill=tk.X)
        
        # Descripción
        desc_label = tk.Label(
            section_frame,
            text=description,
            font=("Arial", 9),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            anchor="w"
        )
        desc_label.pack(fill=tk.X)
        
        # Línea separadora
        separator = tk.Frame(section_frame, bg=PRIMARY_COLOR, height=2)
        separator.pack(fill=tk.X, pady=5)
        
    def _create_threshold_input(self, parent, key, label_text, default_value, tooltip):
        """Crear input para umbral numérico"""
        row_frame = tk.Frame(parent, bg=BG_COLOR)
        row_frame.pack(fill=tk.X, pady=5)
        
        # Label
        label = tk.Label(
            row_frame,
            text=label_text,
            font=("Arial", 10),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            width=35,
            anchor="w"
        )
        label.pack(side=tk.LEFT, padx=5)
        
        # Entry
        var = tk.IntVar(value=default_value)
        self.config_vars[key] = var
        
        entry = tk.Entry(
            row_frame,
            textvariable=var,
            font=("Arial", 10),
            width=10
        )
        entry.pack(side=tk.LEFT, padx=5)
        
        # Tooltip
        tooltip_label = tk.Label(
            row_frame,
            text=f"ℹ️ {tooltip}",
            font=("Arial", 8),
            bg=BG_COLOR,
            fg="#666",
            anchor="w"
        )
        tooltip_label.pack(side=tk.LEFT, padx=10)
        
    def _create_validation_checkbox(self, parent, key, label_text, default_value):
        """Crear checkbox para validación"""
        var = tk.BooleanVar(value=default_value)
        self.config_vars[key] = var
        
        checkbox = tk.Checkbutton(
            parent,
            text=label_text,
            variable=var,
            font=("Arial", 10),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            selectcolor=BG_COLOR,
            activebackground=BG_COLOR,
            anchor="w"
        )
        checkbox.pack(fill=tk.X, pady=3, padx=5)
        
    def _create_output_checkbox(self, parent, key, label_text, default_value):
        """Crear checkbox para opción de salida"""
        var = tk.BooleanVar(value=default_value)
        self.config_vars[key] = var
        
        checkbox = tk.Checkbutton(
            parent,
            text=label_text,
            variable=var,
            font=("Arial", 10),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            selectcolor=BG_COLOR,
            activebackground=BG_COLOR,
            anchor="w"
        )
        checkbox.pack(fill=tk.X, pady=3, padx=5)
        
    def _select_custom_logo(self):
        """Seleccionar logo personalizado"""
        filetypes = [
            ("Imágenes", "*.png *.jpg *.jpeg *.gif"),
            ("Todos los archivos", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="Seleccionar Logo",
            filetypes=filetypes
        )
        
        if filepath:
            # Actualizar label
            self.logo_path_label.config(text=f"Logo actual: {filepath}")
            # Guardar en configuración temporal
            self.custom_logo_path = filepath
            messagebox.showinfo(
                "Logo Seleccionado",
                f"Logo seleccionado correctamente.\nNo olvides guardar la configuración."
            )
            
    def _reset_logo(self):
        """Restaurar logo por defecto"""
        self.logo_path_label.config(text="Logo actual: Logo por defecto")
        self.custom_logo_path = None
        messagebox.showinfo(
            "Logo Restaurado",
            "Logo restaurado al valor por defecto.\nNo olvides guardar la configuración."
        )
        
    def _save_configuration(self):
        """Guardar toda la configuración"""
        try:
            # Cargar config actual
            config = load_user_config()
            
            # Actualizar umbrales
            config["thresholds"] = {
                "max_activities_sequence": self.config_vars.get("max_activities_sequence", tk.IntVar(value=20)).get(),
                "max_nested_ifs": self.config_vars.get("max_nested_ifs", tk.IntVar(value=3)).get(),
                "max_commented_code_percent": self.config_vars.get("max_commented_code_percent", tk.IntVar(value=5)).get()
            }
            
            # Actualizar validaciones
            config["validations"] = {
                "validate_variable_prefixes": self.config_vars.get("validate_variable_prefixes", tk.BooleanVar(value=True)).get(),
                "validate_argument_descriptions": self.config_vars.get("validate_argument_descriptions", tk.BooleanVar(value=True)).get(),
                "validate_init_end_pattern": self.config_vars.get("validate_init_end_pattern", tk.BooleanVar(value=False)).get()
            }
            
            # Actualizar opciones de salida
            config["output"] = {
                "auto_generate_reports": self.config_vars.get("auto_generate_reports", tk.BooleanVar(value=True)).get(),
                "generate_html": self.config_vars.get("generate_html", tk.BooleanVar(value=True)).get(),
                "generate_excel": self.config_vars.get("generate_excel", tk.BooleanVar(value=False)).get(),
                "include_charts": self.config_vars.get("include_charts", tk.BooleanVar(value=True)).get()
            }
            
            # Actualizar logo personalizado si se cambió
            if hasattr(self, 'custom_logo_path'):
                config["custom_logo"] = self.custom_logo_path
            
            # Guardar
            if save_user_config(config):
                messagebox.showinfo(
                    "✅ Configuración Guardada",
                    "La configuración se ha guardado correctamente."
                )
            else:
                messagebox.showerror(
                    "❌ Error",
                    "No se pudo guardar la configuración."
                )
                
        except Exception as e:
            messagebox.showerror(
                "❌ Error",
                f"Error al guardar la configuración:\n{str(e)}"
            )
            
    def _reset_configuration(self):
        """Restaurar configuración a valores por defecto"""
        confirm = messagebox.askyesno(
            "⚠️ Confirmar Restauración",
            "¿Estás seguro de que quieres restaurar todos los valores por defecto?\n\nEsta acción no se puede deshacer."
        )
        
        if confirm:
            if reset_to_defaults():
                messagebox.showinfo(
                    "✅ Restaurado",
                    "La configuración ha sido restaurada a los valores por defecto.\n\nRecarga la pantalla para ver los cambios."
                )
                # Recargar pantalla
                self._show_config_screen()
            else:
                messagebox.showerror(
                    "❌ Error",
                    "No se pudo restaurar la configuración."
                )
        
    def _save_company_settings(self):
        """Guardar configuración de empresa"""
        try:
            from src.branding_manager import get_branding_manager
            branding = get_branding_manager()
            
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
            success_name = branding.set_company_name(company_name)
            success_short = branding.set_company_short_name(company_short_name)
            
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
                    self.refresh_sidebar()
                    print("✅ Sidebar refrescado correctamente")
                except Exception as e:
                    print(f"⚠️ Error al refrescar sidebar: {e}")
                    import traceback
                    traceback.print_exc()
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
        
    def _show_version_notes(self):
        """Mostrar notas de versión desde CHANGELOG.md"""
        self._clear_main_area()
        
        # Importar y mostrar pantalla de release notes
        from src.ui.release_notes_screen import ReleaseNotesScreen
        
        release_notes = ReleaseNotesScreen(self.main_area)
        release_notes.pack(fill=tk.BOTH, expand=True)
    
    def _show_metrics_dashboard(self):
        """Mostrar dashboard de métricas"""
        self._clear_main_area()
        
        # Importar y mostrar dashboard de métricas
        from src.ui.metrics_dashboard import show_metrics_dashboard
        
        dashboard = show_metrics_dashboard(self.main_area, self.project_path)
        dashboard.pack(fill=tk.BOTH, expand=True)
        
    # ========================================================================
    # FUNCIONES
    # ========================================================================
    
    def _browse_project(self):
        """Abrir diálogo para seleccionar carpeta de proyecto"""
        folder = filedialog.askdirectory(
            title="Seleccionar carpeta de proyecto UiPath"
        )
        if folder:
            self.project_path = Path(folder)
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, str(self.project_path))
            self.status_bar.config(text=f"Proyecto seleccionado: {self.project_path.name}")
    
    def _start_analysis(self):
        """Iniciar análisis del proyecto"""
        if not self.project_path:
            messagebox.showwarning(
                "Advertencia",
                "Por favor, selecciona una carpeta de proyecto primero"
            )
            return
        
        # Importar módulos necesarios
        from src.project_scanner import ProjectScanner
        from src.config import DEFAULT_CONFIG
        import threading
        
        # Limpiar resultados previos
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", "Iniciando análisis...\n\n")
        self.results_text.config(state=tk.DISABLED)
        
        # Crear barra de progreso
        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title("Analizando proyecto...")
        self.progress_window.geometry("500x150")
        self.progress_window.transient(self.root)
        self.progress_window.grab_set()
        
        # Centrar ventana de progreso
        self.progress_window.update_idletasks()
        x = (self.progress_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.progress_window.winfo_screenheight() // 2) - (150 // 2)
        self.progress_window.geometry(f"500x150+{x}+{y}")
        
        # Label de archivo actual
        self.progress_label = tk.Label(
            self.progress_window,
            text="Buscando archivos XAML...",
            font=("Arial", 10),
            wraplength=450
        )
        self.progress_label.pack(pady=20)
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(
            self.progress_window,
            length=450,
            mode='determinate'
        )
        self.progress_bar.pack(pady=10)
        
        # Label de porcentaje
        self.progress_percent_label = tk.Label(
            self.progress_window,
            text="0%",
            font=("Arial", 10, "bold")
        )
        self.progress_percent_label.pack(pady=5)
        
        # Botón cancelar (por ahora solo cierra)
        cancel_btn = tk.Button(
            self.progress_window,
            text="Cancelar",
            command=self._cancel_analysis
        )
        cancel_btn.pack(pady=10)
        
        self.analysis_cancelled = False
        
        # Función de callback para progreso
        def progress_callback(file_name, percentage):
            if self.analysis_cancelled:
                return
            
            self.progress_label.config(text=f"Analizando: {file_name}")
            self.progress_bar['value'] = percentage
            self.progress_percent_label.config(text=f"{int(percentage)}%")
            self.progress_window.update()
        
        # Función para ejecutar análisis en thread separado
        def run_analysis():
            try:
                # Cargar configuración del usuario (no DEFAULT_CONFIG)
                user_config = load_user_config()
                scanner = ProjectScanner(self.project_path, user_config)
                results = scanner.scan(progress_callback)
                
                # Al terminar, actualizar UI en el thread principal
                self.root.after(0, lambda: self._show_results(results, scanner))
                
            except Exception as e:
                self.root.after(0, lambda: self._show_error(str(e)))
        
        # Iniciar análisis en thread separado
        analysis_thread = threading.Thread(target=run_analysis, daemon=True)
        analysis_thread.start()
    
    def _cancel_analysis(self):
        """Cancelar análisis en curso"""
        self.analysis_cancelled = True
        if hasattr(self, 'progress_window'):
            self.progress_window.destroy()
        self.status_bar.config(text="Análisis cancelado")
    
    def _show_results(self, results, scanner):
        """Mostrar resultados del análisis"""
        # Guardar resultados para reporte
        self.last_results = results
        
        # Cargar configuración para verificar opciones de salida
        config = load_user_config()
        output_options = config.get('output', {})
        
        # Habilitar botones según configuración
        if output_options.get('generate_html', True):
            self.report_btn.config(state=tk.NORMAL)
        else:
            self.report_btn.config(state=tk.DISABLED)
        
        if output_options.get('generate_excel', False):
            self.excel_btn.config(state=tk.NORMAL)
        else:
            self.excel_btn.config(state=tk.DISABLED)
        
        # Cerrar ventana de progreso
        if hasattr(self, 'progress_window'):
            self.progress_window.destroy()
        
        if not results.get('success'):
            self._show_error(results.get('error', 'Error desconocido'))
            return
        
        # Actualizar área de resultados
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        
        # Mostrar resumen
        summary = scanner.get_summary()
        self.results_text.insert("1.0", summary)
        
        # Agregar hallazgos detallados si existen
        findings = results.get('findings', [])
        if findings:
            self.results_text.insert(tk.END, "\n\n" + "="*60 + "\n")
            self.results_text.insert(tk.END, "HALLAZGOS DETALLADOS:\n")
            self.results_text.insert(tk.END, "="*60 + "\n\n")
            
            for idx, finding in enumerate(findings[:50], 1):  # Limitar a 50
                severity_symbol = {
                    'error': '❌',
                    'warning': '⚠️',
                    'info': 'ℹ️'
                }.get(finding['severity'], '•')
                
                self.results_text.insert(
                    tk.END,
                    f"{idx}. {severity_symbol} [{finding['category'].upper()}] "
                    f"{finding['description']}\n"
                )
                self.results_text.insert(
                    tk.END,
                    f"   Archivo: {Path(finding['file_path']).name}\n"
                )
                if finding.get('location'):
                    self.results_text.insert(
                        tk.END,
                        f"   Ubicación: {finding['location']}\n"
                    )
                self.results_text.insert(tk.END, "\n")
            
            if len(findings) > 50:
                self.results_text.insert(
                    tk.END,
                    f"\n... y {len(findings) - 50} hallazgos más.\n"
                )
        
        self.results_text.config(state=tk.DISABLED)
        
        # Actualizar barra de estado
        score = results.get('score', {}).get('score', 0)
        self.status_bar.config(
            text=f"Análisis completado - Score: {score}/100"
        )
        
        # Mostrar mensaje de éxito
        messagebox.showinfo(
            "Análisis Completado",
            f"Proyecto analizado con éxito.\n\n"
            f"Score: {score}/100\n"
            f"Hallazgos: {results['statistics']['total_findings']}\n"
            f"Archivos analizados: {results['analyzed_files']}"
        )
    
    def _generate_report(self):
        """Generar reporte HTML"""
        if not self.last_results:
            messagebox.showwarning(
                "Advertencia",
                "No hay resultados para generar reporte.\nPor favor, analiza un proyecto primero."
            )
            return
        
        try:
            from src.report_generator import HTMLReportGenerator
            from datetime import datetime
            
            # Crear nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name = self.last_results['project_info'].get('name', 'proyecto')
            output_file = Path(f"output/reporte_{project_name}_{timestamp}.html")
            
            # Generar reporte
            generator = HTMLReportGenerator(self.last_results, output_file)
            report_path = generator.generate()
            
            # Preguntar si abrir el reporte
            result = messagebox.askyesno(
                "Reporte Generado",
                f"Reporte HTML generado con éxito:\n\n{report_path}\n\n¿Deseas abrirlo ahora?"
            )
            
            if result:
                import webbrowser
                webbrowser.open(str(report_path.absolute()))
            
            self.status_bar.config(text=f"Reporte generado: {report_path.name}")
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al generar el reporte:\n\n{str(e)}"
            )
    
    def _generate_excel_report(self):
        """Generar reporte Excel"""
        if not self.last_results:
            messagebox.showwarning(
                "Advertencia",
                "No hay resultados para generar reporte.\nPor favor, analiza un proyecto primero."
            )
            return
        
        try:
            from src.excel_report_generator import ExcelReportGenerator
            from datetime import datetime
            
            # Crear nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name = self.last_results['project_info'].get('name', 'proyecto')
            output_file = Path(f"output/reporte_{project_name}_{timestamp}.xlsx")
            
            # Cargar configuración para gráficos
            config = load_user_config()
            include_charts = config.get('output', {}).get('include_charts', True)
            
            # Generar reporte
            generator = ExcelReportGenerator(
                self.last_results, 
                output_file,
                include_charts=include_charts
            )
            report_path = generator.generate()
            
            # Preguntar si abrir el reporte
            result = messagebox.askyesno(
                "Reporte Excel Generado",
                f"Reporte Excel generado con éxito:\n\n{report_path}\n\n¿Deseas abrirlo ahora?"
            )
            
            if result:
                import os
                os.startfile(str(report_path.absolute()))
            
            self.status_bar.config(text=f"Reporte Excel generado: {report_path.name}")
            
        except ImportError:
            messagebox.showerror(
                "Error",
                "No se pudo importar el generador de Excel.\n\n"
                "Asegúrate de tener instalado: pip install openpyxl"
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al generar el reporte Excel:\n\n{str(e)}"
            )
    
    def _show_error(self, error_message):
        """Mostrar error en el análisis"""
        if hasattr(self, 'progress_window'):
            self.progress_window.destroy()
        
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", f"ERROR: {error_message}\n")
        self.results_text.config(state=tk.DISABLED)
        
        self.status_bar.config(text="Error en el análisis")
        
        messagebox.showerror(
            "Error",
            f"Error durante el análisis:\n\n{error_message}"
        )
    
    # ========================================================================
    # GESTIÓN DE CONJUNTOS DE BBPP
    # ========================================================================
    
    def _show_bbpp_management_screen(self):
        """Mostrar pantalla de gestión de reglas BBPP"""
        # Limpiar área principal
        for widget in self.main_area.winfo_children():
            widget.destroy()
        
        # Importar y crear pantalla de gestión de reglas
        try:
            from src.ui.rules_management_screen import RulesManagementScreen
            RulesManagementScreen(self.main_area)
        except Exception as e:
            # Si falla, mostrar mensaje de error
            import traceback
            error_frame = tk.Frame(self.main_area, bg=BG_COLOR)
            error_frame.pack(fill=tk.BOTH, expand=True)
            
            error_text = f"❌ Error al cargar Gestión de Reglas:\n\n{str(e)}\n\n{traceback.format_exc()}"
            error_label = tk.Label(
                error_frame,
                text=error_text,
                font=("Arial", 10),
                bg=BG_COLOR,
                fg="red",
                justify=tk.LEFT,
                padx=20,
                pady=20
            )
            error_label.pack(fill=tk.BOTH, expand=True)
    
    def _show_bbpp_management_screen(self):
        """Mostrar pantalla de gestión de reglas BBPP"""
        self._clear_main_area()
        
        # Importar y crear pantalla de gestión de reglas
        try:
            from src.ui.rules_management_screen import RulesManagementScreen
            RulesManagementScreen(self.main_area)
        except Exception as e:
            # Si falla, mostrar mensaje de error
            import traceback
            error_frame = tk.Frame(self.main_area, bg=BG_COLOR)
            error_frame.pack(fill=tk.BOTH, expand=True)
            
            error_text = f"❌ Error al cargar Gestión de Reglas:\n\n{str(e)}\n\n{traceback.format_exc()}"
            error_label = tk.Label(
                error_frame,
                text=error_text,
                font=("Arial", 10),
                bg=BG_COLOR,
                fg="red",
                justify=tk.LEFT,
                padx=20,
                pady=20
            )
            error_label.pack(fill=tk.BOTH, expand=True)
    
    def _create_bbpp_set_card(self, parent, set_name, set_info, rules_mgr):
        """Crear tarjeta para un conjunto de BBPP"""
        # Frame para lista de conjuntos
        list_frame = tk.LabelFrame(
            content_frame,
            text="Conjuntos Disponibles",
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            padx=15,
            pady=15
        )
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Cargar conjuntos disponibles
        from src.config import get_available_bbpp_sets
        available_sets = get_available_bbpp_sets()
        
        # Crear checkboxes para cada conjunto
        self.bbpp_checkboxes = {}
        
        if not available_sets:
            no_sets_label = tk.Label(
                list_frame,
                text="⚠️ No se encontraron conjuntos de BBPP en config/bbpp/",
                font=("Arial", 11),
                bg=BG_COLOR,
                fg="#FFC107"
            )
            no_sets_label.pack(pady=20)
        else:
            for bbpp_set in available_sets:
                # Frame para cada conjunto
                set_frame = tk.Frame(list_frame, bg=BG_COLOR)
                set_frame.pack(fill=tk.X, pady=8)
                
                # Checkbox
                var = tk.BooleanVar(value=bbpp_set['is_active'])
                checkbox = tk.Checkbutton(
                    set_frame,
                    variable=var,
                    bg=BG_COLOR,
                    font=("Arial", 11),
                    cursor="hand2"
                )
                checkbox.pack(side=tk.LEFT, padx=(0, 10))
                
                # Guardar referencia
                self.bbpp_checkboxes[bbpp_set['filename']] = var
                
                # Info del conjunto
                info_frame = tk.Frame(set_frame, bg=BG_COLOR)
                info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Nombre del conjunto
                name_label = tk.Label(
                    info_frame,
                    text=bbpp_set['name'],
                    font=("Arial", 12, "bold"),
                    bg=BG_COLOR,
                    fg=TEXT_COLOR,
                    anchor=tk.W
                )
                name_label.pack(anchor=tk.W)
                
                # Detalles
                details = f"📄 {bbpp_set['filename']} • {bbpp_set['rules_count']} reglas • v{bbpp_set['version']}"
                details_label = tk.Label(
                    info_frame,
                    text=details,
                    font=("Arial", 9),
                    bg=BG_COLOR,
                    fg="#666666",
                    anchor=tk.W
                )
                details_label.pack(anchor=tk.W)
                
                # Descripción si existe
                if bbpp_set['description']:
                    desc_label = tk.Label(
                        info_frame,
                        text=bbpp_set['description'],
                        font=("Arial", 9, "italic"),
                        bg=BG_COLOR,
                        fg="#888888",
                        anchor=tk.W,
                        wraplength=600
                    )
                    desc_label.pack(anchor=tk.W, pady=(2, 0))
                
                # Separador
                separator = tk.Frame(list_frame, bg="#E0E0E0", height=1)
                separator.pack(fill=tk.X, pady=5)
        
        # Frame para botones principales
        buttons_frame = tk.Frame(content_frame, bg=BG_COLOR)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Botón Guardar
        save_btn = tk.Button(
            buttons_frame,
            text="💾 Guardar Configuración",
            command=self._save_bbpp_configuration,
            bg=PRIMARY_COLOR,
            fg="white",
            font=("Arial", 11, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=10
        )
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón Seleccionar Todos
        select_all_btn = tk.Button(
            buttons_frame,
            text="☑️ Seleccionar Todos",
            command=lambda: self._toggle_all_bbpp(True),
            bg=SECONDARY_COLOR,
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=10
        )
        select_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón Deseleccionar Todos
        deselect_all_btn = tk.Button(
            buttons_frame,
            text="☐ Deseleccionar Todos",
            command=lambda: self._toggle_all_bbpp(False),
            bg="#6C757D",
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=10
        )
        deselect_all_btn.pack(side=tk.LEFT)
        
        # Frame para botones de Exportar/Importar
        export_import_frame = tk.Frame(content_frame, bg=BG_COLOR)
        export_import_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Botón Exportar Conjunto Individual
        export_btn = tk.Button(
            export_import_frame,
            text="📤 Exportar Conjunto",
            command=self._export_bbpp_set,
            bg="#28A745",
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=8
        )
        export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón Importar Conjunto
        import_btn = tk.Button(
            export_import_frame,
            text="📥 Importar Conjunto",
            command=self._import_bbpp_set,
            bg="#17A2B8",
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=8
        )
        import_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón Exportar Configuración Completa
        export_all_btn = tk.Button(
            export_import_frame,
            text="📦 Exportar Config Completa",
            command=self._export_all_configuration,
            bg="#FFC107",
            fg="black",
            font=("Arial", 10),
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=8
        )
        export_all_btn.pack(side=tk.LEFT)
        
        # Info adicional
        info_label = tk.Label(
            content_frame,
            text="💡 Tip: Puedes crear tus propios conjuntos agregando archivos JSON en config/bbpp/",
            font=("Arial", 9, "italic"),
            bg=BG_COLOR,
            fg="#666666"
        )
        info_label.pack(side=tk.BOTTOM, pady=(10, 0))
        
        self.status_bar.config(text="Gestión de Conjuntos de BBPP")
    
    def _toggle_all_bbpp(self, state: bool):
        """Seleccionar o deseleccionar todos los conjuntos"""
        for var in self.bbpp_checkboxes.values():
            var.set(state)
    
    def _save_bbpp_configuration(self):
        """Guardar configuración de conjuntos activos"""
        # Obtener conjuntos activos
        active_sets = [
            filename for filename, var in self.bbpp_checkboxes.items()
            if var.get()
        ]
        
        # Guardar en config
        from src.config import set_active_bbpp_sets
        
        if set_active_bbpp_sets(active_sets):
            messagebox.showinfo(
                "Configuración Guardada",
                f"✅ Se han activado {len(active_sets)} conjunto(s) de BBPP.\n\n"
                "Los cambios se aplicarán en el próximo análisis."
            )
            self.status_bar.config(text=f"Configuración guardada: {len(active_sets)} conjunto(s) activo(s)")
        else:
            messagebox.showerror(
                "Error",
                "❌ No se pudo guardar la configuración.\n\n"
                "Verifica los permisos de escritura en config/user_config.json"
            )
    
    def _export_bbpp_set(self):
        """Exportar un conjunto de BBPP individual"""
        from src.config import get_available_bbpp_sets, export_bbpp_set
        
        # Obtener conjuntos disponibles
        available_sets = get_available_bbpp_sets()
        
        if not available_sets:
            messagebox.showwarning(
                "Sin Conjuntos",
                "No hay conjuntos disponibles para exportar"
            )
            return
        
        # Crear ventana de selección
        select_window = tk.Toplevel(self.root)
        select_window.title("Seleccionar Conjunto a Exportar")
        select_window.geometry("500x400")
        select_window.transient(self.root)
        select_window.grab_set()
        
        # Centrar ventana
        select_window.update_idletasks()
        x = (select_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (select_window.winfo_screenheight() // 2) - (400 // 2)
        select_window.geometry(f"500x400+{x}+{y}")
        
        # Título
        tk.Label(
            select_window,
            text="Selecciona el conjunto a exportar:",
            font=("Arial", 12, "bold"),
            pady=15
        ).pack()
        
        # Lista de conjuntos
        selected_set = tk.StringVar()
        
        list_frame = tk.Frame(select_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
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
        
        # Agregar conjuntos a la lista
        for bbpp_set in available_sets:
            display_text = f"{bbpp_set['name']} ({bbpp_set['filename']}) - {bbpp_set['rules_count']} reglas"
            listbox.insert(tk.END, display_text)
        
        def do_export():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Advertencia", "Por favor, selecciona un conjunto")
                return
            
            selected_index = selection[0]
            bbpp_set = available_sets[selected_index]
            
            # Pedir ubicación de guardado
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                title="Guardar conjunto como",
                defaultextension=".json",
                initialfile=bbpp_set['filename'],
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                from pathlib import Path
                if export_bbpp_set(Path(bbpp_set['filepath']), Path(filename)):
                    select_window.destroy()
                    messagebox.showinfo(
                        "Exportación Exitosa",
                        f"✅ Conjunto exportado correctamente a:\n{filename}"
                    )
                else:
                    messagebox.showerror(
                        "Error",
                        "❌ No se pudo exportar el conjunto"
                    )
        
        # Botones
        btn_frame = tk.Frame(select_window)
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="📤 Exportar",
            command=do_export,
            bg="#28A745",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Cancelar",
            command=select_window.destroy,
            bg="#6C757D",
            fg="white",
            font=("Arial", 10),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
    
    def _import_bbpp_set(self):
        """Importar un conjunto de BBPP desde archivo"""
        from src.config import import_bbpp_set
        from tkinter import filedialog
        from pathlib import Path
        
        # Pedir archivo a importar
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo JSON a importar",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        # Confirmar importación
        response = messagebox.askyesno(
            "Confirmar Importación",
            f"¿Importar el conjunto desde:\n{Path(filename).name}?\n\n"
            "Si ya existe un archivo con el mismo nombre, se creará un backup automático."
        )
        
        if not response:
            return
        
        # Importar
        if import_bbpp_set(Path(filename)):
            messagebox.showinfo(
                "Importación Exitosa",
                f"✅ Conjunto importado correctamente.\n\n"
                "El nuevo conjunto ya está disponible en config/bbpp/\n"
                "Recarga esta pantalla para verlo en la lista."
            )
            # Recargar pantalla
            self._show_bbpp_management_screen()
        else:
            messagebox.showerror(
                "Error",
                "❌ No se pudo importar el conjunto.\n\n"
                "Verifica que el archivo JSON tenga el formato correcto."
            )
    
    def _export_all_configuration(self):
        """Exportar configuración completa (todos los conjuntos activos)"""
        from src.config import export_all_active_bbpp
        from tkinter import filedialog
        from pathlib import Path
        from datetime import datetime
        
        # Nombre por defecto con timestamp
        default_name = f"BBPP_Config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Pedir ubicación de guardado
        filename = filedialog.asksaveasfilename(
            title="Guardar configuración completa como",
            defaultextension=".json",
            initialfile=default_name,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        # Exportar
        if export_all_active_bbpp(Path(filename)):
            messagebox.showinfo(
                "Exportación Exitosa",
                f"✅ Configuración completa exportada a:\n{Path(filename).name}\n\n"
                "Incluye todos los conjuntos activos y sus reglas."
            )
        else:
            messagebox.showerror(
                "Error",
                "❌ No se pudo exportar la configuración.\n\n"
                "Verifica que haya al menos un conjunto activo."
            )
    
    def run(self):
        """Ejecutar la aplicación"""
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()
