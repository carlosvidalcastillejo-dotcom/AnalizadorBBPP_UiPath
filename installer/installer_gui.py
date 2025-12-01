"""
Interfaz gráfica del instalador - Diseño moderno y atractivo
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import sys
import threading
from pathlib import Path
from typing import Optional
from git_downloader import GitDownloader


class ModernButton(tk.Canvas):
    """Botón moderno con efectos hover"""
    
    def __init__(self, parent, text, command, bg_color="#4A90E2", fg_color="white", 
                 hover_color="#357ABD", width=200, height=45):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=parent['bg'])
        
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.width = width
        self.height = height
        self.is_hovered = False
        
        self._draw()
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)
    
    def _draw(self):
        """Dibuja el botón"""
        self.delete('all')
        
        color = self.hover_color if self.is_hovered else self.bg_color
        
        # Rectángulo con bordes redondeados
        self.create_rounded_rectangle(
            2, 2, self.width-2, self.height-2,
            radius=10, fill=color, outline=""
        )
        
        # Texto
        self.create_text(
            self.width/2, self.height/2,
            text=self.text, fill=self.fg_color,
            font=('Segoe UI', 11, 'bold')
        )
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        """Crea un rectángulo con bordes redondeados"""
        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_enter(self, event):
        """Mouse entra al botón"""
        self.is_hovered = True
        self._draw()
        self.config(cursor='hand2')
    
    def _on_leave(self, event):
        """Mouse sale del botón"""
        self.is_hovered = False
        self._draw()
        self.config(cursor='')
    
    def _on_click(self, event):
        """Click en el botón"""
        if self.command:
            self.command()


class InstallerGUI:
    """Interfaz gráfica del instalador"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Instalador - Analizador BBPP UiPath")
        self.root.geometry("700x650")
        self.root.resizable(False, False)
        
        # Colores del tema
        self.colors = {
            'bg': '#F5F7FA',
            'primary': '#4A90E2',
            'secondary': '#5C6BC0',
            'success': '#66BB6A',
            'text_dark': '#2C3E50',
            'text_light': '#7F8C8D',
            'card_bg': 'white',
            'border': '#E0E0E0'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Cargar configuración
        self.load_config()
        
        # Variables
        self.install_path = tk.StringVar(value=self.config['installation']['default_path'])
        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        self.create_start_menu_shortcut = tk.BooleanVar(value=True)
        self.launch_after_install = tk.BooleanVar(value=True)
        self.auto_update = tk.BooleanVar(value=True)
        
        self.current_page = 0
        self.pages = []
        
        # Crear interfaz
        self.create_ui()
        
        # Centrar ventana
        self.center_window()
    
    def load_config(self):
        """Carga la configuración del instalador"""
        config_path = Path(__file__).parent / 'config_installer.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_ui(self):
        """Crea la interfaz de usuario"""
        # Contenedor principal
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Crear páginas
        self.create_welcome_page(main_container)
        self.create_options_page(main_container)
        self.create_installation_page(main_container)
        self.create_finish_page(main_container)
        
        # Mostrar primera página
        self.show_page(0)
    
    def create_welcome_page(self, parent):
        """Crea la página de bienvenida"""
        page = tk.Frame(parent, bg=self.colors['bg'])
        self.pages.append(page)
        
        # Header con gradiente simulado
        header = tk.Frame(page, bg=self.colors['primary'], height=120)
        header.pack(fill=tk.X, pady=(0, 20))
        header.pack_propagate(False)
        
        # Título principal
        title = tk.Label(
            header,
            text="🚀 Bienvenido al Instalador",
            font=('Segoe UI', 24, 'bold'),
            bg=self.colors['primary'],
            fg='white'
        )
        title.pack(pady=(20, 5))
        
        subtitle = tk.Label(
            header,
            text=self.config['app_info']['name'],
            font=('Segoe UI', 14),
            bg=self.colors['primary'],
            fg='white'
        )
        subtitle.pack()
        
        # Card de contenido
        content_card = tk.Frame(page, bg=self.colors['card_bg'], relief=tk.FLAT)
        content_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Descripción
        desc_frame = tk.Frame(content_card, bg=self.colors['card_bg'])
        desc_frame.pack(pady=20, padx=30)
        
        desc = tk.Label(
            desc_frame,
            text=self.config['app_info']['description'],
            font=('Segoe UI', 11),
            bg=self.colors['card_bg'],
            fg=self.colors['text_dark'],
            wraplength=600,
            justify=tk.CENTER
        )
        desc.pack()
        
        # Separador
        separator = tk.Frame(content_card, bg=self.colors['border'], height=1)
        separator.pack(fill=tk.X, padx=30, pady=15)
        
        # Características
        features_label = tk.Label(
            content_card,
            text="✨ Características Principales",
            font=('Segoe UI', 13, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_dark']
        )
        features_label.pack(pady=(10, 15))
        
        # Grid de características
        features_frame = tk.Frame(content_card, bg=self.colors['card_bg'])
        features_frame.pack(padx=30, pady=10)
        
        # Mostrar características en 2 columnas
        features = self.config['features']
        for i, feature in enumerate(features):
            row = i // 2
            col = i % 2
            
            feature_item = self.create_feature_item(
                features_frame,
                feature['icon'],
                feature['title'],
                feature['description']
            )
            feature_item.grid(row=row, column=col, padx=10, pady=8, sticky='w')
        
        # Botones
        button_frame = tk.Frame(page, bg=self.colors['bg'])
        button_frame.pack(side=tk.BOTTOM, pady=20)
        
        next_btn = ModernButton(
            button_frame,
            "Siguiente →",
            lambda: self.show_page(1),
            bg_color=self.colors['primary'],
            hover_color=self.colors['secondary']
        )
        next_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = ModernButton(
            button_frame,
            "Cancelar",
            self.cancel_installation,
            bg_color=self.colors['text_light'],
            hover_color='#5D6D7E',
            width=120
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_feature_item(self, parent, icon, title, description):
        """Crea un item de característica"""
        frame = tk.Frame(parent, bg=self.colors['card_bg'])
        
        # Icon y título en la misma línea
        header = tk.Frame(frame, bg=self.colors['card_bg'])
        header.pack(anchor='w')
        
        icon_label = tk.Label(
            header,
            text=icon,
            font=('Segoe UI', 14),
            bg=self.colors['card_bg']
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 8))
        
        title_label = tk.Label(
            header,
            text=title,
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_dark']
        )
        title_label.pack(side=tk.LEFT)
        
        # Descripción
        desc_label = tk.Label(
            frame,
            text=description,
            font=('Segoe UI', 9),
            bg=self.colors['card_bg'],
            fg=self.colors['text_light'],
            wraplength=280,
            justify=tk.LEFT
        )
        desc_label.pack(anchor='w', padx=(30, 0))
        
        return frame
    
    def create_options_page(self, parent):
        """Crea la página de opciones"""
        page = tk.Frame(parent, bg=self.colors['bg'])
        self.pages.append(page)
        
        # Header
        header = tk.Frame(page, bg=self.colors['primary'], height=80)
        header.pack(fill=tk.X, pady=(0, 20))
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="⚙️ Opciones de Instalación",
            font=('Segoe UI', 20, 'bold'),
            bg=self.colors['primary'],
            fg='white'
        )
        title.pack(pady=20)
        
        # Card de opciones
        options_card = tk.Frame(page, bg=self.colors['card_bg'])
        options_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Ruta de instalación
        path_frame = tk.Frame(options_card, bg=self.colors['card_bg'])
        path_frame.pack(fill=tk.X, padx=30, pady=20)
        
        path_label = tk.Label(
            path_frame,
            text="📁 Ubicación de instalación:",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_dark']
        )
        path_label.pack(anchor='w', pady=(0, 10))
        
        path_entry_frame = tk.Frame(path_frame, bg=self.colors['card_bg'])
        path_entry_frame.pack(fill=tk.X)
        
        path_entry = tk.Entry(
            path_entry_frame,
            textvariable=self.install_path,
            font=('Segoe UI', 10),
            relief=tk.FLAT,
            bg='#F8F9FA',
            fg=self.colors['text_dark']
        )
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))
        
        browse_btn = ModernButton(
            path_entry_frame,
            "Examinar",
            self.browse_install_path,
            width=100,
            height=35
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # Separador
        separator = tk.Frame(options_card, bg=self.colors['border'], height=1)
        separator.pack(fill=tk.X, padx=30, pady=20)
        
        # Opciones adicionales
        options_label = tk.Label(
            options_card,
            text="🎯 Opciones adicionales:",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_dark']
        )
        options_label.pack(anchor='w', padx=30, pady=(0, 15))
        
        # Checkboxes con estilo
        checkbox_frame = tk.Frame(options_card, bg=self.colors['card_bg'])
        checkbox_frame.pack(fill=tk.X, padx=50)
        
        self.create_styled_checkbox(
            checkbox_frame,
            "🖥️ Crear acceso directo en el escritorio",
            self.create_desktop_shortcut
        ).pack(anchor='w', pady=8)
        
        self.create_styled_checkbox(
            checkbox_frame,
            "📌 Crear acceso directo en el menú Inicio",
            self.create_start_menu_shortcut
        ).pack(anchor='w', pady=8)
        
        self.create_styled_checkbox(
            checkbox_frame,
            "🚀 Iniciar aplicación al completar instalación",
            self.launch_after_install
        ).pack(anchor='w', pady=8)
        
        self.create_styled_checkbox(
            checkbox_frame,
            "🔄 Habilitar actualizaciones automáticas",
            self.auto_update
        ).pack(anchor='w', pady=8)
        
        # Botones
        button_frame = tk.Frame(page, bg=self.colors['bg'])
        button_frame.pack(side=tk.BOTTOM, pady=20)
        
        install_btn = ModernButton(
            button_frame,
            "Instalar",
            self.start_installation,
            bg_color=self.colors['success'],
            hover_color='#4CAF50',
            width=150
        )
        install_btn.pack(side=tk.RIGHT, padx=5)
        
        back_btn = ModernButton(
            button_frame,
            "← Atrás",
            lambda: self.show_page(0),
            bg_color=self.colors['text_light'],
            hover_color='#5D6D7E',
            width=120
        )
        back_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_styled_checkbox(self, parent, text, variable):
        """Crea un checkbox con estilo"""
        cb = tk.Checkbutton(
            parent,
            text=text,
            variable=variable,
            font=('Segoe UI', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text_dark'],
            activebackground=self.colors['card_bg'],
            selectcolor='white',
            relief=tk.FLAT,
            cursor='hand2'
        )
        return cb
    
    def create_installation_page(self, parent):
        """Crea la página de instalación"""
        page = tk.Frame(parent, bg=self.colors['bg'])
        self.pages.append(page)
        
        # Header
        header = tk.Frame(page, bg=self.colors['secondary'], height=80)
        header.pack(fill=tk.X, pady=(0, 20))
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="⏳ Instalando...",
            font=('Segoe UI', 20, 'bold'),
            bg=self.colors['secondary'],
            fg='white'
        )
        title.pack(pady=20)
        
        # Card de progreso
        progress_card = tk.Frame(page, bg=self.colors['card_bg'])
        progress_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Mensaje de estado
        self.status_label = tk.Label(
            progress_card,
            text="Preparando instalación...",
            font=('Segoe UI', 12),
            bg=self.colors['card_bg'],
            fg=self.colors['text_dark']
        )
        self.status_label.pack(pady=(40, 20))
        
        # Barra de progreso
        progress_frame = tk.Frame(progress_card, bg=self.colors['card_bg'])
        progress_frame.pack(pady=20, padx=50, fill=tk.X)
        
        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=500,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X)
        
        # Porcentaje
        self.percentage_label = tk.Label(
            progress_card,
            text="0%",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['primary']
        )
        self.percentage_label.pack(pady=10)
        
        # Log de instalación
        log_frame = tk.Frame(progress_card, bg=self.colors['card_bg'])
        log_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        log_label = tk.Label(
            log_frame,
            text="📋 Detalles:",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_dark']
        )
        log_label.pack(anchor='w', pady=(0, 5))
        
        self.log_text = tk.Text(
            log_frame,
            height=8,
            font=('Consolas', 9),
            bg='#F8F9FA',
            fg=self.colors['text_dark'],
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
    
    def create_finish_page(self, parent):
        """Crea la página de finalización"""
        page = tk.Frame(parent, bg=self.colors['bg'])
        self.pages.append(page)
        
        # Header
        header = tk.Frame(page, bg=self.colors['success'], height=120)
        header.pack(fill=tk.X, pady=(0, 20))
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="✅ ¡Instalación Completada!",
            font=('Segoe UI', 24, 'bold'),
            bg=self.colors['success'],
            fg='white'
        )
        title.pack(pady=(30, 5))
        
        subtitle = tk.Label(
            header,
            text="El Analizador BBPP UiPath está listo para usar",
            font=('Segoe UI', 12),
            bg=self.colors['success'],
            fg='white'
        )
        subtitle.pack()
        
        # Card de finalización
        finish_card = tk.Frame(page, bg=self.colors['card_bg'])
        finish_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Mensaje
        message = tk.Label(
            finish_card,
            text="La aplicación se ha instalado correctamente en:\n",
            font=('Segoe UI', 11),
            bg=self.colors['card_bg'],
            fg=self.colors['text_dark']
        )
        message.pack(pady=(30, 5))
        
        path_label = tk.Label(
            finish_card,
            text=self.install_path.get(),
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['primary']
        )
        path_label.pack(pady=(0, 30))
        
        # Información adicional
        info_frame = tk.Frame(finish_card, bg=self.colors['card_bg'])
        info_frame.pack(pady=20)
        
        if self.create_desktop_shortcut.get():
            tk.Label(
                info_frame,
                text="✓ Acceso directo creado en el escritorio",
                font=('Segoe UI', 10),
                bg=self.colors['card_bg'],
                fg=self.colors['text_dark']
            ).pack(anchor='w', pady=3)
        
        if self.auto_update.get():
            tk.Label(
                info_frame,
                text="✓ Actualizaciones automáticas habilitadas",
                font=('Segoe UI', 10),
                bg=self.colors['card_bg'],
                fg=self.colors['text_dark']
            ).pack(anchor='w', pady=3)
        
        # Botones
        button_frame = tk.Frame(page, bg=self.colors['bg'])
        button_frame.pack(side=tk.BOTTOM, pady=20)
        
        finish_btn = ModernButton(
            button_frame,
            "Finalizar",
            self.finish_installation,
            bg_color=self.colors['success'],
            hover_color='#4CAF50'
        )
        finish_btn.pack(side=tk.RIGHT, padx=5)
        
        if self.launch_after_install.get():
            launch_btn = ModernButton(
                button_frame,
                "🚀 Iniciar Aplicación",
                self.launch_application,
                bg_color=self.colors['primary'],
                hover_color=self.colors['secondary']
            )
            launch_btn.pack(side=tk.RIGHT, padx=5)
    
    def show_page(self, page_index):
        """Muestra una página específica"""
        # Ocultar todas las páginas
        for page in self.pages:
            page.pack_forget()
        
        # Mostrar página seleccionada
        if 0 <= page_index < len(self.pages):
            self.pages[page_index].pack(fill=tk.BOTH, expand=True)
            self.current_page = page_index
    
    def browse_install_path(self):
        """Abre diálogo para seleccionar ruta de instalación"""
        path = filedialog.askdirectory(
            title="Seleccionar ubicación de instalación",
            initialdir=self.install_path.get()
        )
        if path:
            self.install_path.set(path)
    
    def log_message(self, message: str):
        """Añade un mensaje al log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def update_progress(self, message: str, percentage: int):
        """Actualiza el progreso de la instalación"""
        self.status_label.config(text=message)
        self.progress_var.set(percentage)
        self.percentage_label.config(text=f"{percentage}%")
        self.log_message(f"[{percentage}%] {message}")
        self.root.update()
    
    def start_installation(self):
        """Inicia el proceso de instalación"""
        self.show_page(2)
        
        # Ejecutar instalación en thread separado
        thread = threading.Thread(target=self.run_installation, daemon=True)
        thread.start()
    
    def run_installation(self):
        """Ejecuta el proceso de instalación"""
        try:
            install_path = self.install_path.get()
            
            # Crear downloader
            downloader = GitDownloader(self.config, self.update_progress)
            
            # Descargar repositorio
            if not downloader.download(install_path):
                messagebox.showerror(
                    "Error",
                    "No se pudo descargar el repositorio. Verifica tu conexión a internet."
                )
                self.show_page(1)
                return
            
            # Instalar dependencias
            self.update_progress("Instalando dependencias de Python...", 85)
            self.install_dependencies(install_path)
            
            # Crear accesos directos
            if self.create_desktop_shortcut.get():
                self.update_progress("Creando acceso directo en escritorio...", 92)
                self.create_shortcut('desktop', install_path)
            
            if self.create_start_menu_shortcut.get():
                self.update_progress("Creando acceso directo en menú Inicio...", 95)
                self.create_shortcut('start_menu', install_path)
            
            # Guardar configuración
            self.update_progress("Guardando configuración...", 98)
            self.save_installation_config(install_path)
            
            self.update_progress("¡Instalación completada!", 100)
            
            # Mostrar página de finalización
            self.root.after(1000, lambda: self.show_page(3))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la instalación:\n{str(e)}")
            self.show_page(1)
    
    def install_dependencies(self, install_path: str):
        """Instala las dependencias de Python"""
        try:
            requirements_file = os.path.join(install_path, 'requirements.txt')
            if os.path.exists(requirements_file):
                import subprocess
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', '-r', requirements_file],
                    check=True,
                    capture_output=True
                )
        except Exception as e:
            self.log_message(f"Advertencia: No se pudieron instalar todas las dependencias: {e}")
    
    def create_shortcut(self, location: str, install_path: str):
        """Crea un acceso directo"""
        try:
            import win32com.client
            
            shell = win32com.client.Dispatch("WScript.Shell")
            
            if location == 'desktop':
                shortcut_path = os.path.join(
                    shell.SpecialFolders("Desktop"),
                    "Analizador BBPP UiPath.lnk"
                )
            else:  # start_menu
                shortcut_path = os.path.join(
                    shell.SpecialFolders("StartMenu"),
                    "Programs",
                    "Analizador BBPP UiPath.lnk"
                )
            
            shortcut = shell.CreateShortCut(shortcut_path)
            
            # Buscar el ejecutable o el script principal
            exe_path = os.path.join(install_path, 'dist', 'AnalizadorBBPP_UiPath.exe')
            if not os.path.exists(exe_path):
                exe_path = os.path.join(install_path, 'src', 'main.py')
                shortcut.TargetPath = sys.executable
                shortcut.Arguments = f'"{exe_path}"'
            else:
                shortcut.TargetPath = exe_path
            
            shortcut.WorkingDirectory = install_path
            shortcut.IconLocation = exe_path
            shortcut.save()
            
        except Exception as e:
            self.log_message(f"No se pudo crear acceso directo: {e}")
    
    def save_installation_config(self, install_path: str):
        """Guarda la configuración de la instalación"""
        config = {
            'install_path': install_path,
            'version': self.config['app_info']['version'],
            'auto_update': self.auto_update.get(),
            'installed_date': str(Path(__file__).stat().st_mtime)
        }
        
        config_file = os.path.join(install_path, 'installation_config.json')
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    
    def launch_application(self):
        """Inicia la aplicación"""
        try:
            install_path = self.install_path.get()
            exe_path = os.path.join(install_path, 'dist', 'AnalizadorBBPP_UiPath.exe')
            
            if os.path.exists(exe_path):
                os.startfile(exe_path)
            else:
                # Ejecutar con Python
                main_py = os.path.join(install_path, 'src', 'main.py')
                if os.path.exists(main_py):
                    import subprocess
                    subprocess.Popen([sys.executable, main_py], cwd=install_path)
            
            self.finish_installation()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar la aplicación:\n{str(e)}")
    
    def finish_installation(self):
        """Finaliza el instalador"""
        self.root.quit()
        self.root.destroy()
    
    def cancel_installation(self):
        """Cancela la instalación"""
        if messagebox.askyesno("Cancelar", "¿Estás seguro de que deseas cancelar la instalación?"):
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()


if __name__ == "__main__":
    app = InstallerGUI()
    app.run()
