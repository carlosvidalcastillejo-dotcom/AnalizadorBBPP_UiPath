"""
Gestor de Branding Personalizable
Centraliza toda la configuración de marca (logo, colores, textos)
"""

import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class BrandingManager:
    """Gestor centralizado de branding de la aplicación"""
    
    _instance = None
    _config = None
    _config_path = Path(__file__).parent.parent / 'config' / 'branding.json'
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Cargar configuración de branding"""
        try:
            if self._config_path.exists():
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                # Configuración por defecto si no existe el archivo
                self._config = self._get_default_config()
                self._save_config()
        except Exception as e:
            print(f"WARNING: Error cargando branding: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Obtener configuración por defecto"""
        return {
            "company": {
                "name": "Your Company",
                "short_name": "YC",
                "website": "https://yourcompany.com",
                "email": "contact@yourcompany.com"
            },
            "branding": {
                "logo_path": None,
                "logo_width": 150,
                "logo_height": 50,
                "use_logo_in_reports": True,
                "use_logo_in_ui": True,
                "use_logo_in_excel": True
            },
            "colors": {
                "primary": "#0067B1",
                "secondary": "#00A3E0",
                "accent": "#FFC107",
                "success": "#28A745",
                "warning": "#FFC107",
                "error": "#DC3545",
                "info": "#17A2B8",
                "background": "#F5F5F5",
                "text": "#333333"
            },
            "texts": {
                "app_title": "Analizador BBPP UiPath",
                "app_subtitle": "Análisis de Buenas Prácticas",
                "report_footer": "Desarrollado por {author}",
                "sidebar_company": "Your Company",
                "welcome_message": "Bienvenido al Analizador de Buenas Prácticas"
            }
        }
    
    def _save_config(self):
        """Guardar configuración actual"""
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Añadir metadata de actualización
            if 'metadata' not in self._config:
                self._config['metadata'] = {}
            
            self._config['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"ERROR: Error guardando branding: {e}")
            return False
    
    # ========== COMPANY ==========
    
    def get_company_name(self) -> str:
        """Obtener nombre de la empresa"""
        return self._config.get('company', {}).get('name', 'Your Company')
    
    def get_company_short_name(self) -> str:
        """Obtener nombre corto de la empresa"""
        return self._config.get('company', {}).get('short_name', 'YC')
    
    def get_company_website(self) -> str:
        """Obtener sitio web de la empresa"""
        return self._config.get('company', {}).get('website', '')
    
    def get_company_email(self) -> str:
        """Obtener email de la empresa"""
        return self._config.get('company', {}).get('email', '')
    
    def set_company_name(self, name: str) -> bool:
        """Establecer nombre de la empresa"""
        if 'company' not in self._config:
            self._config['company'] = {}
        self._config['company']['name'] = name
        return self._save_config()
    
    def set_company_short_name(self, short_name: str) -> bool:
        """Establecer nombre corto de la empresa"""
        if 'company' not in self._config:
            self._config['company'] = {}
        self._config['company']['short_name'] = short_name
        return self._save_config()
    
    # ========== LOGO ==========
    
    def get_logo_path(self) -> Optional[Path]:
        """Obtener ruta del logo"""
        logo_path = self._config.get('branding', {}).get('logo_path')
        if logo_path and Path(logo_path).exists():
            return Path(logo_path)
        return None
    
    def set_logo_path(self, logo_path: Optional[Path]) -> bool:
        """Establecer ruta del logo"""
        if 'branding' not in self._config:
            self._config['branding'] = {}
        self._config['branding']['logo_path'] = str(logo_path) if logo_path else None
        return self._save_config()
    
    def use_logo_in_reports(self) -> bool:
        """¿Usar logo en reportes HTML?"""
        return self._config.get('branding', {}).get('use_logo_in_reports', True)
    
    def use_logo_in_ui(self) -> bool:
        """¿Usar logo en interfaz?"""
        return self._config.get('branding', {}).get('use_logo_in_ui', True)
    
    def use_logo_in_excel(self) -> bool:
        """¿Usar logo en reportes Excel?"""
        return self._config.get('branding', {}).get('use_logo_in_excel', True)
    
    def get_logo_dimensions(self) -> tuple:
        """Obtener dimensiones del logo (width, height)"""
        branding = self._config.get('branding', {})
        return (branding.get('logo_width', 150), branding.get('logo_height', 50))
    
    # ========== COLORS ==========
    
    def get_color(self, color_name: str) -> str:
        """Obtener color por nombre"""
        colors = self._config.get('colors', {})
        return colors.get(color_name, '#0067B1')
    
    def get_all_colors(self) -> Dict[str, str]:
        """Obtener todos los colores"""
        return self._config.get('colors', {})
    
    def set_color(self, color_name: str, color_value: str) -> bool:
        """Establecer un color"""
        if 'colors' not in self._config:
            self._config['colors'] = {}
        self._config['colors'][color_name] = color_value
        return self._save_config()
    
    # ========== TEXTS ==========
    
    def get_text(self, text_key: str, **kwargs) -> str:
        """Obtener texto por clave (soporta formateo)"""
        texts = self._config.get('texts', {})
        text = texts.get(text_key, '')
        
        # Formatear si hay kwargs
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass  # Si falta alguna clave, devolver sin formatear
        
        return text
    
    def set_text(self, text_key: str, text_value: str) -> bool:
        """Establecer un texto"""
        if 'texts' not in self._config:
            self._config['texts'] = {}
        self._config['texts'][text_key] = text_value
        return self._save_config()
    
    # ========== EXPORT/IMPORT ==========
    
    def export_config(self, export_path: Path) -> bool:
        """Exportar configuración a archivo JSON"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"ERROR: Error exportando configuración: {e}")
            return False
    
    def import_config(self, import_path: Path) -> bool:
        """Importar configuración desde archivo JSON"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Validar estructura básica
            required_keys = ['company', 'branding', 'colors', 'texts']
            if all(key in imported_config for key in required_keys):
                self._config = imported_config
                return self._save_config()
            else:
                print("ERROR: Configuración importada no válida")
                return False
        except Exception as e:
            print(f"ERROR: Error importando configuración: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Resetear a configuración por defecto"""
        self._config = self._get_default_config()
        return self._save_config()
    
    # ========== UTILITY ==========
    
    def get_full_config(self) -> Dict:
        """Obtener configuración completa"""
        return self._config.copy()
    
    def reload(self):
        """Recargar configuración desde archivo"""
        self._load_config()


# Funciones de conveniencia para importar fácilmente
_branding_manager = None

def get_branding_manager() -> BrandingManager:
    """Obtener instancia del BrandingManager (singleton)"""
    global _branding_manager
    if _branding_manager is None:
        _branding_manager = BrandingManager()
    return _branding_manager


# Funciones de acceso rápido
def get_company_name() -> str:
    return get_branding_manager().get_company_name()

def get_logo_path() -> Optional[Path]:
    return get_branding_manager().get_logo_path()

def get_color(color_name: str) -> str:
    return get_branding_manager().get_color(color_name)

def get_text(text_key: str, **kwargs) -> str:
    return get_branding_manager().get_text(text_key, **kwargs)

def set_logo(logo_path: Optional[Path]) -> bool:
    return get_branding_manager().set_logo_path(logo_path)

def set_company_name(name: str) -> bool:
    return get_branding_manager().set_company_name(name)
