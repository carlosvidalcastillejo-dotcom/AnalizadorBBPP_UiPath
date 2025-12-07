"""
Validador de Compatibilidad de Versiones UiPath
Verifica que las dependencias sean compatibles con la versión de Studio
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple
from packaging import version


def load_compatibility_matrix() -> Dict:
    """Cargar matriz de compatibilidad desde config"""
    config_path = Path(__file__).parent.parent / 'config' / 'version_compatibility.json'

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: No se pudo cargar version_compatibility.json: {e}")
        return {'compatibility_matrix': {}, 'version_order': []}


def extract_version_key(studio_version: str) -> Optional[str]:
    """
    Extraer clave de versión de UiPath Studio

    Args:
        studio_version: Versión completa (ej: "2023.10.5.1", "23.10.5")

    Returns:
        Clave de versión (ej: "2023.10") o None
    """
    if not studio_version:
        return None

    # Manejar formatos: "2023.10.5.1", "23.10.5", "2023.10"
    parts = studio_version.split('.')

    if len(parts) < 2:
        return None

    # Si empieza con año de 4 dígitos (2019-2024)
    year = parts[0]
    month = parts[1]

    # Normalizar año (si viene como "23" → "2023")
    if len(year) == 2:
        # Asumir 20XX para versiones >= 19
        if int(year) >= 19:
            year = f"20{year}"
        else:
            year = f"20{year}"

    return f"{year}.{month}"


def validate_dependency_compatibility(
    project_info: Dict,
    selected_studio_version: Optional[str] = None
) -> Dict:
    """
    Validar compatibilidad de dependencias con versión de Studio

    Args:
        project_info: Información del proyecto (contiene studio_version y dependencies)
        selected_studio_version: Versión de Studio seleccionada manualmente (opcional)

    Returns:
        Dict con resultados de validación:
        {
            'studio_version_used': str,  # Versión usada para validación
            'studio_version_from_project': str,  # Versión en project.json
            'validation_results': [
                {
                    'package': str,
                    'installed_version': str,
                    'expected_version': str,
                    'status': 'updated' | 'outdated' | 'incompatible',
                    'message': str
                }
            ]
        }
    """
    # Cargar matriz de compatibilidad
    compat_data = load_compatibility_matrix()
    compat_matrix = compat_data.get('compatibility_matrix', {})

    # Determinar versión de Studio a usar
    studio_version_from_project = project_info.get('studio_version', 'Unknown')

    if selected_studio_version:
        # Usuario seleccionó manualmente
        studio_version_key = selected_studio_version
        version_used = selected_studio_version
    else:
        # Usar versión del project.json
        studio_version_key = extract_version_key(studio_version_from_project)
        version_used = studio_version_from_project

    # Si no encontramos versión válida
    if not studio_version_key or studio_version_key not in compat_matrix:
        return {
            'studio_version_used': version_used,
            'studio_version_from_project': studio_version_from_project,
            'validation_results': [],
            'error': f'Versión de Studio no soportada o no encontrada: {studio_version_key}'
        }

    # Obtener versiones mínimas esperadas
    expected_versions = compat_matrix[studio_version_key].get('min_versions', {})

    # Validar dependencias
    dependencies = project_info.get('dependencies', [])
    validation_results = []

    # Dependencias críticas a validar
    critical_packages = ['UiPath.System.Activities', 'UiPath.UIAutomation.Activities']

    for dep in dependencies:
        package_name = dep.get('name', '')
        installed_version = dep.get('version', '')

        # Solo validar paquetes críticos
        if package_name not in critical_packages:
            continue

        # Obtener versión mínima esperada
        expected_version = expected_versions.get(package_name, None)

        if not expected_version:
            continue

        # Comparar versiones
        try:
            installed_ver = version.parse(installed_version)
            expected_ver = version.parse(expected_version)

            if installed_ver >= expected_ver:
                status = 'updated'
                message = f'Versión actualizada (>= {expected_version})'
            else:
                status = 'outdated'
                message = f'Versión desactualizada. Se recomienda {expected_version} o superior'

        except Exception as e:
            status = 'unknown'
            message = f'No se pudo comparar versiones: {e}'

        validation_results.append({
            'package': package_name,
            'installed_version': installed_version,
            'expected_version': expected_version,
            'status': status,
            'message': message
        })

    return {
        'studio_version_used': version_used,
        'studio_version_from_project': studio_version_from_project,
        'selected_manually': selected_studio_version is not None,
        'validation_results': validation_results
    }
