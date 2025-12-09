"""
Sistema de Base de Datos para Métricas
Gestiona el almacenamiento y recuperación de análisis históricos en SQLite
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class MetricsDatabase:
    """Gestor de base de datos SQLite para métricas de análisis"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Inicializar conexión a base de datos
        
        Args:
            db_path: Ruta al archivo de base de datos (si None, usa ruta por defecto)
        """
        if db_path is None:
            # Crear carpeta data si no existe
            data_dir = Path(__file__).parent.parent.parent / 'data'
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / 'metrics.db'
        
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._init_database()
    
    def _connect(self):
        """Establecer conexión a la base de datos"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
    
    def _init_database(self):
        """Crear tablas si no existen"""
        cursor = self.conn.cursor()
        
        # Tabla principal de historial de análisis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                project_path TEXT NOT NULL,
                analysis_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                version TEXT,
                total_files INTEGER,
                analyzed_files INTEGER,
                total_findings INTEGER,
                critical_findings INTEGER,
                high_findings INTEGER,
                medium_findings INTEGER,
                low_findings INTEGER,
                score REAL,
                execution_time REAL,
                metadata TEXT,
                html_report_path TEXT,
                excel_report_path TEXT
            )
        ''')
        
        # Migración: Añadir columnas si no existen (para BDs existentes)
        self._migrate_add_report_paths()
        
        # Tabla de detalles de hallazgos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS findings_detail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                rule_id TEXT,
                rule_name TEXT,
                severity TEXT,
                category TEXT,
                file_path TEXT,
                location TEXT,
                description TEXT,
                FOREIGN KEY (analysis_id) REFERENCES analysis_history(id) ON DELETE CASCADE
            )
        ''')
        
        # Tabla de métricas resumidas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                metric_name TEXT,
                metric_value REAL,
                metric_unit TEXT,
                FOREIGN KEY (analysis_id) REFERENCES analysis_history(id) ON DELETE CASCADE
            )
        ''')
        
        # Índices para mejorar rendimiento
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_project_name 
            ON analysis_history(project_name)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_analysis_date 
            ON analysis_history(analysis_date DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_findings_analysis 
            ON findings_detail(analysis_id)
        ''')
        
        self.conn.commit()
    
    def _migrate_add_report_paths(self):
        """Migración: Añadir columnas de rutas de reportes si no existen"""
        cursor = self.conn.cursor()
        
        try:
            # Verificar si las columnas ya existen
            cursor.execute("PRAGMA table_info(analysis_history)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Añadir html_report_path si no existe
            if 'html_report_path' not in columns:
                cursor.execute('''
                    ALTER TABLE analysis_history 
                    ADD COLUMN html_report_path TEXT
                ''')
                print("✅ Columna 'html_report_path' añadida a la base de datos")
            
            # Añadir excel_report_path si no existe
            if 'excel_report_path' not in columns:
                cursor.execute('''
                    ALTER TABLE analysis_history 
                    ADD COLUMN excel_report_path TEXT
                ''')
                print("✅ Columna 'excel_report_path' añadida a la base de datos")
            
            # Añadir bbpp_sets si no existe
            if 'bbpp_sets' not in columns:
                cursor.execute('''
                    ALTER TABLE analysis_history 
                    ADD COLUMN bbpp_sets TEXT
                ''')
                print("✅ Columna 'bbpp_sets' añadida a la base de datos")
            
            self.conn.commit()
        except Exception as e:
            print(f"⚠️  Error en migración de BD: {e}")
    
    
    def save_analysis(self, analysis_data: Dict) -> int:
        """
        Guardar resultado de análisis en la base de datos
        
        Args:
            analysis_data: Diccionario con datos del análisis
            
        Returns:
            ID del análisis guardado
        """
        cursor = self.conn.cursor()
        
        # Extraer datos principales
        project_name = Path(analysis_data.get('project_path', '')).name
        
        # Extraer versión de Studio desde project_info
        project_info = analysis_data.get('project_info', {})
        studio_version = project_info.get('studio_version', 'Unknown')
        
        # Mapeo de severidades: analyzer → metrics
        # error → HIGH, warning → MEDIUM, info → LOW
        severity_map = {
            'error': 'HIGH',
            'warning': 'MEDIUM',
            'info': 'LOW'
        }
        
        # Contar hallazgos por severidad
        findings = analysis_data.get('findings', [])
        severity_counts = {
            'CRITICAL': 0,  # Reservado para futuros errores críticos
            'HIGH': 0,      # Errores
            'MEDIUM': 0,    # Warnings
            'LOW': 0        # Info
        }
        
        for finding in findings:
            # Obtener severidad del analyzer (error/warning/info)
            analyzer_severity = finding.get('severity', 'info').lower()
            # Mapear a severidad de métricas (HIGH/MEDIUM/LOW)
            metrics_severity = severity_map.get(analyzer_severity, 'LOW')
            
            if metrics_severity in severity_counts:
                severity_counts[metrics_severity] += 1
        
        # Preparar metadata como JSON
        metadata = {
            'bbpp_sets': analysis_data.get('bbpp_sets', []),
            'config': analysis_data.get('config', {}),
            'statistics': analysis_data.get('statistics', {})
        }
        
        # Extraer conjuntos de BBPP para columna dedicada
        bbpp_sets = analysis_data.get('bbpp_sets', [])
        bbpp_sets_str = ', '.join(bbpp_sets) if bbpp_sets else 'N/A'
        
        # Insertar análisis principal
        cursor.execute('''
            INSERT INTO analysis_history (
                project_name, project_path, version, bbpp_sets,
                total_files, analyzed_files, total_findings,
                critical_findings, high_findings, medium_findings, low_findings,
                score, execution_time, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            project_name,
            analysis_data.get('project_path', ''),
            studio_version,  # Usar versión de Studio extraída
            bbpp_sets_str,  # Conjuntos de BBPP utilizados
            analysis_data.get('total_files', 0),
            analysis_data.get('analyzed_files', 0),
            len(findings),
            severity_counts['CRITICAL'],
            severity_counts['HIGH'],
            severity_counts['MEDIUM'],
            severity_counts['LOW'],
            analysis_data.get('score', {}).get('score', 0),
            analysis_data.get('execution_time', 0),
            json.dumps(metadata, ensure_ascii=False)
        ))
        
        analysis_id = cursor.lastrowid
        
        # Guardar detalles de hallazgos (limitado a primeros 1000 para no saturar BD)
        for finding in findings[:1000]:
            cursor.execute('''
                INSERT INTO findings_detail (
                    analysis_id, rule_id, rule_name, severity,
                    category, file_path, location, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_id,
                finding.get('rule_id', ''),
                finding.get('rule_name', ''),
                finding.get('severity', 'MEDIUM'),
                finding.get('category', ''),
                finding.get('file', ''),
                finding.get('location', ''),
                finding.get('description', '')
            ))
        
        self.conn.commit()
        return analysis_id
    
    def get_unique_projects(self) -> List[str]:
        """
        Obtener lista de nombres de proyectos únicos
        
        Returns:
            Lista de nombres de proyectos
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT DISTINCT project_name FROM analysis_history ORDER BY project_name')
        return [row[0] for row in cursor.fetchall()]
    
    def get_analysis_history(self, project_name: Optional[str] = None, 
                            limit: int = 100) -> List[Dict]:
        """
        Obtener historial de análisis
        
        Args:
            project_name: Filtrar por nombre de proyecto (None = todos)
            limit: Número máximo de resultados
            
        Returns:
            Lista de análisis
        """
        cursor = self.conn.cursor()
        
        if project_name:
            cursor.execute('''
                SELECT * FROM analysis_history 
                WHERE project_name = ?
                ORDER BY analysis_date DESC 
                LIMIT ?
            ''', (project_name, limit))
        else:
            cursor.execute('''
                SELECT * FROM analysis_history 
                ORDER BY analysis_date DESC 
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        
        # Convertir a lista de diccionarios
        results = []
        for row in rows:
            analysis = dict(row)
            # Parsear metadata JSON
            if analysis['metadata']:
                try:
                    analysis['metadata'] = json.loads(analysis['metadata'])
                except:
                    analysis['metadata'] = {}
            results.append(analysis)
        
        return results
    
    def get_analysis_by_id(self, analysis_id: int) -> Optional[Dict]:
        """
        Obtener análisis específico por ID
        
        Args:
            analysis_id: ID del análisis
            
        Returns:
            Diccionario con datos del análisis o None
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT * FROM analysis_history WHERE id = ?
        ''', (analysis_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return None
        
        analysis = dict(row)
        
        # Parsear metadata
        if analysis['metadata']:
            try:
                analysis['metadata'] = json.loads(analysis['metadata'])
            except:
                analysis['metadata'] = {}
        
        # Obtener hallazgos
        cursor.execute('''
            SELECT * FROM findings_detail WHERE analysis_id = ?
        ''', (analysis_id,))
        
        findings = [dict(row) for row in cursor.fetchall()]
        analysis['findings'] = findings
        
        return analysis
    
    def get_project_stats(self, project_name: str) -> Dict:
        """
        Obtener estadísticas de un proyecto
        
        Args:
            project_name: Nombre del proyecto
            
        Returns:
            Diccionario con estadísticas
        """
        cursor = self.conn.cursor()
        
        # Estadísticas generales
        cursor.execute('''
            SELECT 
                COUNT(*) as total_analyses,
                AVG(score) as avg_score,
                MIN(score) as min_score,
                MAX(score) as max_score,
                AVG(total_findings) as avg_findings
            FROM analysis_history
            WHERE project_name = ?
        ''', (project_name,))
        
        stats = dict(cursor.fetchone())
        
        # Último análisis
        cursor.execute('''
            SELECT * FROM analysis_history
            WHERE project_name = ?
            ORDER BY analysis_date DESC
            LIMIT 1
        ''', (project_name,))
        
        last_analysis = cursor.fetchone()
        if last_analysis:
            stats['last_analysis'] = dict(last_analysis)
        
        return stats
    
    def compare_analyses(self, analysis_id1: int, analysis_id2: int) -> Dict:
        """
        Comparar dos análisis
        
        Args:
            analysis_id1: ID del primer análisis
            analysis_id2: ID del segundo análisis
            
        Returns:
            Diccionario con comparación
        """
        analysis1 = self.get_analysis_by_id(analysis_id1)
        analysis2 = self.get_analysis_by_id(analysis_id2)
        
        if not analysis1 or not analysis2:
            return {}
        
        comparison = {
            'analysis1': {
                'id': analysis1['id'],
                'date': analysis1['analysis_date'],
                'version': analysis1['version'],
                'score': analysis1['score']
            },
            'analysis2': {
                'id': analysis2['id'],
                'date': analysis2['analysis_date'],
                'version': analysis2['version'],
                'score': analysis2['score']
            },
            'differences': {
                'score_diff': analysis2['score'] - analysis1['score'],
                'findings_diff': analysis2['total_findings'] - analysis1['total_findings'],
                'critical_diff': analysis2['critical_findings'] - analysis1['critical_findings'],
                'high_diff': analysis2['high_findings'] - analysis1['high_findings'],
                'medium_diff': analysis2['medium_findings'] - analysis1['medium_findings'],
                'low_diff': analysis2['low_findings'] - analysis1['low_findings']
            }
        }
        
        return comparison
    
    def delete_analysis(self, analysis_id: int) -> bool:
        """
        Eliminar análisis
        
        Args:
            analysis_id: ID del análisis a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            DELETE FROM analysis_history WHERE id = ?
        ''', (analysis_id,))
        
        self.conn.commit()
        return cursor.rowcount > 0
    
    def cleanup_old_analyses(self, project_name: str, keep_last: int = 50) -> int:
        """
        Limpiar análisis antiguos, manteniendo los últimos N
        
        Args:
            project_name: Nombre del proyecto
            keep_last: Número de análisis a mantener
            
        Returns:
            Número de análisis eliminados
        """
        cursor = self.conn.cursor()
        
        # Obtener IDs a eliminar
        cursor.execute('''
            SELECT id FROM analysis_history
            WHERE project_name = ?
            ORDER BY analysis_date DESC
            LIMIT -1 OFFSET ?
        ''', (project_name, keep_last))
        
        ids_to_delete = [row[0] for row in cursor.fetchall()]
        
        if not ids_to_delete:
            return 0
        
        # Eliminar
        placeholders = ','.join('?' * len(ids_to_delete))
        cursor.execute(f'''
            DELETE FROM analysis_history 
            WHERE id IN ({placeholders})
        ''', ids_to_delete)
        
        self.conn.commit()
        return cursor.rowcount
    
    def close(self):
        """Cerrar conexión a la base de datos"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Función helper para obtener instancia de BD
def get_metrics_db() -> MetricsDatabase:
    """
    Obtener instancia de base de datos de métricas
    
    Returns:
        Instancia de MetricsDatabase
    """
    return MetricsDatabase()
