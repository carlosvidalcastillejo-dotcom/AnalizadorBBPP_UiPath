"""
Dashboard de Métricas
Pantalla para visualizar historial y estadísticas de análisis
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime
import sys

# Añadir path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database.metrics_db import get_metrics_db
from src.metrics.metrics_calculator import create_metrics_calculator


class MetricsDashboard(tk.Frame):
    """Dashboard de métricas y análisis histórico"""
    
    def __init__(self, parent, project_path=None):
        """
        Inicializar dashboard
        
        Args:
            parent: Widget padre
            project_path: Ruta del proyecto actual
        """
        super().__init__(parent)
        self.parent = parent
        self.project_path = project_path
        
        # Colores NTT Data
        self.NTT_BLUE = "#0067B1"
        self.NTT_LIGHT_BLUE = "#00A3E0"
        self.BG_COLOR = "#FFFFFF"
        self.TEXT_COLOR = "#58595B"
        
        # Base de datos
        self.db = None
        self.calculator = None
        
        self._init_database()
        self._create_widgets()
        self._load_data()
    
    def _init_database(self):
        """Inicializar conexión a base de datos"""
        try:
            self.db = get_metrics_db()
            self.calculator = create_metrics_calculator(self.db)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar a la base de datos:\n{e}")
    
    def _create_widgets(self):
        """Crear widgets de la interfaz"""
        self.configure(bg=self.BG_COLOR)
        
        # Header
        header_frame = tk.Frame(self, bg=self.NTT_BLUE, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="📊 Dashboard de Métricas",
            font=("Segoe UI", 18, "bold"),
            bg=self.NTT_BLUE,
            fg="white"
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Contenedor principal
        main_container = tk.Frame(self, bg=self.BG_COLOR)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Panel de estadísticas
        stats_frame = tk.LabelFrame(
            main_container,
            text="📈 Estadísticas Generales",
            font=("Segoe UI", 12, "bold"),
            bg=self.BG_COLOR,
            fg=self.NTT_BLUE
        )
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Grid de estadísticas
        stats_grid = tk.Frame(stats_frame, bg=self.BG_COLOR)
        stats_grid.pack(fill=tk.X, padx=15, pady=15)
        
        self.stats_labels = {}
        stats_items = [
            ("total_analyses", "Total Análisis", "0"),
            ("avg_score", "Score Promedio", "0.0"),
            ("last_score", "Último Score", "0.0"),
            ("trend", "Tendencia", "---")
        ]
        
        for i, (key, label, default) in enumerate(stats_items):
            frame = tk.Frame(stats_grid, bg=self.BG_COLOR)
            frame.grid(row=0, column=i, padx=15, pady=5, sticky="ew")
            
            tk.Label(
                frame,
                text=label,
                font=("Segoe UI", 9),
                bg=self.BG_COLOR,
                fg=self.TEXT_COLOR
            ).pack()
            
            value_label = tk.Label(
                frame,
                text=default,
                font=("Segoe UI", 16, "bold"),
                bg=self.BG_COLOR,
                fg=self.NTT_BLUE
            )
            value_label.pack()
            
            self.stats_labels[key] = value_label
        
        # Filtro de proyectos
        filter_frame = tk.LabelFrame(
            main_container,
            text="🔍 Filtrar por Proyecto",
            font=("Segoe UI", 11, "bold"),
            bg=self.BG_COLOR,
            fg=self.NTT_BLUE
        )
        filter_frame.pack(fill=tk.X, pady=(0, 20))
        
        filter_inner = tk.Frame(filter_frame, bg=self.BG_COLOR)
        filter_inner.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(
            filter_inner,
            text="Proyecto:",
            font=("Segoe UI", 10),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.project_filter = ttk.Combobox(
            filter_inner,
            state="readonly",
            font=("Segoe UI", 10),
            width=30
        )
        self.project_filter.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.project_filter.bind("<<ComboboxSelected>>", self._on_filter_change)
        
        # Frame para la tabla
        table_frame = tk.Frame(main_container, bg=self.BG_COLOR)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("Fecha", "Proyecto", "Versión", "Score", "Errors", "Warnings", "Info")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=10
        )
        scrollbar.config(command=self.tree.yview)
        
        # Configurar columnas
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Proyecto", text="Proyecto")
        self.tree.heading("Versión", text="Versión")
        self.tree.heading("Score", text="Score")
        self.tree.heading("Errors", text="Errors")
        self.tree.heading("Warnings", text="Warnings")
        self.tree.heading("Info", text="Info")
        
        self.tree.column("Fecha", width=130)
        self.tree.column("Proyecto", width=150)
        self.tree.column("Versión", width=80)
        self.tree.column("Score", width=70)
        self.tree.column("Errors", width=70)
        self.tree.column("Warnings", width=80)
        self.tree.column("Info", width=70)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Botones
        buttons_frame = tk.Frame(main_container, bg=self.BG_COLOR)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Button(
            buttons_frame,
            text="🔄 Actualizar",
            command=self._load_data,
            bg=self.NTT_BLUE,
            fg="white",
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            buttons_frame,
            text="📊 Ver Detalles",
            command=self._show_details,
            bg=self.NTT_LIGHT_BLUE,
            fg="white",
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            buttons_frame,
            text="📄 Abrir HTML",
            command=self._open_html_report,
            bg="#FF6B6B",
            fg="white",
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            buttons_frame,
            text="📊 Abrir Excel",
            command=self._open_excel_report,
            bg="#217346",
            fg="white",
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            buttons_frame,
            text="📁 Carpeta Output",
            command=self._open_output_folder,
            bg="#9B59B6",
            fg="white",
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2"
        ).pack(side=tk.LEFT)
    
    def _load_data(self):
        """Cargar datos del historial"""
        if not self.db:
            return
        
        try:
            # Cargar proyectos únicos para el filtro
            unique_projects = self.db.get_unique_projects()
            self.project_filter['values'] = ["Todos"] + unique_projects
            
            # Seleccionar valor actual si no hay selección
            if not self.project_filter.get():
                if self.project_path:
                    current_project = Path(self.project_path).name
                    if current_project in unique_projects:
                        self.project_filter.set(current_project)
                    else:
                        self.project_filter.set("Todos")
                else:
                    self.project_filter.set("Todos")

            # Obtener selección actual
            selected_project = self.project_filter.get()
            if selected_project == "Todos":
                selected_project = None
            
            # Obtener historial
            history = self.db.get_analysis_history(selected_project, limit=50)
            
            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Llenar tabla
            for analysis in history:
                # Convertir timestamp UTC a hora local
                try:
                    from datetime import datetime, timezone
                    # SQLite guarda en UTC sin timezone info, así que lo parseamos como UTC
                    utc_time = datetime.strptime(analysis['analysis_date'], "%Y-%m-%d %H:%M:%S")
                    # Marcar como UTC
                    utc_time = utc_time.replace(tzinfo=timezone.utc)
                    # Convertir a hora local
                    local_time = utc_time.astimezone()
                    date_str = local_time.strftime("%Y-%m-%d %H:%M")
                except Exception as e:
                    # Fallback si hay error en conversión
                    date_str = analysis['analysis_date'][:16]  # YYYY-MM-DD HH:MM
                
                project = analysis.get('project_name', 'N/A')
                version = analysis.get('version', 'N/A')
                score = f"{analysis['score']:.1f}"
                # Mapeo: HIGH=Errors, MEDIUM=Warnings, LOW=Info
                errors = str(analysis.get('high_findings', 0))
                warnings = str(analysis.get('medium_findings', 0))
                info = str(analysis.get('low_findings', 0))
                
                self.tree.insert('', 'end', 
                               values=(date_str, project, version, score, errors, warnings, info),
                               tags=(str(analysis['id']),))
            
            # Actualizar estadísticas
            # Actualizar estadísticas
            if history:
                self._update_stats(history, selected_project)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos:\n{e}")

    def _on_filter_change(self, event):
        """Manejar cambio de filtro"""
        self._load_data()
    
    def _update_stats(self, history, project_name):
        """Actualizar panel de estadísticas"""
        if not history:
            return
        
        # Total de análisis
        self.stats_labels['total_analyses'].config(text=str(len(history)))
        
        # Score promedio
        avg_score = sum(a['score'] for a in history) / len(history)
        self.stats_labels['avg_score'].config(text=f"{avg_score:.1f}")
        
        # Último score
        last_score = history[0]['score']
        self.stats_labels['last_score'].config(text=f"{last_score:.1f}")
        
        # Tendencia
        if project_name and self.calculator:
            trend_data = self.calculator.calculate_trend(project_name, limit=10)
            trend_text = {
                'improving': '↑ Mejorando',
                'declining': '↓ Declinando',
                'stable': '→ Estable',
                'insufficient_data': '---'
            }.get(trend_data['trend'], '---')
            
            trend_color = {
                'improving': '#28A745',
                'declining': '#DC3545',
                'stable': '#FFC107',
                'insufficient_data': self.TEXT_COLOR
            }.get(trend_data['trend'], self.TEXT_COLOR)
            
            self.stats_labels['trend'].config(text=trend_text, fg=trend_color)
    
    def _show_details(self):
        """Mostrar detalles del análisis seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Por favor, selecciona un análisis")
            return
        
        # Obtener ID del análisis
        item = self.tree.item(selection[0])
        analysis_id = int(item['tags'][0])
        
        # Obtener detalles
        analysis = self.db.get_analysis_by_id(analysis_id)
        
        if not analysis:
            messagebox.showerror("Error", "No se pudo cargar el análisis")
            return
        
        # Mostrar ventana de detalles
        self._show_details_window(analysis)
    
    def _show_details_window(self, analysis):
        """Mostrar ventana con detalles del análisis"""
        details_window = tk.Toplevel(self.parent)
        details_window.title(f"Detalles - Análisis #{analysis['id']}")
        details_window.geometry("600x500")
        
        # Texto con detalles
        text = tk.Text(details_window, wrap=tk.WORD, padx=15, pady=15)
        text.pack(fill=tk.BOTH, expand=True)
        
        # Formatear información
        info = f"""
ANÁLISIS #{analysis['id']}
{'=' * 50}

Proyecto: {analysis['project_name']}
Fecha: {analysis['analysis_date']}
Versión: {analysis.get('version', 'N/A')}

RESULTADOS
{'=' * 50}

Score: {analysis['score']:.1f}/100
Total de Hallazgos: {analysis['total_findings']}

Por Severidad:
  • Errors (HIGH): {analysis['high_findings']}
  • Warnings (MEDIUM): {analysis['medium_findings']}
  • Info (LOW): {analysis['low_findings']}

Archivos Analizados: {analysis['analyzed_files']} de {analysis['total_files']}
Tiempo de Ejecución: {analysis['execution_time']:.2f}s

TODOS LOS HALLAZGOS
{'=' * 50}
"""
        
        text.insert('1.0', info)
        
        # Añadir TODOS los hallazgos (sin límite)
        for i, finding in enumerate(analysis.get('findings', []), 1):
            finding_text = f"\n{i}. [{finding.get('severity', 'N/A')}] {finding.get('rule_name', 'N/A')}\n"
            finding_text += f"   Archivo: {finding.get('file_path', 'N/A')}\n"
            finding_text += f"   {finding.get('description', 'N/A')}\n"
            text.insert(tk.END, finding_text)
        
        text.config(state=tk.DISABLED)
    
    def _open_html_report(self):
        """Abrir reporte HTML del análisis seleccionado"""
        from tkinter import messagebox
        from src.report_utils import get_report_path_from_db, open_file_or_folder
        
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Por favor, selecciona un análisis")
            return
        
        # Obtener ID del análisis
        item = self.tree.item(selection[0])
        analysis_id = int(item['tags'][0])
        
        # Obtener ruta del reporte HTML
        html_path = get_report_path_from_db(analysis_id, 'html')
        
        if html_path and html_path.exists():
            if open_file_or_folder(html_path):
                print(f"✅ Abriendo reporte HTML: {html_path}")
            else:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{html_path}")
        else:
            messagebox.showwarning(
                "Reporte no encontrado",
                "No se encontró el reporte HTML para este análisis.\n\n"
                "Asegúrate de tener activada la opción 'Generar reportes automáticamente' "
                "en Configuración."
            )
    
    def _open_excel_report(self):
        """Abrir reporte Excel del análisis seleccionado"""
        from tkinter import messagebox
        from src.report_utils import get_report_path_from_db, open_file_or_folder
        
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Por favor, selecciona un análisis")
            return
        
        # Obtener ID del análisis
        item = self.tree.item(selection[0])
        analysis_id = int(item['tags'][0])
        
        # Obtener ruta del reporte Excel
        excel_path = get_report_path_from_db(analysis_id, 'excel')
        
        if excel_path and excel_path.exists():
            if open_file_or_folder(excel_path):
                print(f"✅ Abriendo reporte Excel: {excel_path}")
            else:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{excel_path}")
        else:
            messagebox.showwarning(
                "Reporte no encontrado",
                "No se encontró el reporte Excel para este análisis.\n\n"
                "Asegúrate de tener activada la opción 'Generar reportes automáticamente' "
                "en Configuración."
            )
    
    def _open_output_folder(self):
        """Abrir carpeta output donde se guardan todos los reportes"""
        from tkinter import messagebox
        from src.report_utils import open_file_or_folder
        from src.config import OUTPUT_DIR
        
        if OUTPUT_DIR.exists():
            if open_file_or_folder(OUTPUT_DIR):
                print(f"✅ Abriendo carpeta output: {OUTPUT_DIR}")
            else:
                messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{OUTPUT_DIR}")
        else:
            messagebox.showwarning(
                "Carpeta no encontrada",
                f"La carpeta output no existe aún:\n{OUTPUT_DIR}\n\n"
                "Se creará automáticamente al generar el primer reporte."
            )
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.db:
            self.db.close()


def show_metrics_dashboard(parent, project_path=None):
    """
    Mostrar dashboard de métricas
    
    Args:
        parent: Widget padre
        project_path: Ruta del proyecto
        
    Returns:
        Instancia de MetricsDashboard
    """
    dashboard = MetricsDashboard(parent, project_path)
    return dashboard
