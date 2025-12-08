"""
Configuración global de la aplicación
Colores corporativos, rutas, constantes
"""

from pathlib import Path
from datetime import datetime
import json

# Importar BrandingManager para branding personalizable
try:
    from src.branding_manager import get_company_name, get_color, get_text
    BRANDING_AVAILABLE = True
except ImportError:
    BRANDING_AVAILABLE = False

# ============================================================================
# INFORMACIÓN DE LA APLICACIÓN
# ============================================================================
APP_NAME = "Analizador BBPP UiPath"
APP_VERSION = "1.1.2"
APP_VERSION_TYPE = "Stable"
APP_AUTHOR = "Carlos Vidal Castillejo"
BUILD_DATE = "2025-12-07 20:59:00"

# EMPRESA (ahora configurable)
if BRANDING_AVAILABLE:
    COMPANY = get_company_name()
else:
    COMPANY = "Your Company"  # Fallback

# ============================================================================
# COLORES CORPORATIVOS (ahora configurables)
# ============================================================================
if BRANDING_AVAILABLE:
    PRIMARY_COLOR = get_color('primary')
    SECONDARY_COLOR = get_color('secondary')
    ACCENT_COLOR = get_color('accent')
    BG_COLOR = "#FFFFFF"
    BG_SECONDARY = "#E5E5E5"
    TEXT_COLOR = "#58595B"
    TEXT_LIGHT = "#FFFFFF"
else:
    # Fallback colors
    PRIMARY_COLOR = "#0067B1"
    SECONDARY_COLOR = "#00A3E0"
    ACCENT_COLOR = "#003D7A"
    BG_COLOR = "#FFFFFF"
    BG_SECONDARY = "#E5E5E5"
    TEXT_COLOR = "#58595B"
    TEXT_LIGHT = "#FFFFFF"

# Colores para severidades
COLOR_ERROR = "#DC3545"  # Rojo
COLOR_WARNING = "#FFC107"  # Amarillo
COLOR_INFO = "#17A2B8"  # Azul claro
COLOR_SUCCESS = "#28A745"  # Verde

# ============================================================================
# RUTAS DEL PROYECTO
# ============================================================================
ROOT_DIR = Path(__file__).parent.parent
SRC_DIR = ROOT_DIR / "src"
ASSETS_DIR = ROOT_DIR / "assets"
CONFIG_DIR = ROOT_DIR / "config"
OUTPUT_DIR = ROOT_DIR / "output"
TESTS_DIR = ROOT_DIR / "tests"
DOCS_DIR = ROOT_DIR / "docs"

# Rutas de archivos de configuración
BBPP_DIR = CONFIG_DIR / "bbpp"
USER_CONFIG_FILE = CONFIG_DIR / "user_config.json"
LOGO_DEFAULT = ASSETS_DIR / "logo.png"  # Logo genérico

# Crear directorios si no existen
for directory in [ASSETS_DIR, CONFIG_DIR, OUTPUT_DIR, BBPP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# CONFIGURACIÓN DE ANÁLISIS - VALORES POR DEFECTO
# ============================================================================
DEFAULT_CONFIG = {
    "thresholds": {
        "max_activities_sequence": 20,  # Máximo de actividades por Sequence
        "max_nested_ifs": 3,  # Máximo de IFs anidados
        "max_commented_code_percent": 5,  # % máximo de código comentado
    },
    "validations": {
        "detect_unused_variables": False,  # Detectar variables no utilizadas (futuro)
    },
    "output": {
        "generate_html": True,
        "generate_excel": True,
        "generate_pdf": False,  # Futuro
        "include_charts": True,
        "include_commented_code_list": True,
    },
    "scoring": {
        "error_weight": -10,
        "warning_weight": -3,
        "info_weight": -0.5,
    }
}

# ============================================================================
# REGLAS BBPP - CATEGORÍAS
# ============================================================================
BBPP_CATEGORIES = [
    "nomenclatura",
    "hardcodeo",
    "anidamiento",
    "try_catch",
    "modularizacion",
    "logs",
    "custom"
]

# ============================================================================
# SEVERIDADES
# ============================================================================
SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"
SEVERITY_INFO = "info"

SEVERITIES = [SEVERITY_ERROR, SEVERITY_WARNING, SEVERITY_INFO]

SEVERITY_COLORS = {
    SEVERITY_ERROR: COLOR_ERROR,
    SEVERITY_WARNING: COLOR_WARNING,
    SEVERITY_INFO: COLOR_INFO,
}

SEVERITY_NAMES = {
    SEVERITY_ERROR: "Error",
    SEVERITY_WARNING: "Warning",
    SEVERITY_INFO: "Info",
}

# ============================================================================
# EXTENSIONES DE ARCHIVO
# ============================================================================
UIPATH_EXTENSIONS = [".xaml"]
CONFIG_EXTENSIONS = [".json", ".xlsx", ".xls", ".csv"]
DOCUMENT_EXTENSIONS = [".pdf", ".docx", ".doc"]

# ============================================================================
# MENSAJES
# ============================================================================
MSG_NO_PROJECT_SELECTED = "Por favor, selecciona una carpeta de proyecto UiPath"
MSG_ANALYSIS_COMPLETE = "Análisis completado con éxito"
MSG_ANALYSIS_CANCELLED = "Análisis cancelado por el usuario"
MSG_ERROR_READING_FILE = "Error al leer el archivo"
MSG_INVALID_PROJECT = "La carpeta seleccionada no parece ser un proyecto UiPath válido"

# ============================================================================
# CONFIGURACIÓN DE UI
# ============================================================================
WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION} {APP_VERSION_TYPE}"
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 700

