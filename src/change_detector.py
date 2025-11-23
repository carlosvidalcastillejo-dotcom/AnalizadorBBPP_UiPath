"""
Detector de Cambios para Changelog Automático
Analiza archivos modificados y genera descripción de cambios
"""

import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Set
import json


def get_modified_files(project_root: Path, hours: int = 24) -> List[Dict]:
    """
    Obtener archivos modificados en las últimas N horas
    
    Args:
        project_root: Ruta raíz del proyecto
        hours: Horas hacia atrás para buscar cambios
        
    Returns:
        Lista de diccionarios con info de archivos modificados:
        [
            {
                'path': 'src/analyzer.py',
                'type': 'modified',  # 'new', 'modified', 'deleted'
                'size': 18340,
                'modified_time': '2025-11-21 20:30:00'
            }
        ]
    """
    cutoff_time = datetime.now() - timedelta(hours=hours)
    modified_files = []
    
    # Extensiones a considerar
    code_extensions = {'.py', '.json', '.md', '.txt', '.yaml', '.yml'}
    
    # Directorios a ignorar
    ignore_dirs = {'__pycache__', '.git', 'dist', 'build', 'output', '.pytest_cache', 'node_modules'}
    
    for root, dirs, files in os.walk(project_root):
        # Filtrar directorios ignorados
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            file_path = Path(root) / file
            
            # Solo archivos de código
            if file_path.suffix not in code_extensions:
                continue
            
            try:
                # Obtener tiempo de modificación
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                # Si fue modificado recientemente
                if mtime > cutoff_time:
                    relative_path = file_path.relative_to(project_root)
                    
                    modified_files.append({
                        'path': str(relative_path).replace('\\\\', '/'),
                        'type': 'modified',  # Asumimos modificado por ahora
                        'size': file_path.stat().st_size,
                        'modified_time': mtime.strftime('%Y-%m-%d %H:%M:%S')
                    })
            except Exception:
                continue
    
    return sorted(modified_files, key=lambda x: x['modified_time'], reverse=True)


def categorize_changes(files: List[Dict]) -> Dict[str, List[str]]:
    """
    Categorizar cambios por tipo
    
    Args:
        files: Lista de archivos modificados
        
    Returns:
        Diccionario con cambios categorizados:
        {
            'added': ['src/new_module.py'],
            'changed': ['src/analyzer.py', 'build.py'],
            'fixed': [],
            'removed': []
        }
    """
    categories = {
        'added': [],
        'changed': [],
        'fixed': [],
        'removed': []
    }
    
    for file_info in files:
        path = file_info['path']
        
        # Categorizar según tipo
        if file_info['type'] == 'new':
            categories['added'].append(path)
        elif file_info['type'] == 'deleted':
            categories['removed'].append(path)
        else:
            categories['changed'].append(path)
    
    return categories


def generate_changelog_description(files: List[Dict], bump_type: str = 'patch') -> str:
    """
    Generar descripción de changelog basada en archivos modificados
    
    Args:
        files: Lista de archivos modificados
        bump_type: Tipo de cambio (patch/minor/major)
        
    Returns:
        Descripción formateada para changelog
    """
    if not files:
        return f"Build de versión ({bump_type})"
    
    # Categorizar cambios
    categories = categorize_changes(files)
    
    description_parts = []
    
    # Determinar tipo de cambio principal
    if bump_type == 'major':
        description_parts.append("### Cambios importantes")
    elif bump_type == 'minor':
        description_parts.append("### Nuevas funcionalidades")
    else:
        description_parts.append("### Mejoras y correcciones")
    
    description_parts.append("")
    
    # Añadidos
    if categories['added']:
        description_parts.append("**Archivos nuevos:**")
        for path in categories['added'][:5]:  # Máximo 5
            description_parts.append(f"- {path}")
        if len(categories['added']) > 5:
            description_parts.append(f"- ... y {len(categories['added']) - 5} más")
        description_parts.append("")
    
    # Modificados
    if categories['changed']:
        description_parts.append("**Archivos modificados:**")
        for path in categories['changed'][:5]:  # Máximo 5
            description_parts.append(f"- {path}")
        if len(categories['changed']) > 5:
            description_parts.append(f"- ... y {len(categories['changed']) - 5} más")
        description_parts.append("")
    
    # Eliminados
    if categories['removed']:
        description_parts.append("**Archivos eliminados:**")
        for path in categories['removed'][:5]:
            description_parts.append(f"- {path}")
        description_parts.append("")
    
    return "\n".join(description_parts)


