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
    
    def __init__(self, results: Dict, output_path: Path = None, report_type: str = "detallado"):
        """
        Inicializar generador

        Args:
            results: Resultados del análisis (de ProjectScanner)
            output_path: Ruta donde guardar el reporte (opcional)
            report_type: Tipo de reporte ('detallado' o 'normal')
        """
        self.results = results
        self.report_type = report_type
        
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
        """Construir contenido HTML completo según el tipo de reporte"""
        if self.report_type == "detallado":
            return self._build_html_detallado()
        else:
            return self._build_html_normal()

    def _build_html_detallado(self) -> str:
        """Construir reporte HTML detallado con pestañas, filtros y scores por archivo"""
        project_info = self.results.get('project_info', {})
        stats = self.results.get('statistics', {})
        score = self.results.get('score', {})
        findings = self.results.get('findings', [])
        
        # Preparar botón IA condicional (Mostrar siempre que haya datos, incluso error)
        ai_data = self.results.get('ai_analysis')
        ai_button_html = ""
        if ai_data:
            state_icon = "⚠️" if ai_data.get('error') else "🤖"
            ai_button_html = f'<button class="tab-button" onclick="switchTab(\'tab-ia\')">{state_icon} Análisis IA</button>'

        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Análisis - {html.escape(project_info.get('name', 'Proyecto'))}</title>
    <style>
        {self._get_css()}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script>
        // Función para colapsar/expandir hallazgos
        function toggleFinding(findingId) {{
            const content = document.getElementById(findingId);
            const icon = document.getElementById('icon-' + findingId);

            if (content.style.display === 'none') {{
                content.style.display = 'block';
                icon.textContent = '▼';
            }} else {{
                content.style.display = 'none';
                icon.textContent = '▶';
            }}
        }}

        // Función para colapsar/expandir todos
        function toggleAll(expand) {{
            const allContents = document.querySelectorAll('.collapsible-content');
            const allIcons = document.querySelectorAll('.toggle-icon');

            allContents.forEach(content => {{
                content.style.display = expand ? 'block' : 'none';
            }});

            allIcons.forEach(icon => {{
                icon.textContent = expand ? '▼' : '▶';
            }});
        }}

        // Función para aplicar filtros
        function applyFilters() {{
            // Obtener severidades seleccionadas
            const selectedSeverities = Array.from(
                document.querySelectorAll('.severity-filter:checked')
            ).map(cb => cb.value);

            // Obtener categorías seleccionadas
            const selectedCategories = Array.from(
                document.querySelectorAll('.category-filter:checked')
            ).map(cb => cb.value);

            // Filtrar hallazgos
            const allFindings = document.querySelectorAll('.finding-item');
            let visibleCount = 0;

            allFindings.forEach(finding => {{
                const severity = finding.getAttribute('data-severity');
                const category = finding.getAttribute('data-category');

                const severityMatch = selectedSeverities.includes(severity);
                const categoryMatch = selectedCategories.includes(category);

                if (severityMatch && categoryMatch) {{
                    finding.style.display = 'block';
                    visibleCount++;
                }} else {{
                    finding.style.display = 'none';
                }}
            }});

            // Mostrar contador de hallazgos visibles
            updateVisibleCount(visibleCount, allFindings.length);
        }}

        // Función para resetear filtros
        function resetFilters() {{
            // Marcar todos los checkboxes
            document.querySelectorAll('.severity-filter, .category-filter').forEach(cb => {{
                cb.checked = true;
            }});

            // Aplicar filtros (mostrar todos)
            applyFilters();
        }}

        // Función para actualizar contador de hallazgos visibles
        function updateVisibleCount(visible, total) {{
            let countElement = document.getElementById('visible-count');
            if (!countElement) {{
                // Crear elemento si no existe
                const filtersPanel = document.querySelector('.filters-panel');
                if (filtersPanel) {{
                    countElement = document.createElement('div');
                    countElement.id = 'visible-count';
                    countElement.style.cssText = 'text-align: center; padding: 10px; background: #e3f2fd; border-radius: 5px; margin-top: 10px; font-weight: bold; color: #0067B1;';
                    filtersPanel.appendChild(countElement);
                }}
            }}

            if (countElement) {{
                if (visible === total) {{
                    countElement.textContent = `Mostrando todos los hallazgos (${{total}})`;
                }} else {{
                    countElement.textContent = `Mostrando ${{visible}} de ${{total}} hallazgos`;
                }}
            }}
        }}

        // Función para colapsar/expandir el panel de filtros
        function toggleFiltersPanel() {{
            const content = document.getElementById('filters-content');
            const icon = document.getElementById('icon-filters');

            if (content.style.display === 'none') {{
                content.style.display = 'grid';
                icon.textContent = '▼';
            }} else {{
                content.style.display = 'none';
                icon.textContent = '▶';
            }}
        }}
        // Función para cambiar de pestaña
        function switchTab(tabName) {{
            // Ocultar todas las pestañas
            const tabs = document.querySelectorAll('.tab-content');
            tabs.forEach(tab => tab.style.display = 'none');

            // Desactivar todos los botones
            const buttons = document.querySelectorAll('.tab-button');
            buttons.forEach(btn => btn.classList.remove('active'));

            // Mostrar pestaña seleccionada
            const selectedTab = document.getElementById(tabName);
            if (selectedTab) {{
                selectedTab.style.display = 'block';
            }}

            // Activar botón seleccionado
            const selectedButton = document.querySelector(`[onclick="switchTab('${{tabName}}')"]`);
            if (selectedButton) {{
                selectedButton.classList.add('active');
            }}
        }}
    </script>
