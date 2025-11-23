"""
Generador de Notas de Versión (Release Notes)
Gestiona la creación y actualización del archivo CHANGELOG.md
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


# ============================================================================
# PLANTILLAS DE CHANGELOG
# ============================================================================

CHANGELOG_HEADER = """# Changelog

Todos los cambios notables del proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

"""


def create_changelog_entry(
    version: str,
    date: str,
    author: str,
    changes: Dict[str, List[str]],
    bump_type: str = "patch"
) -> str:
    """
    Crear entrada de changelog en formato Markdown
    
    Args:
        version: Versión (ej: "0.2.7")
        date: Fecha en formato YYYY-MM-DD
        author: Nombre del autor del build
        changes: Diccionario con cambios por categoría:
                 {
                     'added': ['Feature 1', 'Feature 2'],
                     'changed': ['Change 1'],
                     'fixed': ['Bug fix 1'],
                     'removed': ['Deprecated feature']
                 }
        bump_type: Tipo de incremento (patch/minor/major)
        
    Returns:
        String con la entrada de changelog formateada
    """
    # Encabezado de versión
    entry = f"## [{version}] - {date}\n\n"
    
    # Metadata
    entry += f"**Autor:** {author}  \n"
    entry += f"**Tipo de cambio:** {bump_type.capitalize()}  \n\n"
    
    # Secciones de cambios
    sections = {
        'added': '### Added',
        'changed': '### Changed',
        'fixed': '### Fixed',
        'removed': '### Removed',
        'deprecated': '### Deprecated',
        'security': '### Security'
    }
    
    for key, title in sections.items():
        if key in changes and changes[key]:
            entry += f"{title}\n"
            for change in changes[key]:
                entry += f"- {change}\n"
            entry += "\n"
    
    return entry


def create_simple_changelog_entry(
    version: str,
    date: str,
    author: str,
    description: str = "",
    bump_type: str = "patch"
) -> str:
    """
    Crear entrada simple de changelog (sin categorías detalladas)
    
    Args:
        version: Versión (ej: "0.2.7")
        date: Fecha en formato YYYY-MM-DD
        author: Nombre del autor del build
        description: Descripción breve de los cambios
        bump_type: Tipo de incremento (patch/minor/major)
        
    Returns:
        String con la entrada de changelog formateada
    """
    entry = f"## [{version}] - {date}\n\n"
    entry += f"**Autor:** {author}  \n"
    entry += f"**Tipo de cambio:** {bump_type.capitalize()}  \n\n"
    
    if description:
        entry += f"{description}\n\n"
    else:
        entry += f"Build de versión {version}\n\n"
    
    return entry


def update_changelog(
    entry: str,
    changelog_path: Optional[Path] = None,
    create_if_missing: bool = True
) -> bool:
    """
    Añadir entrada al inicio del CHANGELOG.md (después del header)
    
    Args:
        entry: Entrada de changelog a añadir
        changelog_path: Ruta al CHANGELOG.md (si None, usa ruta por defecto)
        create_if_missing: Si True, crea el archivo si no existe
        
    Returns:
        True si se actualizó correctamente
    """
    if changelog_path is None:
        # Ruta por defecto (raíz del proyecto)
        changelog_path = Path(__file__).parent.parent / 'CHANGELOG.md'
    
    # Si no existe y create_if_missing es True, crear con header
    if not changelog_path.exists():
        if create_if_missing:
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write(CHANGELOG_HEADER)
                f.write(entry)
            return True
        else:
            raise FileNotFoundError(f"No se encontró CHANGELOG.md en: {changelog_path}")
    
    # Leer contenido actual
    with open(changelog_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Si el archivo está vacío o solo tiene el header, añadir directamente
    if not content or content.strip() == CHANGELOG_HEADER.strip():
        new_content = CHANGELOG_HEADER + entry
    else:
        # Insertar después del header
        # Buscar el final del header (primera línea que empieza con ##)
        lines = content.split('\n')
        insert_index = 0
        
        for i, line in enumerate(lines):
            if line.startswith('## ['):
                insert_index = i
                break
        
        # Si no se encontró ninguna entrada previa, insertar después del header
        if insert_index == 0:
            # Buscar el final del header (líneas vacías después del texto inicial)
            header_end = 0
            for i, line in enumerate(lines):
                if i > 5 and line.strip() == '':  # Después de las primeras líneas del header
                    header_end = i + 1
                    break
            
            if header_end == 0:
                header_end = len(lines)
            
            lines.insert(header_end, entry.rstrip())
        else:
            # Insertar antes de la primera entrada existente
            lines.insert(insert_index, entry.rstrip())
            lines.insert(insert_index + 1, '')  # Línea en blanco
        
        new_content = '\n'.join(lines)
    
    # Guardar
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True


def get_latest_changelog_entry(changelog_path: Optional[Path] = None) -> Optional[Dict]:
    """
    Leer la última entrada del changelog
    
    Args:
        changelog_path: Ruta al CHANGELOG.md (si None, usa ruta por defecto)
        
    Returns:
        Diccionario con información de la última entrada:
        {
            'version': '0.2.6',
            'date': '2025-11-21',
            'content': '...'
        }
        o None si no hay entradas
    """
    if changelog_path is None:
        changelog_path = Path(__file__).parent.parent / 'CHANGELOG.md'
    
    if not changelog_path.exists():
        return None
    
    with open(changelog_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar primera entrada (línea que empieza con ## [)
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if line.startswith('## ['):
            # Extraer versión y fecha
            # Formato: ## [0.2.6] - 2025-11-21
            import re
            match = re.match(r'## \[([^\]]+)\] - (\d{4}-\d{2}-\d{2})', line)
            
            if match:
                version = match.group(1)
                date = match.group(2)
                
                # Extraer contenido hasta la siguiente entrada o fin de archivo
                entry_lines = [line]
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith('## ['):
                        break
                    entry_lines.append(lines[j])
                
                return {
                    'version': version,
                    'date': date,
                    'content': '\n'.join(entry_lines)
                }
    
    return None


def get_all_changelog_entries(changelog_path: Optional[Path] = None) -> List[Dict]:
    """
    Leer todas las entradas del changelog
    
    Args:
        changelog_path: Ruta al CHANGELOG.md
        
    Returns:
        Lista de diccionarios con todas las entradas
    """
    if changelog_path is None:
        changelog_path = Path(__file__).parent.parent / 'CHANGELOG.md'
    
    if not changelog_path.exists():
        return []
    
    with open(changelog_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = []
    lines = content.split('\n')
    current_entry = None
    
    for i, line in enumerate(lines):
        if line.startswith('## ['):
            # Si ya había una entrada en proceso, guardarla
            if current_entry:
                entries.append(current_entry)
            
            # Iniciar nueva entrada
            import re
            match = re.match(r'## \[([^\]]+)\] - (\d{4}-\d{2}-\d{2})', line)
            
            if match:
                current_entry = {
                    'version': match.group(1),
                    'date': match.group(2),
                    'content_lines': [line]
                }
        elif current_entry:
            current_entry['content_lines'].append(line)
    
    # Añadir última entrada
    if current_entry:
        entries.append(current_entry)
    
    # Convertir content_lines a content
    for entry in entries:
        entry['content'] = '\n'.join(entry['content_lines'])
        del entry['content_lines']
    
    return entries


def create_initial_changelog(
    initial_version: str = "0.1.0",
    initial_date: str = None,
    author: str = "Carlos Vidal Castillejo",
    changelog_path: Optional[Path] = None
) -> bool:
    """
    Crear CHANGELOG.md inicial con primera entrada
    
    Args:
        initial_version: Versión inicial
        initial_date: Fecha inicial (si None, usa fecha actual)
        author: Autor del proyecto
        changelog_path: Ruta donde crear el archivo
        
    Returns:
        True si se creó correctamente
    """
    if initial_date is None:
        initial_date = datetime.now().strftime("%Y-%m-%d")
    
    if changelog_path is None:
        changelog_path = Path(__file__).parent.parent / 'CHANGELOG.md'
    
    # Crear entrada inicial
    initial_entry = create_simple_changelog_entry(
        version=initial_version,
        date=initial_date,
        author=author,
        description="Versión inicial del proyecto",
        bump_type="major"
    )
    
    # Crear archivo
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write(CHANGELOG_HEADER)
        f.write(initial_entry)
    
    return True
