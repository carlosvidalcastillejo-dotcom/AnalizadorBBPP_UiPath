"""
Utilidades para generación de reportes
Funciones helper para nombres de archivos y apertura de reportes
"""

import os
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional


def generate_report_filename(project_name: str, extension: str) -> str:
    """
    Generar nombre de archivo de reporte con formato estándar
    
    Args:
        project_name: Nombre del proyecto
        extension: 'html' o 'xlsx' (sin punto)
    
    Returns:
        Nombre del archivo: REPORTE_NombreProyecto_AAAAMMDD_HHmmss.ext
    
    Example:
        >>> generate_report_filename("Proyecto Clientes", "html")
        'REPORTE_ProyectoClientes_20251122_110730.html'
    """
    # Limpiar nombre del proyecto (sin espacios ni caracteres especiales)
    clean_name = re.sub(r'[^\w\-]', '', project_name.replace(' ', ''))
    
    # Limitar longitud del nombre
    if len(clean_name) > 50:
        clean_name = clean_name[:50]
    
    # Timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Asegurar que extension no tenga punto
    extension = extension.lstrip('.')
    
    return f"REPORTE_{clean_name}_{timestamp}.{extension}"


def get_report_output_dir(report_type: str) -> Path:
    """
    Obtener directorio de salida para reportes
    
    Args:
        report_type: 'html' o 'excel'
    
    Returns:
        Path al directorio (output/HTML/ o output/Excel/)
    """
    from src.config import OUTPUT_DIR
    
    if report_type.lower() == 'html':
        output_dir = OUTPUT_DIR / 'HTML'
    elif report_type.lower() == 'excel':
        output_dir = OUTPUT_DIR / 'Excel'
    else:
        output_dir = OUTPUT_DIR
    
    # Crear directorio si no existe
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return output_dir


def open_file_or_folder(path: Path) -> bool:
    """
    Abrir archivo o carpeta con aplicación por defecto del sistema
    
    Args:
        path: Ruta al archivo o carpeta
    
    Returns:
        True si se abrió correctamente, False si hubo error
    """
    try:
        if not path.exists():
            print(f"⚠️  Ruta no existe: {path}")
            return False
        
        # Windows
        os.startfile(str(path))
        return True
    except AttributeError:
        # Linux/Mac
        try:
            if path.is_dir():
                subprocess.run(['xdg-open', str(path)], check=True)
            else:
                subprocess.run(['xdg-open', str(path)], check=True)
            return True
        except Exception as e:
            print(f"❌ Error al abrir {path}: {e}")
            return False
    except Exception as e:
        print(f"❌ Error al abrir {path}: {e}")
        return False


def get_report_path_from_db(analysis_id: int, report_type: str) -> Optional[Path]:
    """
    Obtener ruta de reporte desde la base de datos
    
    Args:
        analysis_id: ID del análisis
        report_type: 'html' o 'excel'
    
    Returns:
        Path al reporte o None si no existe
    """
    from src.database.metrics_db import get_metrics_db
    
    try:
        db = get_metrics_db()
        analysis = db.get_analysis_by_id(analysis_id)
        db.close()
        
        if not analysis:
            return None
        
        if report_type.lower() == 'html':
            path_str = analysis.get('html_report_path')
        elif report_type.lower() == 'excel':
            path_str = analysis.get('excel_report_path')
        else:
            return None
        
        if path_str:
            path = Path(path_str)
            if path.exists():
                return path
        
        return None
    except Exception as e:
        print(f"❌ Error al obtener ruta de reporte: {e}")
        return None


def update_analysis_report_paths(analysis_id: int, html_path: Optional[Path] = None, 
                                 excel_path: Optional[Path] = None) -> bool:
    """
    Actualizar rutas de reportes en la base de datos
    
    Args:
        analysis_id: ID del análisis
        html_path: Ruta al reporte HTML (opcional)
        excel_path: Ruta al reporte Excel (opcional)
    
    Returns:
        True si se actualizó correctamente
    """
    from src.database.metrics_db import get_metrics_db
    
    try:
        db = get_metrics_db()
        cursor = db.conn.cursor()
        
        if html_path:
            cursor.execute('''
                UPDATE analysis_history 
                SET html_report_path = ? 
                WHERE id = ?
            ''', (str(html_path), analysis_id))
        
        if excel_path:
            cursor.execute('''
                UPDATE analysis_history 
                SET excel_report_path = ? 
                WHERE id = ?
            ''', (str(excel_path), analysis_id))
        
        db.conn.commit()
        db.close()
        return True
    except Exception as e:
        print(f"❌ Error al actualizar rutas de reportes: {e}")
        return False