def detect_feature_type(files: List[Dict]) -> str:
    """
    Detectar tipo de feature basado en archivos modificados
    
    Args:
        files: Lista de archivos modificados
        
    Returns:
        Tipo sugerido: 'patch', 'minor', 'major'
    """
    # Contadores
    new_files = sum(1 for f in files if f['type'] == 'new')
    modified_files = sum(1 for f in files if f['type'] == 'modified')
    
    # Archivos críticos
    critical_files = {'config.py', 'main.py', 'analyzer.py'}
    has_critical_changes = any(
        Path(f['path']).name in critical_files 
        for f in files
    )
    
    # Lógica de detección
    if new_files >= 3 or has_critical_changes:
        return 'minor'  # Nuevas funcionalidades
    elif new_files >= 1:
        return 'minor'  # Al menos un archivo nuevo
    elif modified_files >= 5:
        return 'minor'  # Muchos cambios
    else:
        return 'patch'  # Cambios menores


def get_change_summary(project_root: Path, hours: int = 24) -> Dict:
    """
    Obtener resumen completo de cambios
    
    Args:
        project_root: Ruta raíz del proyecto
        hours: Horas hacia atrás para buscar cambios
        
    Returns:
        Diccionario con resumen:
        {
            'files': [...],
            'total_files': 5,
            'suggested_bump': 'patch',
            'description': '...',
            'categories': {...}
        }
    """
    files = get_modified_files(project_root, hours)
    
    if not files:
        return {
            'files': [],
            'total_files': 0,
            'suggested_bump': 'patch',
            'description': 'Sin cambios detectados',
            'categories': {'added': [], 'changed': [], 'fixed': [], 'removed': []}
        }
    
    suggested_bump = detect_feature_type(files)
    categories = categorize_changes(files)
    description = generate_changelog_description(files, suggested_bump)
    
    return {
        'files': files,
        'total_files': len(files),
        'suggested_bump': suggested_bump,
        'description': description,
        'categories': categories
    }


def format_changes_for_preview(summary: Dict) -> str:
    """
    Formatear cambios para mostrar en preview editable
    
    Args:
        summary: Resumen de cambios de get_change_summary()
        
    Returns:
        String formateado para mostrar al usuario
    """
    lines = []
    
    lines.append("=" * 70)
    lines.append("  CAMBIOS DETECTADOS AUTOMÁTICAMENTE")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"📊 Total de archivos modificados: {summary['total_files']}")
    lines.append(f"📈 Tipo de cambio sugerido: {summary['suggested_bump'].upper()}")
    lines.append("")
    lines.append("=" * 70)
    lines.append("  DESCRIPCIÓN GENERADA (editable)")
    lines.append("=" * 70)
    lines.append("")
    lines.append(summary['description'])
    lines.append("")
    lines.append("=" * 70)
    
    return "\n".join(lines)


def save_changes_cache(summary: Dict, cache_path: Path):
    """
    Guardar caché de cambios detectados
    
    Args:
        summary: Resumen de cambios
        cache_path: Ruta donde guardar el caché
    """
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️  Error al guardar caché de cambios: {e}")


def load_changes_cache(cache_path: Path) -> Dict:
    """
    Cargar caché de cambios detectados
    
    Args:
        cache_path: Ruta del archivo de caché
        
    Returns:
        Resumen de cambios o dict vacío
    """
    try:
        if cache_path.exists():
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    
    return {
        'files': [],
        'total_files': 0,
        'suggested_bump': 'patch',
        'description': '',
        'categories': {'added': [], 'changed': [], 'fixed': [], 'removed': []}
    }
