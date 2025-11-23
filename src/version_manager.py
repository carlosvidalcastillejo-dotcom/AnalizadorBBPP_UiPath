"""
Gestor de Versionado Semántico
Maneja el incremento automático de versiones siguiendo semver (MAJOR.MINOR.PATCH)
"""

import re
from pathlib import Path
from typing import Tuple, Optional


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """
    Parsear string de versión a tupla (major, minor, patch)
    
    Args:
        version_str: Versión en formato "X.Y.Z"
        
    Returns:
        Tupla (major, minor, patch)
        
    Raises:
        ValueError: Si el formato no es válido
    """
    pattern = r'^(\d+)\.(\d+)\.(\d+)$'
    match = re.match(pattern, version_str.strip())
    
    if not match:
        raise ValueError(f"Formato de versión inválido: {version_str}. Debe ser X.Y.Z")
    
    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch)


def version_to_string(major: int, minor: int, patch: int) -> str:
    """
    Convertir tupla de versión a string
    
    Args:
        major: Número de versión mayor
        minor: Número de versión menor
        patch: Número de parche
        
    Returns:
        String en formato "X.Y.Z"
    """
    return f"{major}.{minor}.{patch}"


def increment_version(current_version: str, bump_type: str) -> str:
    """
    Incrementar versión según tipo de bump
    
    Args:
        current_version: Versión actual en formato "X.Y.Z"
        bump_type: Tipo de incremento ("major", "minor", "patch")
        
    Returns:
        Nueva versión en formato "X.Y.Z"
        
    Raises:
        ValueError: Si el tipo de bump no es válido
    """
    major, minor, patch = parse_version(current_version)
    
    bump_type = bump_type.lower()
    
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Tipo de bump inválido: {bump_type}. Debe ser 'major', 'minor' o 'patch'")
    
    return version_to_string(major, minor, patch)


def get_current_version(config_path: Optional[Path] = None) -> str:
    """
    Leer versión actual desde config.py
    
    Args:
        config_path: Ruta al archivo config.py (si None, usa ruta por defecto)
        
    Returns:
        Versión actual en formato "X.Y.Z"
        
    Raises:
        FileNotFoundError: Si no se encuentra config.py
        ValueError: Si no se encuentra APP_VERSION en el archivo
    """
    if config_path is None:
        # Ruta por defecto
        config_path = Path(__file__).parent / 'config.py'
    
    if not config_path.exists():
        raise FileNotFoundError(f"No se encontró config.py en: {config_path}")
    
    # Leer archivo
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar APP_VERSION
    pattern = r'APP_VERSION\s*=\s*["\']([^"\']+)["\']'
    match = re.search(pattern, content)
    
    if not match:
        raise ValueError("No se encontró APP_VERSION en config.py")
    
    return match.group(1)


def update_version_in_config(new_version: str, config_path: Optional[Path] = None) -> bool:
    """
    Actualizar versión en config.py
    
    Args:
        new_version: Nueva versión en formato "X.Y.Z"
        config_path: Ruta al archivo config.py (si None, usa ruta por defecto)
        
    Returns:
        True si se actualizó correctamente
        
    Raises:
        FileNotFoundError: Si no se encuentra config.py
    """
    if config_path is None:
        # Ruta por defecto
        config_path = Path(__file__).parent / 'config.py'
    
    if not config_path.exists():
        raise FileNotFoundError(f"No se encontró config.py en: {config_path}")
    
    # Leer archivo
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazar APP_VERSION
    pattern = r'(APP_VERSION\s*=\s*["\'])([^"\']+)(["\'])'
    new_content = re.sub(pattern, rf'\g<1>{new_version}\g<3>', content)
    
    # Guardar
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True


def suggest_version_bump(current_version: str) -> dict:
    """
    Sugerir opciones de incremento de versión
    
    Args:
        current_version: Versión actual en formato "X.Y.Z"
        
    Returns:
        Diccionario con opciones:
        {
            'patch': '0.2.7',
            'minor': '0.3.0',
            'major': '1.0.0'
        }
    """
    return {
        'patch': increment_version(current_version, 'patch'),
        'minor': increment_version(current_version, 'minor'),
        'major': increment_version(current_version, 'major')
    }


def compare_versions(version1: str, version2: str) -> int:
    """
    Comparar dos versiones
    
    Args:
        version1: Primera versión
        version2: Segunda versión
        
    Returns:
        -1 si version1 < version2
         0 si version1 == version2
         1 si version1 > version2
    """
    v1 = parse_version(version1)
    v2 = parse_version(version2)
    
    if v1 < v2:
        return -1
    elif v1 > v2:
        return 1
    else:
        return 0


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def is_valid_version(version_str: str) -> bool:
    """
    Verificar si un string es una versión válida
    
    Args:
        version_str: String a verificar
        
    Returns:
        True si es válido
    """
    try:
        parse_version(version_str)
        return True
    except ValueError:
        return False


def get_version_info(version_str: str) -> dict:
    """
    Obtener información detallada de una versión
    
    Args:
        version_str: Versión en formato "X.Y.Z"
        
    Returns:
        Diccionario con información:
        {
            'version': '0.2.6',
            'major': 0,
            'minor': 2,
            'patch': 6,
            'is_stable': False  # True si major >= 1
        }
    """
    major, minor, patch = parse_version(version_str)
    
    return {
        'version': version_str,
        'major': major,
        'minor': minor,
        'patch': patch,
        'is_stable': major >= 1
    }
