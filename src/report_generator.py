"""
Generador de reportes HTML
Crea reportes profesionales con los resultados del análisis
"""

from pathlib import Path
from datetime import datetime
from typing import Dict
import html


class HTMLReportGenerator:
    """Generador de reportes HTML"""
    
    def __init__(self, results: Dict, output_path: Path = None):
        """
        Inicializar generador
        
        Args:
            results: Resultados del análisis (de ProjectScanner)
            output_path: Ruta donde guardar el reporte (opcional)
        """
        self.results = results
        
        # Si no se especifica ruta, usar estructura nueva con nombre estandarizado
        if output_path is None:
            from src.report_utils import get_report_output_dir, generate_report_filename
            project_name = results.get('project_info', {}).get('name', 'Proyecto')
            output_dir = get_report_output_dir('html')
            filename = generate_report_filename(project_name, 'html')
            self.output_path = output_dir / filename
        else:
            self.output_path = output_path
        
    def generate(self) -> Path:
        """
        Generar reporte HTML
        
        Returns:
            Ruta al archivo generado
        """
        html_content = self._build_html()
        
        # Asegurar que existe el directorio
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Guardar archivo
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return self.output_path
    
    def _build_html(self) -> str:
        """Construir contenido HTML completo"""
        project_info = self.results.get('project_info', {})
        stats = self.results.get('statistics', {})
        score = self.results.get('score', {})
        findings = self.results.get('findings', [])
        
        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Análisis - {html.escape(project_info.get('name', 'Proyecto'))}</title>
    <style>
        {self._get_css()}
    </style>
</head>
<body>
    <div class="container">
        {self._build_header(project_info)}
        {self._build_summary(score, stats)}
        {self._build_dependencies(project_info)}
        {self._build_statistics(stats)}
        {self._build_findings(findings, stats)}
        {self._build_footer()}
    </div>
