"""
Pantalla de Notas de Versión
Muestra el CHANGELOG.md en la interfaz de usuario
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path
import re


class ReleaseNotesScreen(tk.Frame):
    """Pantalla para mostrar notas de versión desde CHANGELOG.md"""
    
    def __init__(self, parent, on_back=None):
        """
        Inicializar pantalla de notas de versión
        
        Args:
            parent: Widget padre
            on_back: Callback para volver atrás
        """
        super().__init__(parent)
        self.parent = parent
        self.on_back = on_back
        
        # Colores corporativos NTT Data
        self.NTT_BLUE = "#0067B1"
        self.NTT_LIGHT_BLUE = "#00A3E0"
        self.BG_COLOR = "#FFFFFF"
        self.TEXT_COLOR = "#58595B"
        
        self._create_widgets()
        self._load_changelog()
    
    def _create_widgets(self):
        """Crear widgets de la interfaz"""
        self.configure(bg=self.BG_COLOR)
        
        # Header
        header_frame = tk.Frame(self, bg=self.NTT_BLUE, height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Título
        title_label = tk.Label(
            header_frame,
            text="📋 Notas de Versión",
            font=("Segoe UI", 18, "bold"),
            bg=self.NTT_BLUE,
            fg="white"
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Botón volver
        if self.on_back:
            back_btn = tk.Button(
                header_frame,
                text="← Volver",
                font=("Segoe UI", 10),
                bg="white",
                fg=self.NTT_BLUE,
                relief=tk.FLAT,
                padx=15,
                pady=5,
                cursor="hand2",
                command=self.on_back
            )
            back_btn.pack(side=tk.RIGHT, padx=20, pady=20)
        
        # Contenedor principal
        main_frame = tk.Frame(self, bg=self.BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Área de texto con scroll
        self.text_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="white",
            fg=self.TEXT_COLOR,
            relief=tk.SOLID,
            borderwidth=1,
            padx=15,
            pady=15
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags para formato
        self._configure_text_tags()
    
    def _configure_text_tags(self):
        """Configurar tags para formateo de texto"""
        # Encabezados de versión (## [X.Y.Z])
        self.text_area.tag_configure(
            "version_header",
            font=("Segoe UI", 14, "bold"),
            foreground=self.NTT_BLUE,
            spacing1=10,
            spacing3=5
        )
        
        # Metadata (Autor, Tipo de cambio)
        self.text_area.tag_configure(
            "metadata",
            font=("Segoe UI", 9),
            foreground="#666666",
            spacing3=5
        )
        
        # Secciones (### Added, ### Changed, etc.)
        self.text_area.tag_configure(
            "section_header",
            font=("Segoe UI", 11, "bold"),
            foreground=self.NTT_LIGHT_BLUE,
            spacing1=8,
            spacing3=3
        )
        
        # Items de lista
        self.text_area.tag_configure(
            "list_item",
            font=("Segoe UI", 10),
            foreground=self.TEXT_COLOR,
            lmargin1=20,
            lmargin2=35
        )
        
        # Texto normal
        self.text_area.tag_configure(
            "normal",
            font=("Segoe UI", 10),
            foreground=self.TEXT_COLOR
        )
    
    def _load_changelog(self):
        """Cargar y mostrar contenido del CHANGELOG.md"""
        changelog_path = Path(__file__).parent.parent.parent / 'CHANGELOG.md'
        
        if not changelog_path.exists():
            self._show_no_changelog()
            return
        
        try:
            with open(changelog_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self._parse_and_display_changelog(content)
        except Exception as e:
            self._show_error(str(e))
    
    def _sanitize_content(self, content: str) -> str:
        """
        Limpiar contenido de escapes literales y otros problemas
        
        Args:
            content: Contenido crudo del CHANGELOG.md
            
        Returns:
            Contenido sanitizado
        """
        # Reemplazar \n literales con saltos de línea reales
        content = content.replace('\\n', '\n')
        
        # Reemplazar \t literales con tabs reales
        content = content.replace('\\t', '\t')
        
        # Limpiar múltiples saltos de línea consecutivos (más de 2)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content
    
    def _parse_and_display_changelog(self, content: str):
        """
        Parsear y mostrar changelog con formato
        
        Args:
            content: Contenido del CHANGELOG.md
        """
        self.text_area.delete('1.0', tk.END)
        
        # Sanitizar contenido (limpiar \n literales y otros escapes)
        content = self._sanitize_content(content)
        
        lines = content.split('\n')
        
        for line in lines:
            # Saltar header del changelog
            if line.startswith('# Changelog') or line.startswith('Todos los cambios'):
                continue
            if 'Keep a Changelog' in line or 'Versionado Semántico' in line:
                continue
            
            # Encabezado de versión (## [X.Y.Z] - YYYY-MM-DD)
            if re.match(r'^## \[\d+\.\d+\.\d+\]', line):
                self.text_area.insert(tk.END, line + '\n', 'version_header')
            
            # Metadata (Autor, Tipo de cambio)
            elif line.startswith('**Autor:**') or line.startswith('**Tipo de cambio:**'):
                self.text_area.insert(tk.END, line + '\n', 'metadata')
            
            # Secciones (### Added, ### Changed, etc.)
            elif line.startswith('###'):
                self.text_area.insert(tk.END, '\n' + line + '\n', 'section_header')
            
            # Items de lista
            elif line.strip().startswith('-'):
                self.text_area.insert(tk.END, line + '\n', 'list_item')
            
            # Líneas vacías
            elif line.strip() == '':
                self.text_area.insert(tk.END, '\n')
            
            # Texto normal
            else:
                self.text_area.insert(tk.END, line + '\n', 'normal')
        
        # Deshabilitar edición
        self.text_area.configure(state=tk.DISABLED)
    
    def _show_no_changelog(self):
        """Mostrar mensaje cuando no existe CHANGELOG.md"""
        self.text_area.delete('1.0', tk.END)
        self.text_area.insert(
            tk.END,
            "\n\n" + " " * 30 + "📋 No hay notas de versión disponibles\n\n" +
            " " * 25 + "El archivo CHANGELOG.md no existe todavía.\n" +
            " " * 20 + "Se creará automáticamente al compilar el proyecto.",
            'normal'
        )
        self.text_area.configure(state=tk.DISABLED)
    
    def _show_error(self, error_msg: str):
        """Mostrar mensaje de error"""
        self.text_area.delete('1.0', tk.END)
        self.text_area.insert(
            tk.END,
            f"\n\n" + " " * 30 + "❌ Error al cargar notas de versión\n\n" +
            f" " * 25 + f"Error: {error_msg}",
            'normal'
        )
        self.text_area.configure(state=tk.DISABLED)
    
    def refresh(self):
        """Recargar el changelog"""
        self.text_area.configure(state=tk.NORMAL)
        self._load_changelog()


# Función helper para abrir la pantalla desde el menú principal
def show_release_notes(parent, on_back=None):
    """
    Mostrar pantalla de notas de versión
    
    Args:
        parent: Widget padre
        on_back: Callback para volver atrás
        
    Returns:
        Instancia de ReleaseNotesScreen
    """
    screen = ReleaseNotesScreen(parent, on_back)
    return screen