# Fuentes
FONT_FAMILY = "Segoe UI"
FONT_SIZE_NORMAL = 10
FONT_SIZE_HEADING = 14
FONT_SIZE_TITLE = 18

# ============================================================================
# PATRONES REGEX COMUNES
# ============================================================================
PATTERN_CAMEL_CASE = r'^[a-z][a-zA-Z0-9]*$'
PATTERN_PASCAL_CASE = r'^[A-Z][a-zA-Z0-9]*$'
PATTERN_URL = r'https?://[^\s"]+'
PATTERN_FILE_PATH = r'[A-Za-z]:\\[\w\s\\\-\.]+|/[\w\s/\-\.]+'
PATTERN_GENERIC_VARIABLE_NAME = r'^(var|temp|test|data|value|result|output|item)\d*$'

# ============================================================================
# NOMBRES GENÉRICOS A DETECTAR
# ============================================================================
GENERIC_NAMES = [
    "var", "var1", "var2",
    "temp", "temp1", "temp2",
    "test", "test1",
    "data", "value", "result",
    "output", "input",
    "item", "elemento"
]

# ============================================================================
# SISTEMA DE CARGA DE REGLAS DESDE JSON
# ============================================================================
from typing import List, Dict

def load_bbpp_file(filepath: Path) -> Dict:
    """
    Cargar un archivo JSON de BBPP
    
    Args:
        filepath: Ruta al archivo JSON
        
    Returns:
        Diccionario con metadata y reglas
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"WARNING: Archivo no encontrado: {filepath}")
        return {"metadata": {}, "rules": []}
    except json.JSONDecodeError as e:
        print(f"ERROR: Error al parsear JSON {filepath}: {e}")
        return {"metadata": {}, "rules": []}
    except Exception as e:
        print(f"ERROR: Error al cargar {filepath}: {e}")
        return {"metadata": {}, "rules": []}


def load_all_bbpp_sets() -> List[Dict]:
    """
    Cargar todos los conjuntos de BBPP disponibles en config/bbpp/
    
    Returns:
        Lista de diccionarios con conjuntos de BBPP
    """
    bbpp_sets = []
    
    if not BBPP_DIR.exists():
        print(f"WARNING: Directorio de BBPP no encontrado: {BBPP_DIR}")
        return bbpp_sets
    
    # Buscar todos los archivos .json en el directorio (excepto BBPP_Master.json)
    json_files = [f for f in BBPP_DIR.glob("*.json") if f.name != "BBPP_Master.json"]

    if not json_files:
        print(f"WARNING: No se encontraron archivos JSON en {BBPP_DIR}")
        return bbpp_sets

    for json_file in json_files:
        bbpp_data = load_bbpp_file(json_file)
        if bbpp_data and bbpp_data.get("rules"):
            bbpp_data["_filepath"] = str(json_file)  # Guardar ruta para referencia
            bbpp_sets.append(bbpp_data)
            print(f"OK: Cargado: {bbpp_data['metadata'].get('name', json_file.name)}")
    
    return bbpp_sets


def get_enabled_rules(bbpp_sets: List[Dict] = None) -> List[Dict]:
    """
    Obtener todas las reglas habilitadas de todos los conjuntos
    
    Args:
        bbpp_sets: Lista de conjuntos de BBPP (si None, carga todos)
        
    Returns:
        Lista de reglas habilitadas
    """
    if bbpp_sets is None:
        bbpp_sets = load_all_bbpp_sets()
    
    enabled_rules = []
    
    for bbpp_set in bbpp_sets:
        rules = bbpp_set.get("rules", [])
        for rule in rules:
            if rule.get("enabled", True):  # Por defecto habilitada si no se especifica
                enabled_rules.append(rule)
    
    return enabled_rules


def get_rules_by_category(category: str, bbpp_sets: List[Dict] = None) -> List[Dict]:
    """
    Obtener reglas habilitadas filtradas por categoría
    
    Args:
        category: Categoría a filtrar (nomenclatura, anidamiento, etc.)
        bbpp_sets: Lista de conjuntos de BBPP (si None, carga todos)
        
    Returns:
        Lista de reglas de esa categoría
    """
    enabled_rules = get_enabled_rules(bbpp_sets)
    return [rule for rule in enabled_rules if rule.get("category") == category]


def get_rule_by_id(rule_id: str, bbpp_sets: List[Dict] = None) -> Dict:
    """
    Buscar una regla específica por su ID
    
    Args:
        rule_id: ID de la regla (ej: "NOMENCLATURA_001")
        bbpp_sets: Lista de conjuntos de BBPP (si None, carga todos)
        
    Returns:
        Diccionario con la regla o None si no se encuentra
    """
    enabled_rules = get_enabled_rules(bbpp_sets)
    for rule in enabled_rules:
        if rule.get("id") == rule_id:
            return rule
    return None


# ============================================================================
# CONFIGURACIÓN DE CONJUNTOS ACTIVOS
# ============================================================================

def load_user_config() -> Dict:
    """
    Cargar configuración del usuario desde user_config.json
    
    Returns:
        Diccionario con configuración del usuario
    """
    if not USER_CONFIG_FILE.exists():
        # Crear configuración por defecto
        default_config = {
            "version": "1.0.0",
            "last_updated": "2024-11-20",
            "active_bbpp_sets": [],  # Vacío = todos activos
            "ui_preferences": {
                "window_width": 1200,
                "window_height": 800
            },
            "thresholds": DEFAULT_CONFIG["thresholds"].copy(),
            "validations": DEFAULT_CONFIG["validations"].copy()
        }
        save_user_config(default_config)
        return default_config
    
    try:
        with open(USER_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"WARNING: Error al cargar user_config.json: {e}")
        return {
            "version": "1.0.0",
            "active_bbpp_sets": [],
            "thresholds": DEFAULT_CONFIG["thresholds"].copy(),
            "validations": DEFAULT_CONFIG["validations"].copy()
        }


def save_user_config(config: Dict) -> bool:
    """
    Guardar configuración del usuario
    
    Args:
        config: Diccionario con configuración
        
    Returns:
        True si se guardó correctamente
    """
    try:
        config["last_updated"] = "2024-11-20"
        with open(USER_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"ERROR: Error al guardar user_config.json: {e}")
        return False


def get_active_bbpp_sets() -> List[str]:
    """
    Obtener lista de nombres de archivos de conjuntos activos
    
    Returns:
        Lista de nombres de archivos (ej: ["BBPP_UiPath.json", "BBPP_NTTData.json"])
    """
    user_config = load_user_config()
    active_sets = user_config.get("active_bbpp_sets", [])
    
    # Si está vacío, activar todos por defecto
    if not active_sets:
        json_files = list(BBPP_DIR.glob("*.json"))
        return [f.name for f in json_files]
    
    return active_sets


def set_active_bbpp_sets(active_sets: List[str]) -> bool:
    """
    Establecer qué conjuntos de BBPP están activos
    
    Args:
        active_sets: Lista de nombres de archivos a activar
        
    Returns:
        True si se guardó correctamente
    """
    user_config = load_user_config()
    user_config["active_bbpp_sets"] = active_sets
    return save_user_config(user_config)


def get_active_rules() -> List[Dict]:
    """
    Obtener reglas activas según configuración del usuario
    
    Returns:
        Lista de reglas habilitadas de los conjuntos activos
    """
    active_set_names = get_active_bbpp_sets()
    
    # Cargar todos los conjuntos
    all_sets = load_all_bbpp_sets()
    
    # Filtrar solo los activos
    active_sets = []
    for bbpp_set in all_sets:
        filepath = Path(bbpp_set.get("_filepath", ""))
        if filepath.name in active_set_names:
            active_sets.append(bbpp_set)
    
    # Obtener reglas habilitadas de los conjuntos activos
    return get_enabled_rules(active_sets)


def get_available_bbpp_sets() -> List[Dict]:
    """
    Obtener información de todos los conjuntos disponibles
    
    Returns:
        Lista de diccionarios con info de cada conjunto:
        {
            'filename': 'BBPP_UiPath.json',
            'name': 'Buenas Prácticas UiPath',
            'description': '...',
            'rules_count': 9,
            'is_active': True
        }
    """
    all_sets = load_all_bbpp_sets()
    active_names = get_active_bbpp_sets()
    
    result = []
    for bbpp_set in all_sets:
        filepath = Path(bbpp_set.get("_filepath", ""))
        metadata = bbpp_set.get("metadata", {})
        
        info = {
            'filename': filepath.name,
            'filepath': str(filepath),
            'name': metadata.get('name', filepath.name),
            'description': metadata.get('description', ''),
            'version': metadata.get('version', '1.0.0'),
            'author': metadata.get('author', ''),
            'rules_count': len(bbpp_set.get('rules', [])),
            'is_active': filepath.name in active_names
        }
        result.append(info)
    
    return result


# ============================================================================
# EXPORTAR E IMPORTAR CONJUNTOS DE BBPP
# ============================================================================

def export_bbpp_set(source_filepath: Path, destination_filepath: Path) -> bool:
    """
    Exportar un conjunto de BBPP a un archivo
    
    Args:
        source_filepath: Ruta del archivo JSON origen
        destination_filepath: Ruta donde guardar la exportación
        
    Returns:
        True si se exportó correctamente
    """
    try:
        import shutil
        from datetime import datetime
        
        # Leer el archivo origen
        bbpp_data = load_bbpp_file(source_filepath)
        
        if not bbpp_data or not bbpp_data.get('rules'):
            print(f"WARNING: No hay datos válidos para exportar en {source_filepath}")
            return False
        
        # Agregar metadata de exportación
        if 'metadata' not in bbpp_data:
            bbpp_data['metadata'] = {}
        
        bbpp_data['metadata']['exported_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bbpp_data['metadata']['exported_from'] = str(source_filepath)
        
        # Guardar en destino
        with open(destination_filepath, 'w', encoding='utf-8') as f:
            json.dump(bbpp_data, f, indent=2, ensure_ascii=False)
        
        print(f"OK: Conjunto exportado: {destination_filepath}")
        return True
        
    except Exception as e:
        print(f"ERROR: Error al exportar conjunto: {e}")
        return False


def import_bbpp_set(source_filepath: Path, destination_filename: str = None) -> bool:
    """
    Importar un conjunto de BBPP desde un archivo
    
    Args:
        source_filepath: Ruta del archivo JSON a importar
        destination_filename: Nombre del archivo destino (si None, usa el nombre original)
        
    Returns:
        True si se importó correctamente
    """
    try:
        from datetime import datetime
        import shutil
        
        # Validar que el archivo existe
        if not source_filepath.exists():
            print(f"ERROR: Archivo no encontrado: {source_filepath}")
            return False
        
        # Leer y validar el archivo
        bbpp_data = load_bbpp_file(source_filepath)
        
        if not bbpp_data:
            print(f"ERROR: Archivo JSON inválido o vacío")
            return False
        
        # Validar estructura básica
        if 'rules' not in bbpp_data:
            print(f"ERROR: El archivo no tiene estructura de conjunto de BBPP (falta 'rules')")
            return False
        
        # Validar estructura completa
        is_valid, error_msg = validate_bbpp_structure(bbpp_data)
        if not is_valid:
            print(f"ERROR: Estructura de BBPP inválida: {error_msg}")
            return False
        
        # Validar que tiene al menos metadata básica
        if 'metadata' not in bbpp_data:
            print(f"WARNING: El archivo no tiene metadata, se agregará metadata básica")
            bbpp_data['metadata'] = {
                'name': 'Conjunto Importado',
                'version': '1.0.0',
                'imported_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        # Determinar nombre de archivo destino
        if destination_filename is None:
            destination_filename = source_filepath.name
        
        # Asegurar que termina en .json
        if not destination_filename.endswith('.json'):
            destination_filename += '.json'
        
        destination_path = BBPP_DIR / destination_filename
        
        # Si ya existe, hacer backup
        if destination_path.exists():
            backup_path = BBPP_DIR / f"{destination_filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(destination_path, backup_path)
            print(f"📦 Backup creado: {backup_path.name}")
        
        # Agregar metadata de importación
        bbpp_data['metadata']['imported_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bbpp_data['metadata']['imported_from'] = str(source_filepath)
        
        # Guardar en destino
        with open(destination_path, 'w', encoding='utf-8') as f:
            json.dump(bbpp_data, f, indent=2, ensure_ascii=False)
        
        print(f"OK: Conjunto importado: {destination_path.name}")
        return True
        
    except Exception as e:
        print(f"ERROR: Error al importar conjunto: {e}")
        return False


def validate_bbpp_structure(bbpp_data: Dict) -> tuple:
    """
    Validar que un conjunto de BBPP tiene la estructura correcta
    
    Args:
        bbpp_data: Diccionario con datos del conjunto
        
    Returns:
        (is_valid, error_message)
    """
    # Verificar campos obligatorios
    if 'rules' not in bbpp_data:
        return False, "Falta el campo 'rules'"
    
    if not isinstance(bbpp_data['rules'], list):
        return False, "'rules' debe ser una lista"
    
    # Verificar estructura de cada regla
    required_rule_fields = ['id', 'name', 'category', 'severity', 'enabled', 'rule_type']
    
    for i, rule in enumerate(bbpp_data['rules']):
        for field in required_rule_fields:
            if field not in rule:
                return False, f"Regla #{i+1}: falta el campo '{field}'"
    
    return True, "Estructura válida"


def export_all_active_bbpp(destination_filepath: Path) -> bool:
    """
    Exportar todos los conjuntos activos en un solo archivo
    
    Args:
        destination_filepath: Ruta donde guardar la exportación
        
    Returns:
        True si se exportó correctamente
    """
    try:
        from datetime import datetime
        
        active_set_names = get_active_bbpp_sets()
        all_sets = load_all_bbpp_sets()
        
        # Filtrar solo los activos
        active_sets = [s for s in all_sets if Path(s.get("_filepath", "")).name in active_set_names]
        
        if not active_sets:
            print("WARNING: No hay conjuntos activos para exportar")
            return False
        
        # Crear estructura consolidada
        consolidated = {
            "metadata": {
                "name": "Configuración Consolidada",
                "description": "Exportación de todos los conjuntos activos",
                "version": "1.0.0",
                "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "exported_sets": [s['metadata']['name'] for s in active_sets]
            },
            "sets": []
        }
        
        # Agregar cada conjunto
        for bbpp_set in active_sets:
            filepath = Path(bbpp_set.get("_filepath", ""))
            consolidated["sets"].append({
                "filename": filepath.name,
                "metadata": bbpp_set.get("metadata", {}),
                "rules": bbpp_set.get("rules", [])
            })
        
        # Guardar
        with open(destination_filepath, 'w', encoding='utf-8') as f:
            json.dump(consolidated, f, indent=2, ensure_ascii=False)
        
        print(f"OK: Configuración consolidada exportada: {destination_filepath}")
        return True
        
    except Exception as e:
        print(f"ERROR: Error al exportar configuración consolidada: {e}")
        return False


# ============================================================================
# FUNCIONES DE CONFIGURACIÓN DE USUARIO
# ============================================================================

def load_user_config() -> dict:
    """
    Cargar configuración de usuario desde archivo
    
    Returns:
        Dict con la configuración completa
    """
    try:
        if USER_CONFIG_FILE.exists():
            with open(USER_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Si no existe, crear con valores por defecto
            default_config = {
                "version": "1.0.0",
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "active_bbpp_sets": [],
                "ui_preferences": {
                    "window_width": WINDOW_MIN_WIDTH,
                    "window_height": WINDOW_MIN_HEIGHT
                },
                "thresholds": DEFAULT_CONFIG["thresholds"].copy(),
                "validations": DEFAULT_CONFIG["validations"].copy(),
                "output": DEFAULT_CONFIG["output"].copy(),
                "scoring": DEFAULT_CONFIG["scoring"].copy(),
                "custom_logo": None
            }
            save_user_config(default_config)
            return default_config
    except Exception as e:
        print(f"ERROR: Error al cargar configuración de usuario: {e}")
        return {}


def save_user_config(config: dict) -> bool:
    """
    Guardar configuración de usuario en archivo
    
    Args:
        config: Diccionario con la configuración completa
        
    Returns:
        True si se guardó correctamente
    """
    try:
        from datetime import datetime
        
        # Actualizar fecha
        config["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        
        # Guardar
        with open(USER_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"OK: Configuración guardada correctamente")
        return True
        
    except Exception as e:
        print(f"ERROR: Error al guardar configuración: {e}")
        return False


def get_threshold(key: str) -> any:
    """
    Obtener un umbral específico de la configuración
    
    Args:
        key: Clave del umbral (ej: 'max_activities_sequence')
        
    Returns:
        Valor del umbral o None si no existe
    """
    config = load_user_config()
    return config.get("thresholds", {}).get(key)


def set_threshold(key: str, value: any) -> bool:
    """
    Establecer un umbral específico
    
    Args:
        key: Clave del umbral
        value: Nuevo valor
        
    Returns:
        True si se guardó correctamente
    """
    config = load_user_config()
    if "thresholds" not in config:
        config["thresholds"] = {}
    config["thresholds"][key] = value
    return save_user_config(config)


def get_validation_option(key: str) -> bool:
    """
    Obtener una opción de validación
    
    Args:
        key: Clave de la opción
        
    Returns:
        Estado de la opción (True/False)
    """
    config = load_user_config()
    return config.get("validations", {}).get(key, False)


def set_validation_option(key: str, value: bool) -> bool:
    """
    Establecer una opción de validación
    
    Args:
        key: Clave de la opción
        value: Nuevo valor (True/False)
        
    Returns:
        True si se guardó correctamente
    """
    config = load_user_config()
    if "validations" not in config:
        config["validations"] = {}
    config["validations"][key] = value
    return save_user_config(config)


def get_output_option(key: str) -> any:
    """
    Obtener una opción de salida/reporte
    
    Args:
        key: Clave de la opción
        
    Returns:
        Valor de la opción
    """
    config = load_user_config()
    return config.get("output", {}).get(key)


def set_output_option(key: str, value: any) -> bool:
    """
    Establecer una opción de salida/reporte
    
    Args:
        key: Clave de la opción
        value: Nuevo valor
        
    Returns:
        True si se guardó correctamente
    """
    config = load_user_config()
    if "output" not in config:
        config["output"] = {}
    config["output"][key] = value
    return save_user_config(config)


def get_custom_logo() -> Path:
    """
    Obtener ruta del logo personalizado
    
    Returns:
        Path al logo personalizado o logo por defecto
    """
    config = load_user_config()
    custom_logo = config.get("custom_logo")
    
    if custom_logo and Path(custom_logo).exists():
        return Path(custom_logo)
    else:
        return LOGO_DEFAULT


def set_custom_logo(logo_path: Path) -> bool:
    """
    Establecer logo personalizado
    
    Args:
        logo_path: Ruta al nuevo logo
        
    Returns:
        True si se guardó correctamente
    """
    config = load_user_config()
    config["custom_logo"] = str(logo_path) if logo_path else None
    return save_user_config(config)


def reset_to_defaults() -> bool:
    """
    Restaurar configuración a valores por defecto
    
    Returns:
        True si se restauró correctamente
    """
    try:
        default_config = {
            "version": "1.0.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "active_bbpp_sets": [],
            "ui_preferences": {
                "window_width": WINDOW_MIN_WIDTH,
                "window_height": WINDOW_MIN_HEIGHT
            },
            "thresholds": DEFAULT_CONFIG["thresholds"].copy(),
            "validations": DEFAULT_CONFIG["validations"].copy(),
            "output": DEFAULT_CONFIG["output"].copy(),
            "scoring": DEFAULT_CONFIG["scoring"].copy(),
            "custom_logo": None
        }
        return save_user_config(default_config)
    except Exception as e:
        print(f"ERROR: Error al restaurar configuración: {e}")
        return False
