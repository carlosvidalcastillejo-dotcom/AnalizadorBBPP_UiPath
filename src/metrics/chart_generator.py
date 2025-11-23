"""
Generador de Gráficos para Métricas
Crea visualizaciones de evolución y comparativas
"""

import matplotlib
matplotlib.use('Agg')  # Backend sin GUI para generar imágenes
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


class ChartGenerator:
    """Generador de gráficos para métricas"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Inicializar generador
        
        Args:
            output_dir: Directorio para guardar gráficos
        """
        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent / 'output' / 'charts'
        
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar estilo
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # Colores corporativos NTT Data
        self.NTT_BLUE = '#0067B1'
        self.NTT_LIGHT_BLUE = '#00A3E0'
        self.NTT_GRAY = '#58595B'
    
    def generate_score_evolution(self, evolution_data: List[Dict], 
                                 project_name: str) -> Path:
        """
        Generar gráfico de evolución de score
        
        Args:
            evolution_data: Lista con datos de evolución
            project_name: Nombre del proyecto
            
        Returns:
            Ruta al archivo de imagen generado
        """
        if not evolution_data:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Extraer datos
        dates = [datetime.fromisoformat(d['date']) for d in evolution_data]
        scores = [d['score'] for d in evolution_data]
        versions = [d.get('version', '') for d in evolution_data]
        
        # Gráfico de línea
        ax.plot(dates, scores, marker='o', linewidth=2, 
               markersize=8, color=self.NTT_BLUE, label='Score')
        
        # Línea de tendencia
        if len(scores) > 1:
            z = np.polyfit(range(len(scores)), scores, 1)
            p = np.poly1d(z)
            ax.plot(dates, p(range(len(scores))), "--", 
                   color=self.NTT_LIGHT_BLUE, alpha=0.7, label='Tendencia')
        
        # Configurar ejes
        ax.set_xlabel('Fecha', fontsize=12)
        ax.set_ylabel('Score (0-100)', fontsize=12)
        ax.set_title(f'Evolución de Score - {project_name}', 
                    fontsize=14, fontweight='bold')
        
        # Formato de fechas
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        plt.xticks(rotation=45)
        
        # Grid
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 105)
        
        # Leyenda
        ax.legend(loc='best')
        
        # Ajustar layout
        plt.tight_layout()
        
        # Guardar
        filename = f'score_evolution_{project_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def generate_findings_distribution(self, severity_data: Dict, 
                                       project_name: str) -> Path:
        """
        Generar gráfico de distribución por severidad
        
        Args:
            severity_data: Diccionario con conteos por severidad
            project_name: Nombre del proyecto
            
        Returns:
            Ruta al archivo de imagen generado
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Datos
        severities = ['Critical', 'High', 'Medium', 'Low']
        counts = [
            severity_data.get('critical', 0),
            severity_data.get('high', 0),
            severity_data.get('medium', 0),
            severity_data.get('low', 0)
        ]
        
        # Colores por severidad
        colors = ['#DC3545', '#FD7E14', '#FFC107', '#28A745']
        
        # Gráfico de barras
        bars = ax.bar(severities, counts, color=colors, alpha=0.8)
        
        # Añadir valores en las barras
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Configurar ejes
        ax.set_xlabel('Severidad', fontsize=12)
        ax.set_ylabel('Número de Hallazgos', fontsize=12)
        ax.set_title(f'Distribución de Hallazgos por Severidad - {project_name}',
                    fontsize=14, fontweight='bold')
        
        # Grid
        ax.grid(True, axis='y', alpha=0.3)
        
        # Ajustar layout
        plt.tight_layout()
        
        # Guardar
        filename = f'findings_distribution_{project_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def generate_comparison_chart(self, comparison_data: Dict, 
                                  project_name: str) -> Path:
        """
        Generar gráfico comparativo entre dos análisis
        
        Args:
            comparison_data: Datos de comparación
            project_name: Nombre del proyecto
            
        Returns:
            Ruta al archivo de imagen generado
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Datos
        analysis1 = comparison_data['analysis1']
        analysis2 = comparison_data['analysis2']
        diffs = comparison_data['differences']
        
        # Gráfico 1: Comparación de scores
        versions = [analysis1.get('version', 'V1'), analysis2.get('version', 'V2')]
        scores = [analysis1['score'], analysis2['score']]
        
        bars1 = ax1.bar(versions, scores, color=[self.NTT_GRAY, self.NTT_BLUE], alpha=0.8)
        
        # Añadir valores
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        ax1.set_ylabel('Score', fontsize=12)
        ax1.set_title('Comparación de Scores', fontsize=13, fontweight='bold')
        ax1.set_ylim(0, 105)
        ax1.grid(True, axis='y', alpha=0.3)
        
        # Gráfico 2: Diferencias por severidad
        severities = ['Critical', 'High', 'Medium', 'Low']
        differences = [
            diffs['critical_diff'],
            diffs['high_diff'],
            diffs['medium_diff'],
            diffs['low_diff']
        ]
        
        colors = ['#DC3545' if d > 0 else '#28A745' for d in differences]
        bars2 = ax2.barh(severities, differences, color=colors, alpha=0.8)
        
        # Añadir valores
        for i, bar in enumerate(bars2):
            width = bar.get_width()
            if width != 0:
                ax2.text(width, bar.get_y() + bar.get_height()/2.,
                        f'{int(width):+d}',
                        ha='left' if width > 0 else 'right',
                        va='center', fontsize=11, fontweight='bold')
        
        ax2.set_xlabel('Diferencia (+ = más hallazgos)', fontsize=12)
        ax2.set_title('Cambios por Severidad', fontsize=13, fontweight='bold')
        ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
        ax2.grid(True, axis='x', alpha=0.3)
        
        # Título general
        fig.suptitle(f'Comparación de Análisis - {project_name}',
                    fontsize=15, fontweight='bold', y=1.02)
        
        # Ajustar layout
        plt.tight_layout()
        
        # Guardar
        filename = f'comparison_{project_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath


# Importar numpy solo si está disponible
try:
    import numpy as np
except ImportError:
    # Fallback simple si numpy no está disponible
    class np:
        @staticmethod
        def polyfit(x, y, deg):
            return [0, sum(y)/len(y)]
        
        @staticmethod
        def poly1d(coeffs):
            return lambda x: coeffs[1]


def create_chart_generator(output_dir: Optional[Path] = None):
    """
    Crear instancia de generador de gráficos
    
    Args:
        output_dir: Directorio para guardar gráficos
        
    Returns:
        Instancia de ChartGenerator
    """
    return ChartGenerator(output_dir)