</head>
<body>
    <div class="container">
        {self._build_header(project_info)}

        <!-- Sistema de Pestañas -->
        <div class="tabs-container">
            <div class="tabs-header">
                <button class="tab-button active" onclick="switchTab('tab-resumen')">📊 Resumen</button>
                <button class="tab-button" onclick="switchTab('tab-hallazgos')">📄 Hallazgos</button>
                <button class="tab-button" onclick="switchTab('tab-archivos')">📂 Archivos</button>
                <button class="tab-button" onclick="switchTab('tab-graficos')">📈 Gráficos</button>
                {ai_button_html}
            </div>

            <!-- Pestaña: Resumen -->
            <div id="tab-resumen" class="tab-content" style="display: block;">
                {self._build_summary(score, stats)}
                {self._build_dependencies(project_info)}
                {self._build_version_validation()}
                {self._build_statistics(stats)}
            </div>

            <!-- Pestaña: Hallazgos -->
            <div id="tab-hallazgos" class="tab-content" style="display: none;">
                {self._build_findings(findings, stats)}
            </div>

            <!-- Pestaña: Archivos -->
            <div id="tab-archivos" class="tab-content" style="display: none;">
                {self._build_files_scores(findings)}
            </div>

            <!-- Pestaña: Gráficos -->
            <div id="tab-graficos" class="tab-content" style="display: none;">
                {self._build_charts(findings, stats, score)}
            </div>
            
            <!-- Pestaña: Análisis IA (Condicional) -->
            {self._build_ai_tab(self.results.get('ai_analysis'))}
        </div>

        {self._build_footer()}
    </div>
