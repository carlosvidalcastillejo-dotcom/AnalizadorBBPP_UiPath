"""
Calculadora de Métricas
Calcula métricas avanzadas y tendencias a partir del historial de análisis
"""

from typing import List, Dict, Optional
from pathlib import Path


class MetricsCalculator:
    """Calculadora de métricas y estadísticas avanzadas"""
    
    def __init__(self, db):
        """
        Inicializar calculadora
        
        Args:
            db: Instancia de MetricsDatabase
        """
        self.db = db
    
    def calculate_density(self, analysis_data: Dict) -> float:
        """
        Calcular densidad de hallazgos (hallazgos por 100 líneas de código)
        
        Args:
            analysis_data: Datos del análisis
            
        Returns:
            Densidad de hallazgos
        """
        total_findings = analysis_data.get('total_findings', 0)
        total_files = analysis_data.get('total_files', 1)
        
        # Estimación: ~100 líneas por archivo XAML promedio
        estimated_lines = total_files * 100
        
        if estimated_lines == 0:
            return 0.0
        
        density = (total_findings / estimated_lines) * 100
        return round(density, 2)
    
    def calculate_trend(self, project_name: str, limit: int = 10) -> Dict:
        """
        Calcular tendencia de score
        
        Args:
            project_name: Nombre del proyecto
            limit: Número de análisis a considerar
            
        Returns:
            Diccionario con tendencia
        """
        history = self.db.get_analysis_history(project_name, limit)
        
        if len(history) < 2:
            return {
                'trend': 'insufficient_data',
                'direction': 0,
                'average_change': 0
            }
        
        # Ordenar por fecha (más antiguo primero)
        history.sort(key=lambda x: x['analysis_date'])
        
        # Calcular cambios entre análisis consecutivos
        changes = []
        for i in range(1, len(history)):
            change = history[i]['score'] - history[i-1]['score']
            changes.append(change)
        
        avg_change = sum(changes) / len(changes) if changes else 0
        
        # Determinar tendencia
        if avg_change > 1:
            trend = 'improving'
            direction = 1
        elif avg_change < -1:
            trend = 'declining'
            direction = -1
        else:
            trend = 'stable'
            direction = 0
        
        return {
            'trend': trend,
            'direction': direction,
            'average_change': round(avg_change, 2),
            'total_change': round(history[-1]['score'] - history[0]['score'], 2),
            'analyses_count': len(history)
        }
    
    def calculate_improvement_ratio(self, analysis_id1: int, analysis_id2: int) -> Dict:
        """
        Calcular ratio de mejora entre dos análisis
        
        Args:
            analysis_id1: ID del análisis base (más antiguo)
            analysis_id2: ID del análisis comparado (más reciente)
            
        Returns:
            Diccionario con ratios de mejora
        """
        comparison = self.db.compare_analyses(analysis_id1, analysis_id2)
        
        if not comparison:
            return {}
        
        analysis1 = comparison['analysis1']
        analysis2 = comparison['analysis2']
        diffs = comparison['differences']
        
        # Calcular porcentajes de mejora
        score_improvement = 0
        if analysis1['score'] > 0:
            score_improvement = (diffs['score_diff'] / analysis1['score']) * 100
        
        return {
            'score_improvement_percent': round(score_improvement, 2),
            'score_improvement_points': round(diffs['score_diff'], 2),
            'findings_reduction': -diffs['findings_diff'],  # Negativo = mejora
            'critical_reduction': -diffs['critical_diff'],
            'high_reduction': -diffs['high_diff']
        }
    
    def get_top_violated_rules(self, project_name: str, limit: int = 10) -> List[Dict]:
        """
        Obtener reglas más violadas
        
        Args:
            project_name: Nombre del proyecto
            limit: Número de reglas a retornar
            
        Returns:
            Lista de reglas con conteos
        """
        # Obtener análisis recientes
        history = self.db.get_analysis_history(project_name, limit=5)
        
        if not history:
            return []
        
        # Contar violaciones por regla
        rule_counts = {}
        
        for analysis in history:
            analysis_full = self.db.get_analysis_by_id(analysis['id'])
            if not analysis_full:
                continue
            
            for finding in analysis_full.get('findings', []):
                rule_id = finding.get('rule_id', 'unknown')
                rule_name = finding.get('rule_name', 'Unknown Rule')
                
                if rule_id not in rule_counts:
                    rule_counts[rule_id] = {
                        'rule_id': rule_id,
                        'rule_name': rule_name,
                        'count': 0,
                        'severity': finding.get('severity', 'MEDIUM')
                    }
                
                rule_counts[rule_id]['count'] += 1
        
        # Ordenar por conteo
        sorted_rules = sorted(
            rule_counts.values(),
            key=lambda x: x['count'],
            reverse=True
        )
        
        return sorted_rules[:limit]
    
    def get_problematic_files(self, analysis_id: int, limit: int = 10) -> List[Dict]:
        """
        Obtener archivos con más problemas
        
        Args:
            analysis_id: ID del análisis
            limit: Número de archivos a retornar
            
        Returns:
            Lista de archivos con conteos
        """
        analysis = self.db.get_analysis_by_id(analysis_id)
        
        if not analysis:
            return []
        
        # Contar hallazgos por archivo
        file_counts = {}
        
        for finding in analysis.get('findings', []):
            file_path = finding.get('file_path', 'unknown')
            
            if file_path not in file_counts:
                file_counts[file_path] = {
                    'file_path': file_path,
                    'total_findings': 0,
                    'critical': 0,
                    'high': 0,
                    'medium': 0,
                    'low': 0
                }
            
            file_counts[file_path]['total_findings'] += 1
            
            severity = finding.get('severity', 'MEDIUM').lower()
            if severity in file_counts[file_path]:
                file_counts[file_path][severity] += 1
        
        # Ordenar por total de hallazgos
        sorted_files = sorted(
            file_counts.values(),
            key=lambda x: x['total_findings'],
            reverse=True
        )
        
        return sorted_files[:limit]
    
    def calculate_category_distribution(self, analysis_id: int) -> Dict:
        """
        Calcular distribución de hallazgos por categoría
        
        Args:
            analysis_id: ID del análisis
            
        Returns:
            Diccionario con distribución por categoría
        """
        analysis = self.db.get_analysis_by_id(analysis_id)
        
        if not analysis:
            return {}
        
        categories = {}
        
        for finding in analysis.get('findings', []):
            category = finding.get('category', 'Other')
            
            if category not in categories:
                categories[category] = {
                    'count': 0,
                    'critical': 0,
                    'high': 0,
                    'medium': 0,
                    'low': 0
                }
            
            categories[category]['count'] += 1
            
            severity = finding.get('severity', 'MEDIUM').lower()
            if severity in categories[category]:
                categories[category][severity] += 1
        
        return categories
    
    def get_score_evolution(self, project_name: str, limit: int = 20) -> List[Dict]:
        """
        Obtener evolución de score
        
        Args:
            project_name: Nombre del proyecto
            limit: Número de análisis a incluir
            
        Returns:
            Lista con evolución de score
        """
        history = self.db.get_analysis_history(project_name, limit)
        
        # Ordenar por fecha
        history.sort(key=lambda x: x['analysis_date'])
        
        evolution = []
        for analysis in history:
            evolution.append({
                'date': analysis['analysis_date'],
                'version': analysis.get('version', ''),
                'score': analysis['score'],
                'total_findings': analysis['total_findings']
            })
        
        return evolution
    
    def calculate_all_metrics(self, analysis_id: int) -> Dict:
        """
        Calcular todas las métricas para un análisis
        
        Args:
            analysis_id: ID del análisis
            
        Returns:
            Diccionario con todas las métricas
        """
        analysis = self.db.get_analysis_by_id(analysis_id)
        
        if not analysis:
            return {}
        
        metrics = {
            'basic': {
                'score': analysis['score'],
                'total_findings': analysis['total_findings'],
                'analyzed_files': analysis['analyzed_files']
            },
            'density': self.calculate_density(analysis),
            'category_distribution': self.calculate_category_distribution(analysis_id),
            'problematic_files': self.get_problematic_files(analysis_id, 5),
            'severity_breakdown': {
                'critical': analysis['critical_findings'],
                'high': analysis['high_findings'],
                'medium': analysis['medium_findings'],
                'low': analysis['low_findings']
            }
        }
        
        return metrics


def create_metrics_calculator(db):
    """
    Crear instancia de calculadora de métricas
    
    Args:
        db: Instancia de MetricsDatabase
        
    Returns:
        Instancia de MetricsCalculator
    """
    return MetricsCalculator(db)