</body>
</html>"""
        
        return html_content
    
    def _get_css(self) -> str:
        """Obtener estilos CSS"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #0067B1 0%, #00A3E0 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 16px;
            opacity: 0.9;
        }
        
        .summary {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }
        
        .summary-card {
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            text-align: center;
        }
        
        .summary-card h3 {
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
            margin-bottom: 15px;
        }
        
        .score-value {
            font-size: 48px;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .score-A { color: #28a745; }
        .score-B { color: #90ee90; }
        .score-C { color: #ffc107; }
        .score-D { color: #ff9800; }
        .score-F { color: #dc3545; }
        
        .grade {
            font-size: 18px;
            color: #666;
        }
        
        .section {
            padding: 40px;
        }
        
        .section h2 {
            color: #0067B1;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #0067B1;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .stat-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #0067B1;
        }
        
        .stat-label {
            color: #666;
            font-size: 14px;
            margin-bottom: 5px;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: bold;
            color: #333;
        }
        
        .findings-list {
            margin-top: 20px;
        }
        
        .finding-item {
            background: white;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 4px solid #ccc;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        
        .finding-error {
            border-left-color: #dc3545;
        }
        
        .finding-warning {
            border-left-color: #ffc107;
        }
        
        .finding-info {
            border-left-color: #17a2b8;
        }
        
        .finding-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .finding-title {
            font-weight: bold;
            font-size: 16px;
        }
        
        .severity-badge {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .badge-error {
            background: #dc3545;
            color: white;
        }
        
        .badge-warning {
            background: #ffc107;
            color: #333;
        }
        
        .badge-info {
            background: #17a2b8;
            color: white;
        }
        
        .finding-details {
            color: #666;
            font-size: 14px;
            line-height: 1.6;
        }
        
        .finding-location {
            color: #999;
            font-size: 13px;
            margin-top: 10px;
            font-family: 'Courier New', monospace;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #666;
            font-size: 14px;
            border-top: 1px solid #ddd;
        }
        
        .category-summary {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 20px 0;
        }
        
        .category-tag {
            background: #e9ecef;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 14px;
        }
        
        .no-findings {
            text-align: center;
            padding: 40px;
            color: #28a745;
            font-size: 18px;
        }
        """
    
    def _build_header(self, project_info: Dict) -> str:
        """Construir encabezado del reporte"""
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        studio_ver = project_info.get('studio_version', 'Unknown')
        
        return f"""
        <div class="header">
            <h1>📊 Reporte de Análisis de Buenas Prácticas</h1>
            <p>Proyecto: {html.escape(project_info.get('name', 'Unknown'))}</p>
            <p>Tipo: {html.escape(project_info.get('type', 'Unknown'))} | 
               UiPath: {html.escape(studio_ver)} | 
               Generado: {now}</p>
        </div>
        """
    
    def _build_dependencies(self, project_info: Dict) -> str:
        """Construir sección de dependencias"""
        dependencies = project_info.get('dependencies', [])
        
        if not dependencies:
            return ""
        
        deps_html = """
        <div class="section">
            <h2>📦 Dependencias del Proyecto</h2>
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                <thead>
                    <tr style="background: #f8f9fa; border-bottom: 2px solid #0067B1;">
                        <th style="padding: 12px; text-align: left; width: 60%;">Paquete</th>
                        <th style="padding: 12px; text-align: left; width: 40%;">Versión Instalada</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for dep in sorted(dependencies, key=lambda x: x['name']):
            deps_html += f"""
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;">{html.escape(dep['name'])}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; font-family: monospace;">{html.escape(dep['version'])}</td>
                </tr>
            """
        
        deps_html += f"""
                </tbody>
            </table>
            <p style="margin-top: 15px; color: #666; font-size: 14px;">
                Total de paquetes instalados: {len(dependencies)}
            </p>
        </div>
        """
        
        return deps_html
    
    def _build_summary(self, score: Dict, stats: Dict) -> str:
        """Construir resumen ejecutivo"""
        score_value = score.get('score', 0)
        grade = score.get('grade', 'N/A')
        
        # Determinar clase de color basada en el score
        if score_value >= 90:
            score_class = 'score-A'
        elif score_value >= 80:
            score_class = 'score-B'
        elif score_value >= 70:
            score_class = 'score-C'
        elif score_value >= 60:
            score_class = 'score-D'
        else:
            score_class = 'score-F'
        
        return f"""
        <div class="summary">
            <div class="summary-card">
                <h3>Score Global</h3>
                <div class="score-value {score_class}">{score_value}</div>
                <div class="grade">{html.escape(grade)}</div>
            </div>
            <div class="summary-card">
                <h3>Total Hallazgos</h3>
                <div class="score-value">{stats.get('total_findings', 0)}</div>
                <div class="grade">
                    ❌ {stats.get('errors', 0)} | 
                    ⚠️ {stats.get('warnings', 0)} | 
                    ℹ️ {stats.get('infos', 0)}
                </div>
            </div>
            <div class="summary-card">
                <h3>Archivos Analizados</h3>
                <div class="score-value">{self.results.get('analyzed_files', 0)}</div>
                <div class="grade">{self.results.get('total_xaml_files', 0)} archivos XAML</div>
            </div>
        </div>
        """
    
    def _build_statistics(self, stats: Dict) -> str:
        """Construir sección de estadísticas"""
        return f"""
        <div class="section">
            <h2>📈 Estadísticas del Proyecto</h2>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-label">Total Actividades</div>
                    <div class="stat-value">{stats.get('total_activities', 0)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Total Variables</div>
                    <div class="stat-value">{stats.get('total_variables', 0)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Total Argumentos</div>
                    <div class="stat-value">{stats.get('total_arguments', 0)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Bloques Try-Catch</div>
                    <div class="stat-value">{stats.get('total_try_catch', 0)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Mensajes de Log</div>
                    <div class="stat-value">{stats.get('total_logs', 0)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Líneas Comentadas</div>
                    <div class="stat-value">{stats.get('total_commented_lines', 0)}</div>
                </div>
            </div>
            
            <h3 style="margin-top: 30px; margin-bottom: 15px;">Por Categoría:</h3>
            <div class="category-summary">
                {self._build_category_tags(stats.get('by_category', {}))}
            </div>
        </div>
        """
    
    def _build_category_tags(self, by_category: Dict) -> str:
        """Construir tags de categorías"""
        tags_html = ""
        for category, count in sorted(by_category.items()):
            tags_html += f'<div class="category-tag">{html.escape(category)}: {count}</div>\n'
        return tags_html or '<div class="category-tag">Sin hallazgos</div>'
    
    def _build_findings(self, findings: list, stats: Dict) -> str:
        """Construir sección de hallazgos"""
        if not findings:
            return """
            <div class="section">
                <h2>✅ Hallazgos</h2>
                <div class="no-findings">
                    🎉 ¡Excelente! No se encontraron problemas en el proyecto.
                </div>
            </div>
            """
        
        findings_html = """
        <div class="section">
            <h2>🔍 Hallazgos Detallados</h2>
            <div class="findings-list">
        """
        
        for finding in findings:
            severity = finding.get('severity', 'info')
            category = finding.get('category', 'unknown')
            description = finding.get('description', '')
            file_path = Path(finding.get('file_path', '')).name
            location = finding.get('location', '')
            
            severity_class = f'finding-{severity}'
            badge_class = f'badge-{severity}'
            
            findings_html += f"""
            <div class="finding-item {severity_class}">
                <div class="finding-header">
                    <div class="finding-title">
                        [{html.escape(category.upper())}] {html.escape(description)}
                    </div>
                    <span class="severity-badge {badge_class}">{severity}</span>
                </div>
                <div class="finding-details">
                    📄 Archivo: {html.escape(file_path)}
            """
            
            if location:
                findings_html += f"""
                    <br>📍 Ubicación: {html.escape(location)}
                """
            
            findings_html += """
                </div>
            </div>
            """
        
        findings_html += """
            </div>
        </div>
        """
        
        return findings_html
    
    def _build_footer(self) -> str:
        """Construir pie de página"""
        from src.config import APP_VERSION, APP_VERSION_TYPE, APP_AUTHOR, BUILD_DATE
        from datetime import datetime
        
        # Importar branding
        try:
            from src.branding_manager import get_company_name, get_text
            company_name = get_company_name()
            footer_text = get_text('report_footer', author=APP_AUTHOR)
        except ImportError:
            company_name = "Your Company"
            footer_text = f"Desarrollado por {APP_AUTHOR}"
        
        current_year = datetime.now().year
        version_info = f"v{APP_VERSION} {APP_VERSION_TYPE}"
        build_info = f" | Build: {BUILD_DATE}" if BUILD_DATE else ""
        
        return f"""
        <div class="footer">
            <p>Generado por <strong>Analizador de Buenas Prácticas UiPath {version_info}</strong>{build_info}</p>
            <p>{footer_text} | {company_name} | {current_year}</p>
        </div>
        """