</body>
</html>"""
        
        return html_content

    def _build_html_normal(self) -> str:
        """Construir reporte HTML simple sin pestañas (formato clásico)"""
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
        {self._get_css_normal()}
    </style>
    <script>
        // Función para colapsar/expandir hallazgos
        function toggleFinding(findingId) {{
            const content = document.getElementById(findingId);
            const icon = document.getElementById('icon-' + findingId);

            if (content.style.display === 'none') {{
                content.style.display = 'block';
                icon.textContent = '▼';
            }} else {{
                content.style.display = 'none';
                icon.textContent = '▶';
            }}
        }}

        // Función para colapsar/expandir todos
        function toggleAll(expand) {{
            const allContents = document.querySelectorAll('.collapsible-content');
            const allIcons = document.querySelectorAll('.toggle-icon');

            allContents.forEach(content => {{
                content.style.display = expand ? 'block' : 'none';
            }});

            allIcons.forEach(icon => {{
                icon.textContent = expand ? '▼' : '▶';
            }});
        }}
    </script>
</head>
<body>
    <div class="container">
        {self._build_header(project_info)}
        {self._build_summary(score, stats)}
        {self._build_dependencies(project_info)}
        {self._build_version_validation()}
        {self._build_statistics(stats)}
        {self._build_findings_normal(findings, stats)}
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

        .tabs-container {
            padding: 20px;
        }

        .tabs-header {
            display: flex;
            gap: 5px;
            border-bottom: 3px solid #0067B1;
            margin-bottom: 20px;
            background: #f8f9fa;
            padding: 10px 10px 0 10px;
            border-radius: 8px 8px 0 0;
        }

        .tab-button {
            padding: 12px 24px;
            background: transparent;
            border: none;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            color: #666;
            transition: all 0.3s ease;
            position: relative;
            top: 3px;
        }

        .tab-button:hover {
            background: #e9ecef;
            color: #0067B1;
        }

        .tab-button.active {
            color: #0067B1;
            background: white;
            border-bottom: 3px solid #0067B1;
        }

        .tab-content {
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
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
            border-left-color: #0d6efd;
        }
        
        .finding-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .finding-header.clickable {
            cursor: pointer;
            user-select: none;
        }

        .finding-header.clickable:hover {
            background: #f8f9fa;
            margin: -5px;
            padding: 5px;
            border-radius: 5px;
        }

        .finding-title-wrapper {
            display: flex;
            align-items: center;
            gap: 10px;
            flex: 1;
        }

        .toggle-icon {
            font-size: 14px;
            color: #0067B1;
            font-weight: bold;
            min-width: 20px;
            transition: transform 0.2s ease;
        }

        .finding-title {
            font-weight: bold;
            font-size: 16px;
        }

        .collapsible-content {
            display: block;
            transition: all 0.3s ease;
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
            background: #0d6efd;
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

        .occurrence-count {
            color: #0067B1;
            font-weight: bold;
            font-size: 14px;
            margin: 10px 0;
            padding: 8px 12px;
            background: #e3f2fd;
            border-radius: 5px;
            display: inline-block;
        }

        .occurrences-list {
            margin-top: 15px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }

        .occurrence-item {
            padding: 10px;
            margin-bottom: 8px;
            background: white;
            border-radius: 4px;
            border-left: 3px solid #0067B1;
            font-size: 14px;
            line-height: 1.8;
        }

        .occurrence-item:last-child {
            margin-bottom: 0;
        }

        .file-group {
            margin-bottom: 15px;
            padding: 12px;
            background: white;
            border-radius: 6px;
            border-left: 3px solid #0067B1;
        }

        .file-group:last-child {
            margin-bottom: 0;
        }

        .file-header {
            font-size: 15px;
            margin-bottom: 10px;
            color: #333;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .file-count {
            font-size: 12px;
            color: #666;
            font-weight: normal;
            background: #e9ecef;
            padding: 2px 8px;
            border-radius: 10px;
        }

        .locations-list {
            margin-left: 20px;
            padding-left: 15px;
            border-left: 2px solid #e9ecef;
        }

        .location-item {
            padding: 6px 10px;
            margin-bottom: 5px;
            font-size: 14px;
            color: #555;
            background: #f8f9fa;
            border-radius: 4px;
        }

        .location-item:last-child {
            margin-bottom: 0;
        }

        .filters-panel {
            background: #f8f9fa;
            border: 2px solid #0067B1;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .filters-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #dee2e6;
        }

        .filters-header.clickable {
            cursor: pointer;
            user-select: none;
            padding: 10px;
            margin: -10px -10px 15px -10px;
            border-radius: 5px;
        }

        .filters-header.clickable:hover {
            background: #e9ecef;
        }

        .filters-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .filter-group {
            background: white;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #dee2e6;
        }

        .filter-label {
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
            font-size: 14px;
        }

        .filter-options {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .filter-checkbox {
            display: flex;
            align-items: center;
            cursor: pointer;
            padding: 5px;
            border-radius: 4px;
            transition: background 0.2s;
        }

        .filter-checkbox:hover {
            background: #f8f9fa;
        }

        .filter-checkbox input[type="checkbox"] {
            margin-right: 8px;
            cursor: pointer;
            width: 18px;
            height: 18px;
        }

        .filter-checkbox span {
            font-size: 14px;
            user-select: none;
        }

        @media (max-width: 768px) {
            .filters-content {
                grid-template-columns: 1fr;
            }
        }

        .files-scores-list {
            display: grid;
            gap: 15px;
        }

        .file-score-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            border-left: 5px solid #ccc;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .file-score-card:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        .file-score-card.score-excellent {
            border-left-color: #28a745;
            background: linear-gradient(to right, #f0fff4 0%, white 50%);
        }

        .file-score-card.score-good {
            border-left-color: #0d6efd;
            background: linear-gradient(to right, #e3f2fd 0%, white 50%);
        }

        .file-score-card.score-warning {
            border-left-color: #ffc107;
            background: linear-gradient(to right, #fff9e6 0%, white 50%);
        }

        .file-score-card.score-critical {
            border-left-color: #dc3545;
            background: linear-gradient(to right, #ffe6e6 0%, white 50%);
        }

        .file-score-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .file-name {
            font-size: 16px;
            color: #333;
        }

        .file-score {
            text-align: right;
        }

        .score-value {
            font-size: 32px;
            font-weight: bold;
            color: #0067B1;
            line-height: 1;
        }

        .score-label {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }

        .file-score-details {
            border-top: 1px solid #e9ecef;
            padding-top: 15px;
        }

        .findings-summary {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }

        .finding-count {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
        }

        .finding-count.total {
            background: #e9ecef;
            color: #495057;
        }

        .finding-count.errors {
            background: #f8d7da;
            color: #721c24;
        }

        .finding-count.warnings {
            background: #fff3cd;
            color: #856404;
        }

        .finding-count.infos {
            background: #d1ecf1;
            color: #0c5460;
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
        
        .dep-badge {
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            display: inline-block;
        }
        
        .dep-ok { background: #d4edda; color: #155724; }
        .dep-outdated { background: #f8d7da; color: #721c24; }
        .dep-missing { background: #fff3cd; color: #856404; }
        .dep-additional { background: #fff3cd; color: #856404; }
        .dep-unknown { background: #fff3cd; color: #856404; }

        /* Estilos para Gráficos */
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 25px;
            margin-top: 20px;
        }

        .chart-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .chart-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }

        .chart-card-wide {
            grid-column: span 2;
        }

        .chart-title {
            color: #0067B1;
            font-size: 18px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }

        .chart-container {
            position: relative;
            height: 300px;
            margin-bottom: 15px;
        }

        .chart-card-wide .chart-container {
            height: 350px;
        }

        .score-info {
            display: flex;
            justify-content: space-around;
            align-items: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-top: 15px;
        }

        .score-big {
            font-size: 36px;
            font-weight: bold;
            color: #0067B1;
        }

        .grade-big {
            font-size: 18px;
            color: #666;
            font-weight: 600;
        }

        @media (max-width: 1024px) {
            .charts-grid {
                grid-template-columns: 1fr;
            }

            .chart-card-wide {
                grid-column: span 1;
            }
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
        error = project_info.get('error_reading_project_json')
        
        if error:
            return f"""
            <div class="section">
                <h2>📦 Dependencias del Proyecto</h2>
                <div class="finding-item finding-error">
                    <div class="finding-header">
                        <div class="finding-title">Error al leer project.json</div>
                        <span class="severity-badge badge-error">ERROR</span>
                    </div>
                    <div class="finding-details">
                        No se pudo leer el archivo de configuración del proyecto.<br>
                        Detalle: {html.escape(error)}
                    </div>
                </div>
            </div>
            """
        
        if not dependencies:
            return ""
        
        deps_html = """
        <div class="section">
            <h2>📦 Dependencias del Proyecto</h2>
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                <thead>
                    <tr style="background: #f8f9fa; border-bottom: 2px solid #0067B1;">
                        <th style="padding: 12px; text-align: left; width: 35%;">Paquete</th>
                        <th style="padding: 12px; text-align: left; width: 20%;">Versión Instalada</th>
                        <th style="padding: 12px; text-align: left; width: 20%;">Versión Requerida</th>
                        <th style="padding: 12px; text-align: left; width: 25%;">Estado</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for dep in sorted(dependencies, key=lambda x: x['name']):
            status = dep.get('status', 'unknown')
            status_label = dep.get('status_label', 'Desconocido')
            
            badge_class = f"dep-{status}"
            
            installed = dep.get('installed_version') or '-'
            required = dep.get('required_version') or '-'
            
            deps_html += f"""
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;">{html.escape(dep['name'])}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; font-family: monospace;">{html.escape(installed)}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; font-family: monospace;">{html.escape(required)}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;">
                        <span class="dep-badge {badge_class}">{html.escape(status_label)}</span>
                    </td>
                </tr>
            """
        
        deps_html += f"""
                </tbody>
            </table>
            <p style="margin-top: 15px; color: #666; font-size: 14px;">
                Total de paquetes: {len(dependencies)}
            </p>
        </div>
        """

        return deps_html

    def _build_version_validation(self) -> str:
        """Construir sección de validación de compatibilidad de versiones"""
        version_validation = self.results.get('version_validation', {})

        if not version_validation or 'error' in version_validation:
            return ""  # No mostrar si no hay datos o hubo error

        validation_results = version_validation.get('validation_results', [])
        if not validation_results:
            return ""  # No mostrar si no hay resultados

        studio_version_used = version_validation.get('studio_version_used', 'Unknown')
        studio_version_from_project = version_validation.get('studio_version_from_project', 'Unknown')
        selected_manually = version_validation.get('selected_manually', False)

        # Texto explicativo de la versión usada
        if selected_manually:
            version_note = f"Versión seleccionada manualmente: <strong>{html.escape(studio_version_used)}</strong><br>(Versión en project.json: {html.escape(studio_version_from_project)})"
        else:
            version_note = f"Versión de UiPath Studio: <strong>{html.escape(studio_version_used)}</strong> (desde project.json)"

        validation_html = f"""
        <div class="section" style="margin-top: 30px;">
            <h2>🔍 Validación de Compatibilidad de Versiones</h2>
            <p style="margin: 15px 0; color: #666; font-size: 14px;">
                {version_note}
            </p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                <thead>
                    <tr style="background: #f8f9fa; border-bottom: 2px solid #0067B1;">
                        <th style="padding: 12px; text-align: left; width: 35%;">Paquete</th>
                        <th style="padding: 12px; text-align: left; width: 20%;">Versión Instalada</th>
                        <th style="padding: 12px; text-align: left; width: 20%;">Versión Mínima</th>
                        <th style="padding: 12px; text-align: left; width: 25%;">Estado</th>
                    </tr>
                </thead>
                <tbody>
        """

        for result in validation_results:
            package = result.get('package', '')
            installed = result.get('installed_version', '-')
            expected = result.get('expected_version', '-')
            status = result.get('status', 'unknown')
            message = result.get('message', '')

            # Determinar estilo según estado
            if status == 'updated':
                badge_html = '<span class="dep-badge dep-ok" style="background: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">✓ Actualizada</span>'
            elif status == 'outdated':
                badge_html = '<span class="dep-badge dep-outdated" style="background: #dc3545; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">¡Atención! Desactualizada</span>'
            else:
                badge_html = '<span class="dep-badge dep-unknown" style="background: #6c757d; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">Desconocido</span>'

            validation_html += f"""
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;">{html.escape(package)}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; font-family: monospace;">{html.escape(installed)}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; font-family: monospace;">{html.escape(expected)}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;">
                        {badge_html}
                        <br><small style="color: #666;">{html.escape(message)}</small>
                    </td>
                </tr>
            """

        validation_html += """
                </tbody>
            </table>
            <p style="margin-top: 15px; color: #666; font-size: 14px;">
                💡 <strong>Recomendación:</strong> Mantener las dependencias actualizadas garantiza acceso a las últimas mejoras,
                correcciones de errores y nuevas funcionalidades de UiPath Studio.
            </p>
        </div>
        """

        return validation_html

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
        """Construir sección de hallazgos agrupados por regla"""
        if not findings:
            return """
            <div class="section">
                <h2>✅ Hallazgos</h2>
                <div class="no-findings">
                    🎉 ¡Excelente! No se encontraron problemas en el proyecto.
                </div>
            </div>
            """

        # Agrupar hallazgos por (rule_id, category, description, severity)
        # Esto agrupa todas las ocurrencias de la misma regla
        from collections import defaultdict
        grouped = defaultdict(list)

        for finding in findings:
            category = finding.get('category', 'unknown')

            # Omitir hallazgos de dependencias (ya se muestran en la tabla superior)
            if category == 'dependencias':
                continue

            # Clave de agrupación: (category, description, severity)
            # Usamos esto para agrupar hallazgos de la misma regla
            key = (
                finding.get('category', 'unknown'),
                finding.get('description', ''),
                finding.get('severity', 'info')
            )
            grouped[key].append(finding)

        # Construir HTML
        findings_html = """
        <div class="section">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2 style="margin: 0;">🔍 Hallazgos Detallados</h2>
                <div style="display: flex; gap: 10px;">
                    <button onclick="toggleAll(true)" style="padding: 8px 16px; background: #0067B1; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 14px;">
                        ▼ Expandir Todos
                    </button>
                    <button onclick="toggleAll(false)" style="padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 14px;">
                        ▶ Colapsar Todos
                    </button>
                </div>
            </div>
            <div class="findings-list">
        """

        # Ordenar por severidad (error > warning > info)
        severity_order = {'error': 0, 'warning': 1, 'info': 2}
        sorted_groups = sorted(
            grouped.items(),
            key=lambda x: (severity_order.get(x[0][2], 3), x[0][0])
        )

        # Extraer categorías y severidades únicas para los filtros
        categories = set()
        severities = set()
        for (category, description, severity), occurrences in sorted_groups:
            categories.add(category)
            severities.add(severity)

        # Añadir panel de filtros
        findings_html += self._build_filters_panel(categories, severities, stats)

        for idx, ((category, description, severity), occurrences) in enumerate(sorted_groups):
            count = len(occurrences)
            severity_class = f'finding-{severity}'
            badge_class = f'badge-{severity}'

            # ID único para este hallazgo (para collapsar)
            finding_id = f'finding-{idx}'

            # Agrupar ocurrencias por archivo
            by_file = defaultdict(list)
            for occ in occurrences:
                file_path = Path(occ.get('file_path', '')).name
                by_file[file_path].append(occ)

            # Encabezado de la regla agrupada (con botón de toggle)
            # Añadir atributos data- para filtrar
            findings_html += f"""
            <div class="finding-item {severity_class}" data-severity="{severity}" data-category="{category}">
                <div class="finding-header clickable" onclick="toggleFinding('{finding_id}')">
                    <div class="finding-title-wrapper">
                        <span class="toggle-icon" id="icon-{finding_id}">▼</span>
                        <div class="finding-title">
                            [{html.escape(category.upper())}] {html.escape(description)}
                        </div>
                    </div>
                    <span class="severity-badge {badge_class}">{severity}</span>
                </div>
                <div class="occurrence-count" onclick="toggleFinding('{finding_id}')" style="cursor: pointer;">
                    📌 {count} ocurrencia{'s' if count > 1 else ''} encontrada{'s' if count > 1 else ''}
                </div>
                <div class="occurrences-list collapsible-content" id="{finding_id}">
            """

            # Listar por archivo
            for file_name, file_occurrences in sorted(by_file.items()):
                file_count = len(file_occurrences)

                findings_html += f"""
                    <div class="file-group">
                        <div class="file-header">
                            📄 <strong>{html.escape(file_name)}</strong>
                            <span class="file-count">({file_count} ocurrencia{'s' if file_count > 1 else ''})</span>
                        </div>
                        <div class="locations-list">
                """

                # Listar ubicaciones dentro del archivo
                for occurrence in file_occurrences:
                    location = occurrence.get('location', '')

                    if location:
                        findings_html += f"""
                            <div class="location-item">
                                📍 {html.escape(location)}
                            </div>
                        """

                findings_html += """
                        </div>
                    </div>
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

    def _build_filters_panel(self, categories: set, severities: set, stats: Dict) -> str:
        """Construir panel de filtros interactivos"""

        # Contadores por severidad
        severity_counts = stats.get('by_severity', {})

        # Contadores por categoría
        category_counts = stats.get('by_category', {})

        filters_html = """
        <div class="filters-panel">
            <div class="filters-header clickable" onclick="toggleFiltersPanel()">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="toggle-icon" id="icon-filters">▼</span>
                    <span style="font-weight: bold; font-size: 16px;">🔍 Filtros</span>
                </div>
                <button onclick="event.stopPropagation(); resetFilters()" style="padding: 6px 12px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 13px;">
                    ↺ Resetear
                </button>
            </div>

            <div class="filters-content collapsible-content" id="filters-content">
                <div class="filter-group">
                    <div class="filter-label">Por Severidad:</div>
                    <div class="filter-options">
        """

        # Filtros de severidad
        severity_labels = {
            'error': ('❌ Errores', '#dc3545'),
            'warning': ('⚠️ Warnings', '#ffc107'),
            'info': ('ℹ️ Info', '#0d6efd')
        }

        for sev in ['error', 'warning', 'info']:
            if sev in severities:
                label, color = severity_labels.get(sev, (sev, '#666'))
                count = severity_counts.get(sev, 0)
                filters_html += f"""
                        <label class="filter-checkbox">
                            <input type="checkbox" class="severity-filter" value="{sev}" checked onchange="applyFilters()">
                            <span style="color: {color};">{label} ({count})</span>
                        </label>
                """

        filters_html += """
                    </div>
                </div>

                <div class="filter-group">
                    <div class="filter-label">Por Categoría:</div>
                    <div class="filter-options">
        """

        # Filtros de categoría
        for cat in sorted(categories):
            count = category_counts.get(cat, 0)
            cat_display = cat.capitalize()
            filters_html += f"""
                        <label class="filter-checkbox">
                            <input type="checkbox" class="category-filter" value="{cat}" checked onchange="applyFilters()">
                            <span>{cat_display} ({count})</span>
                        </label>
            """

        filters_html += """
                    </div>
                </div>
            </div>
        </div>
        """

        return filters_html

    def _build_files_scores(self, findings: list) -> str:
        """Construir pestaña de scores por archivo"""
        from collections import defaultdict
        from pathlib import Path

        # Agrupar hallazgos por archivo
        by_file = defaultdict(list)
        for finding in findings:
            if finding.get('category') == 'dependencias':
                continue
            file_path = Path(finding.get('file_path', '')).name
            by_file[file_path].append(finding)

        if not by_file:
            return """
            <div class="section">
                <h2>📂 Scores por Archivo</h2>
                <div class="no-findings">
                    ✅ No se encontraron archivos para analizar
                </div>
            </div>
            """

        # Calcular score por archivo
        files_data = []
        for file_name, file_findings in by_file.items():
            # Contar por severidad
            errors = sum(1 for f in file_findings if f.get('severity') == 'error')
            warnings = sum(1 for f in file_findings if f.get('severity') == 'warning')
            infos = sum(1 for f in file_findings if f.get('severity') == 'info')

            # Calcular penalización
            penalty = (errors * 10) + (warnings * 5) + (infos * 1)

            # Calcular score (100 - penalización, mínimo 0)
            score = max(0, 100 - penalty)

            files_data.append({
                'name': file_name,
                'score': score,
                'errors': errors,
                'warnings': warnings,
                'infos': infos,
                'total': len(file_findings)
            })

        # Ordenar por score (peor primero)
        files_data.sort(key=lambda x: x['score'])

        # Construir HTML
        files_html = """
        <div class="section">
            <h2>📂 Scores por Archivo</h2>
            <p style="color: #666; margin-bottom: 20px;">
                Análisis individual de cada archivo XAML. Los archivos con menor score requieren más atención.
            </p>

            <div class="files-scores-list">
        """

        for file_data in files_data:
            score = file_data['score']
            name = file_data['name']
            errors = file_data['errors']
            warnings = file_data['warnings']
            infos = file_data['infos']
            total = file_data['total']

            # Determinar clase y emoji según score
            if score >= 80:
                score_class = 'score-excellent'
                emoji = '✅'
                label = 'Excelente'
            elif score >= 60:
                score_class = 'score-good'
                emoji = '✔️'
                label = 'Bueno'
            elif score >= 40:
                score_class = 'score-warning'
                emoji = '⚠️'
                label = 'Mejorable'
            else:
                score_class = 'score-critical'
                emoji = '❌'
                label = 'Crítico'

            files_html += f"""
            <div class="file-score-card {score_class}">
                <div class="file-score-header">
                    <div class="file-name">
                        📄 <strong>{html.escape(name)}</strong>
                    </div>
                    <div class="file-score">
                        <div class="score-value">{score}/100</div>
                        <div class="score-label">{emoji} {label}</div>
                    </div>
                </div>
                <div class="file-score-details">
                    <div class="findings-summary">
                        <span class="finding-count total">{total} hallazgo{'s' if total != 1 else ''}</span>
            """

            if errors > 0:
                files_html += f"""
                        <span class="finding-count errors">❌ {errors} error{'es' if errors != 1 else ''}</span>
                """

            if warnings > 0:
                files_html += f"""
                        <span class="finding-count warnings">⚠️ {warnings} warning{'s' if warnings != 1 else ''}</span>
                """

            if infos > 0:
                files_html += f"""
                        <span class="finding-count infos">ℹ️ {infos} info</span>
                """

            files_html += """
                    </div>
                </div>
            </div>
            """

        files_html += """
            </div>
        </div>
        """

        return files_html

    def _build_charts(self, findings: list, stats: Dict, score: Dict) -> str:
        """Construir pestaña de gráficos con visualizaciones interactivas"""
        from collections import defaultdict
        from pathlib import Path
        import json

        # Preparar datos para gráficos
        severity_data = {
            'errors': stats.get('errors', 0),
            'warnings': stats.get('warnings', 0),
            'infos': stats.get('infos', 0)
        }

        category_data = stats.get('by_category', {})
        # Filtrar dependencias de las categorías
        category_data = {k: v for k, v in category_data.items() if k != 'dependencias'}

        # Top 10 archivos con más hallazgos
        by_file = defaultdict(int)
        for finding in findings:
            if finding.get('category') != 'dependencias':
                file_path = Path(finding.get('file_path', '')).name
                by_file[file_path] += 1
        
        top_files = sorted(by_file.items(), key=lambda x: x[1], reverse=True)[:10]
        
        score_value = score.get('score', 0)
        grade = score.get('grade', 'N/A')

        # Convertir datos a JSON para JavaScript
        severity_labels = json.dumps(['Errores', 'Warnings', 'Info'])
        severity_values = json.dumps([severity_data['errors'], severity_data['warnings'], severity_data['infos']])
        
        category_labels = json.dumps(list(category_data.keys()))
        category_values = json.dumps(list(category_data.values()))
        
        file_labels = json.dumps([f[0] for f in top_files])
        file_values = json.dumps([f[1] for f in top_files])

        charts_html = f"""
        <div class="section">
            <h2>📈 Visualizaciones del Análisis</h2>
            <p style="color: #666; margin-bottom: 30px;">
                Gráficos interactivos para facilitar el análisis visual de los hallazgos del proyecto.
            </p>

            <div class="charts-grid">
                <!-- Gráfico 1: Distribución por Severidad (Dona) -->
                <div class="chart-card">
                    <h3 class="chart-title">📊 Distribución por Severidad</h3>
                    <div class="chart-container">
                        <canvas id="severityChart"></canvas>
                    </div>
                </div>

                <!-- Gráfico 2: Score Global (Gauge) -->
                <div class="chart-card">
                    <h3 class="chart-title">🎯 Score Global del Proyecto</h3>
                    <div class="chart-container">
                        <canvas id="scoreChart"></canvas>
                    </div>
                    <div class="score-info">
                        <span class="score-big">{score_value}/100</span>
                        <span class="grade-big">Calificación: {html.escape(grade)}</span>
                    </div>
                </div>

                <!-- Gráfico 3: Hallazgos por Categoría (Barras Horizontales) -->
                <div class="chart-card chart-card-wide">
                    <h3 class="chart-title">📂 Hallazgos por Categoría</h3>
                    <div class="chart-container">
                        <canvas id="categoryChart"></canvas>
                    </div>
                </div>

                <!-- Gráfico 4: Top 10 Archivos (Barras) -->
                <div class="chart-card chart-card-wide">
                    <h3 class="chart-title">📄 Top 10 Archivos con Más Hallazgos</h3>
                    <div class="chart-container">
                        <canvas id="filesChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Esperar a que Chart.js esté cargado
            document.addEventListener('DOMContentLoaded', function() {{
                // Gráfico 1: Distribución por Severidad (Dona)
                const severityCtx = document.getElementById('severityChart').getContext('2d');
                new Chart(severityCtx, {{
                    type: 'doughnut',
                    data: {{
                        labels: {severity_labels},
                        datasets: [{{
                            data: {severity_values},
                            backgroundColor: [
                                '#dc3545',  // Rojo para errores
                                '#ffc107',  // Amarillo para warnings
                                '#0d6efd'   // Azul para info
                            ],
                            borderWidth: 2,
                            borderColor: '#fff'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {{
                            legend: {{
                                position: 'bottom',
                                labels: {{
                                    padding: 15,
                                    font: {{
                                        size: 12
                                    }}
                                }}
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        const label = context.label || '';
                                        const value = context.parsed || 0;
                                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                        const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                        return label + ': ' + value + ' (' + percentage + '%)';
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});

                // Gráfico 2: Score Global (Dona como gauge)
                const scoreCtx = document.getElementById('scoreChart').getContext('2d');
                const scoreValue = {score_value};
                const scoreRemaining = 100 - scoreValue;
                
                // Determinar color según score
                let scoreColor = '#dc3545';  // Rojo por defecto
                if (scoreValue >= 90) scoreColor = '#28a745';      // Verde
                else if (scoreValue >= 80) scoreColor = '#90ee90'; // Verde claro
                else if (scoreValue >= 70) scoreColor = '#ffc107'; // Amarillo
                else if (scoreValue >= 60) scoreColor = '#ff9800'; // Naranja

                new Chart(scoreCtx, {{
                    type: 'doughnut',
                    data: {{
                        datasets: [{{
                            data: [scoreValue, scoreRemaining],
                            backgroundColor: [scoreColor, '#e9ecef'],
                            borderWidth: 0
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: true,
                        circumference: 180,
                        rotation: 270,
                        cutout: '75%',
                        plugins: {{
                            legend: {{
                                display: false
                            }},
                            tooltip: {{
                                enabled: false
                            }}
                        }}
                    }}
                }});

                // Gráfico 3: Hallazgos por Categoría (Barras Horizontales)
                const categoryCtx = document.getElementById('categoryChart').getContext('2d');
                new Chart(categoryCtx, {{
                    type: 'bar',
                    data: {{
                        labels: {category_labels},
                        datasets: [{{
                            label: 'Número de Hallazgos',
                            data: {category_values},
                            backgroundColor: '#0067B1',
                            borderColor: '#00A3E0',
                            borderWidth: 1
                        }}]
                    }},
                    options: {{
                        indexAxis: 'y',
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                display: false
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        return 'Hallazgos: ' + context.parsed.x;
                                    }}
                                }}
                            }}
                        }},
                        scales: {{
                            x: {{
                                beginAtZero: true,
                                ticks: {{
                                    stepSize: 1
                                }}
                            }}
                        }}
                    }}
                }});

                // Gráfico 4: Top 10 Archivos (Barras)
                const filesCtx = document.getElementById('filesChart').getContext('2d');
                new Chart(filesCtx, {{
                    type: 'bar',
                    data: {{
                        labels: {file_labels},
                        datasets: [{{
                            label: 'Número de Hallazgos',
                            data: {file_values},
                            backgroundColor: '#dc3545',
                            borderColor: '#c82333',
                            borderWidth: 1
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                display: false
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        return 'Hallazgos: ' + context.parsed.y;
                                    }}
                                }}
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                ticks: {{
                                    stepSize: 1
                                }}
                            }},
                            x: {{
                                ticks: {{
                                    maxRotation: 45,
                                    minRotation: 45
                                }}
                            }}
                        }}
                    }}
                }});
            }});
        </script>
        """

        return charts_html

    def _build_ai_tab(self, ai_data: Dict) -> str:
        """Construir contenido de la pestaña de IA"""
        if not ai_data:
            return ""
            
        # Si hay error, mostrarlo
        if ai_data.get('error'):
            return f"""
            <div id="tab-ia" class="tab-content" style="display: none;">
                <div class="section">
                    <h2>⚠️ Error en Análisis IA</h2>
                    <div style="background: #FFF3CD; color: #856404; padding: 20px; border-radius: 8px; border-left: 5px solid #ffc107;">
                        <h3>No se pudo completar el análisis inteligente</h3>
                        <p style="margin-top: 10px; font-family: monospace;">Detalle: {html.escape(str(ai_data.get('error')))}</p>
                        <p style="margin-top: 20px; font-size: 14px;">Verifique su conexión a internet, su API Key y la disponibilidad del servicio.</p>
                    </div>
                </div>
            </div>
            """

        analysis_raw = ai_data.get('analysis', 'Sin análisis general')
        # Escapar HTML pero preservar saltos de línea visualmente
        analysis_safe = html.escape(analysis_raw).replace('\n', '<br>')
        
        suggestions = ai_data.get('suggestions', [])
        model = html.escape(ai_data.get('model', 'IA Desconocida'))
        
        # Construir sección de sugerencias
        suggestions_html = ""
        for s in suggestions:
            prio = s.get('priority', 'Media')
            color_class = 'badge-info'
            if 'Alta' in prio or 'High' in prio: color_class = 'badge-error'
            elif 'Media' in prio or 'Medium' in prio: color_class = 'badge-warning'
            
            suggestions_html += f"""
            <div class="finding-item">
                <div class="finding-header">
                    <div class="finding-title-wrapper">
                        <span class="severity-badge {color_class}">{html.escape(prio)}</span>
                        <span class="finding-title">{html.escape(s.get('title', 'Sugerencia'))}</span>
                    </div>
                </div>
                <div class="finding-details">
                    <p>{html.escape(s.get('description', ''))}</p>
                    <p><strong>Beneficio:</strong> {html.escape(s.get('benefit', ''))}</p>
                </div>
            </div>
            """
            
        return f"""
        <div id="tab-ia" class="tab-content" style="display: none;">
            <div class="section">
                <h2>🧠 Análisis de Inteligencia Artificial</h2>
                <div style="background: #E3F2FD; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 5px solid #2196F3;">
                    <p><strong>Modelo utilizado:</strong> {model}</p>
                    <div style="margin-top: 10px; line-height: 1.6;">{analysis_safe}</div>
                </div>
                
                <h3>💡 Sugerencias de Mejora</h3>
                <div class="findings-list">
                    {suggestions_html}
                </div>
                
                <div style="margin-top: 20px; font-size: 12px; color: #999; text-align: center;">
                    <em>Nota: Este análisis es generado por IA y puede contener imprecisiones. Revise siempre el código manualmente.</em>
                </div>
            </div>
        </div>
        """

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

    def _get_css_normal(self) -> str:
        """Obtener estilos CSS para reporte normal (sin pestañas)"""
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
            border-left-color: #0d6efd;
        }

        .finding-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .finding-header.clickable {
            cursor: pointer;
            transition: background 0.2s;
        }

        .finding-header.clickable:hover {
            background: #f8f9fa;
            border-radius: 5px;
            padding: 5px;
            margin: -5px;
        }

        .finding-title-wrapper {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .finding-title {
            font-weight: bold;
            font-size: 16px;
        }

        .toggle-icon {
            font-size: 14px;
            color: #0067B1;
            user-select: none;
            min-width: 20px;
        }

        .occurrence-count {
            color: #666;
            font-size: 14px;
            margin-top: 5px;
            padding: 5px 10px;
            background: #f8f9fa;
            border-radius: 5px;
            display: inline-block;
        }

        .collapsible-content {
            display: block;
            margin-top: 15px;
            animation: fadeIn 0.3s;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .occurrences-list {
            margin-top: 15px;
            padding-left: 10px;
        }

        .file-group {
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 3px solid #0067B1;
        }

        .file-header {
            font-size: 15px;
            margin-bottom: 10px;
            color: #333;
        }

        .file-count {
            color: #666;
            font-size: 13px;
            font-weight: normal;
        }

        .locations-list {
            margin-left: 20px;
        }

        .location-item {
            padding: 5px 10px;
            margin: 5px 0;
            background: white;
            border-radius: 3px;
            font-size: 13px;
            color: #555;
            font-family: 'Courier New', monospace;
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
            background: #0d6efd;
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

        .dep-badge {
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }

        .dep-ok {
            background: #d4edda;
            color: #155724;
        }

        .dep-outdated {
            background: #fff3cd;
            color: #856404;
        }

        .dep-missing {
            background: #f8d7da;
            color: #721c24;
        }

        .dep-additional {
            background: #d1ecf1;
            color: #0c5460;
        }
        """

    def _build_findings_normal(self, findings: list, stats: Dict) -> str:
        """Construir sección de hallazgos con agrupamiento multinivel (sin filtros)"""
        if not findings:
            return """
            <div class="section">
                <h2>✅ Hallazgos</h2>
                <div class="no-findings">
                    🎉 ¡Excelente! No se encontraron problemas en el proyecto.
                </div>
            </div>
            """

        # Agrupar hallazgos por (rule_id, category, description, severity)
        from collections import defaultdict
        grouped = defaultdict(list)

        for finding in findings:
            category = finding.get('category', 'unknown')

            # Omitir hallazgos de dependencias (ya se muestran en la tabla superior)
            if category == 'dependencias':
                continue

            # Clave de agrupación: (category, description, severity)
            key = (
                finding.get('category', 'unknown'),
                finding.get('description', ''),
                finding.get('severity', 'info')
            )
            grouped[key].append(finding)

        # Construir HTML
        findings_html = """
        <div class="section">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2 style="margin: 0;">🔍 Hallazgos Detallados</h2>
                <div style="display: flex; gap: 10px;">
                    <button onclick="toggleAll(true)" style="padding: 8px 16px; background: #0067B1; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 14px;">
                        ▼ Expandir Todos
                    </button>
                    <button onclick="toggleAll(false)" style="padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 14px;">
                        ▶ Colapsar Todos
                    </button>
                </div>
            </div>
            <div class="findings-list">
        """

        # Ordenar por severidad (error > warning > info)
        severity_order = {'error': 0, 'warning': 1, 'info': 2}
        sorted_groups = sorted(
            grouped.items(),
            key=lambda x: (severity_order.get(x[0][2], 3), x[0][0])
        )

        for idx, ((category, description, severity), occurrences) in enumerate(sorted_groups):
            count = len(occurrences)
            severity_class = f'finding-{severity}'
            badge_class = f'badge-{severity}'

            # ID único para este hallazgo (para collapsar)
            finding_id = f'finding-{idx}'

            # Agrupar ocurrencias por archivo
            by_file = defaultdict(list)
            for occ in occurrences:
                file_path = Path(occ.get('file_path', '')).name
                by_file[file_path].append(occ)

            # Encabezado de la regla agrupada (con botón de toggle)
            findings_html += f"""
            <div class="finding-item {severity_class}">
                <div class="finding-header clickable" onclick="toggleFinding('{finding_id}')">
                    <div class="finding-title-wrapper">
                        <span class="toggle-icon" id="icon-{finding_id}">▼</span>
                        <div class="finding-title">
                            [{html.escape(category.upper())}] {html.escape(description)}
                        </div>
                    </div>
                    <span class="severity-badge {badge_class}">{severity}</span>
                </div>
                <div class="occurrence-count" onclick="toggleFinding('{finding_id}')" style="cursor: pointer;">
                    📌 {count} ocurrencia{'s' if count > 1 else ''} encontrada{'s' if count > 1 else ''}
                </div>
                <div class="occurrences-list collapsible-content" id="{finding_id}">
            """

            # Listar por archivo
            for file_name, file_occurrences in sorted(by_file.items()):
                file_count = len(file_occurrences)

                findings_html += f"""
                    <div class="file-group">
                        <div class="file-header">
                            📄 <strong>{html.escape(file_name)}</strong>
                            <span class="file-count">({file_count} ocurrencia{'s' if file_count > 1 else ''})</span>
                        </div>
                        <div class="locations-list">
                """

                # Listar ubicaciones dentro del archivo
                for occurrence in file_occurrences:
                    location = occurrence.get('location', '')

                    if location:
                        findings_html += f"""
                            <div class="location-item">
                                📍 {html.escape(location)}
                            </div>
                        """

                findings_html += """
                        </div>
                    </div>
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

