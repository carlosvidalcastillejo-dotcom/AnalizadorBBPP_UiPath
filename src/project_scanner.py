"""
Escáner de proyectos UiPath
Recorre recursivamente todos los XAML de un proyecto
"""

from pathlib import Path
from typing import List, Dict, Optional
import json

from src.xaml_parser import XamlParser
from src.analyzer import BBPPAnalyzer, Finding
from src.config import DEFAULT_CONFIG


class ProjectScanner:
    """Escáner de proyectos UiPath"""
    
    def __init__(self, project_path: Path, config: Dict = None, active_sets: List[str] = None):
        """
        Inicializar escáner
        
        Args:
            project_path: Ruta al proyecto UiPath
            config: Configuración de análisis
            active_sets: Lista de conjuntos de reglas activos (ej: ['UiPath', 'NTTData'])
        """
        self.project_path = Path(project_path)
        self.config = config or DEFAULT_CONFIG
        self.active_sets = active_sets if active_sets is not None else ['UiPath', 'NTTData']
        self.xaml_files = []
        self.parsed_files = []
        self.all_findings = []
        self.project_info = {}
        
    def scan(self, progress_callback=None) -> Dict:
        """
        Escanear el proyecto completo
        
        Args:
            progress_callback: Función para reportar progreso (file_path, percentage)
            
        Returns:
            Diccionario con resultados del análisis
        """
        import time
        self._start_time = time.time()  # Para calcular tiempo de ejecución
        
        # 1. Detectar tipo de proyecto
        self.project_info = self._detect_project_info()
        
        # 2. Encontrar todos los XAML
        self.xaml_files = self._find_xaml_files()
        
        if not self.xaml_files:
            return {
                'success': False,
                'error': 'No se encontraron archivos XAML en el proyecto',
                'project_path': str(self.project_path)
            }
        
        # 3. Analizar cada XAML
        # Cargar reglas específicas si se definieron active_sets
        rules = None
        if self.active_sets:
            from src.rules_manager import get_rules_manager
            rm = get_rules_manager()
            rules = rm.get_active_rules(self.active_sets)
            
        analyzer = BBPPAnalyzer(self.config, rules=rules, active_sets=self.active_sets)
        total_files = len(self.xaml_files)
        
        for idx, xaml_file in enumerate(self.xaml_files):
            # Reportar progreso
            if progress_callback:
                percentage = ((idx + 1) / total_files) * 100
                progress_callback(xaml_file.name, percentage)
            
            # Parsear XAML
            parser = XamlParser(xaml_file)
            parsed_data = parser.parse()
            
            if 'error' not in parsed_data:
                self.parsed_files.append(parsed_data)
                
                # Analizar BBPP
                findings = analyzer.analyze(parsed_data)
                self.all_findings.extend(findings)
        
        # 3.5 Analizar dependencias y proyecto global
        project_findings = analyzer.analyze_project(self.project_info)
        self.all_findings.extend(project_findings)
        
        # 4. Calcular estadísticas
        stats = self._calculate_statistics()
        
        # 5. Calcular score
        score = self._calculate_score(stats)
        
        # Preparar resultado
        result = {
            'success': True,
            'project_path': str(self.project_path),
            'project_info': self.project_info,
            'total_files': total_files,
            'analyzed_files': len(self.parsed_files),
            'statistics': stats,
            'score': score,
            'findings': [f.to_dict() for f in self.all_findings],
            'parsed_files': self.parsed_files,
            'bbpp_sets': self.active_sets,  # Conjuntos de BBPP utilizados
        }
        
        # 6. Guardar en base de datos de métricas (auto-save)
        try:
            from src.database.metrics_db import get_metrics_db
            
            start_time = getattr(self, '_start_time', time.time())
            execution_time = time.time() - start_time
            
            # Añadir tiempo de ejecución al resultado
            result['execution_time'] = execution_time
            
            # Guardar en BD
            db = get_metrics_db()
            analysis_id = db.save_analysis(result)
            db.close()
            
            # Opcional: añadir ID al resultado
            result['analysis_id'] = analysis_id
            
            # AUTO-GENERACIÓN DE REPORTES (NUEVO)
            from src.config import load_user_config
            config = load_user_config()
            auto_generate = config.get('output', {}).get('auto_generate_reports', True)
            
            if auto_generate:
                html_path = None
                excel_path = None
                
                # Generar HTML si está habilitado
                if config.get('output', {}).get('generate_html', True):
                    try:
                        from src.report_generator import HTMLReportGenerator
                        html_gen = HTMLReportGenerator(result)
                        html_path = html_gen.generate()
                        print(f"OK: Reporte HTML generado automáticamente: {html_path}")
                    except Exception as e:
                        print(f"WARNING: Error al generar HTML automáticamente: {e}")
                
                # Generar Excel si está habilitado
                if config.get('output', {}).get('generate_excel', False):
                    try:
                        from src.excel_report_generator import ExcelReportGenerator, OPENPYXL_AVAILABLE
                        if OPENPYXL_AVAILABLE:
                            excel_gen = ExcelReportGenerator(
                                result,
                                include_charts=config.get('output', {}).get('include_charts', True)
                            )
                            excel_path = excel_gen.generate()
                            print(f"OK: Reporte Excel generado automáticamente: {excel_path}")
                        else:
                            print("WARNING: openpyxl no disponible - Excel no generado")
                    except Exception as e:
                        print(f"WARNING: Error al generar Excel automáticamente: {e}")
                
                # Guardar rutas en la base de datos
                if html_path or excel_path:
                    try:
                        from src.report_utils import update_analysis_report_paths
                        update_analysis_report_paths(analysis_id, html_path, excel_path)
                        print(f"OK: Rutas de reportes guardadas en BD (ID: {analysis_id})")
                    except Exception as e:
                        print(f"WARNING: Error al guardar rutas en BD: {e}")
            
        except Exception as e:
            # No fallar si no se puede guardar métricas o generar reportes
            print(f"WARNING: No se pudo guardar en base de datos de métricas o generar reportes: {e}")
        
        return result
    
    def _detect_project_info(self) -> Dict:
        """Detectar información del proyecto"""
        info = {
            'name': self.project_path.name,
            'path': str(self.project_path),
            'type': 'Unknown',
            'has_framework': False,
            'has_main': False,
            'dependencies': [],
            'studio_version': 'Unknown',
        }
        
        # Buscar project.json
        project_json = self.project_path / 'project.json'
        if project_json.exists():
            try:
                with open(project_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    info['name'] = data.get('name', info['name'])
                    info['description'] = data.get('description', '')
                    
                    # Extraer versión de Studio
                    info['studio_version'] = data.get('studioVersion', 'Unknown')
                    
                    # Extraer dependencias (solo información, sin juzgar)
                    dependencies = data.get('dependencies', {})
                    for package_name, version in dependencies.items():
                        # Limpiar versión: UiPath usa formato "[2.12.3]"
                        clean_version = version.strip('[]') if isinstance(version, str) else version
                        package_info = {
                            'name': package_name,
                            'version': clean_version
                        }
                        info['dependencies'].append(package_info)
                    
                    # Extraer información adicional
                    info['project_version'] = data.get('projectVersion', 'Unknown')
                    info['entry_points'] = data.get('entryPoints', [])
                    
            except Exception as e:
                info['error_reading_project_json'] = str(e)
        
        # Detectar REFramework
        framework_indicators = [
            'Framework/InitAllSettings.xaml',
            'Framework/GetTransactionData.xaml',
            'Framework/Process.xaml',
        ]
        
        if all((self.project_path / indicator).exists() for indicator in framework_indicators):
            info['type'] = 'REFramework'
            info['has_framework'] = True
        
        # Buscar Main.xaml
        main_xaml = self.project_path / 'Main.xaml'
        if main_xaml.exists():
            info['has_main'] = True
        
        return info
    
    def _find_xaml_files(self) -> List[Path]:
        """Encontrar todos los archivos XAML en el proyecto"""
        xaml_files = []
        
        # Buscar recursivamente
        for xaml_file in self.project_path.rglob('*.xaml'):
            # Ignorar carpetas específicas si es necesario
            if '.local' not in str(xaml_file) and '.git' not in str(xaml_file):
                xaml_files.append(xaml_file)
        
        return sorted(xaml_files)
    
    def _calculate_statistics(self) -> Dict:
        """Calcular estadísticas del análisis"""
        stats = {
            'total_findings': len(self.all_findings),
            'errors': 0,
            'warnings': 0,
            'infos': 0,
            'by_category': {},
            'by_severity': {},
            'findings_by_rule': {},  # NUEVO: Contar hallazgos por regla
            'total_activities': 0,
            'total_variables': 0,
            'total_arguments': 0,
            'total_try_catch': 0,
            'total_logs': 0,
            'files_with_commented_code': 0,
            'total_commented_lines': 0,
        }

        # Contar por severidad y por regla
        for finding in self.all_findings:
            severity = finding.severity
            category = finding.category
            rule_id = finding.rule_id  # Asumimos que los findings tienen rule_id

            if severity == 'error':
                stats['errors'] += 1
            elif severity == 'warning':
                stats['warnings'] += 1
            elif severity == 'info':
                stats['infos'] += 1

            # Por categoría
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1

            # Por regla (NUEVO)
            stats['findings_by_rule'][rule_id] = stats['findings_by_rule'].get(rule_id, 0) + 1

        # Estadísticas de los archivos parseados
        for parsed_file in self.parsed_files:
            stats['total_activities'] += len(parsed_file.get('activities', []))
            stats['total_variables'] += len(parsed_file.get('variables', []))
            stats['total_arguments'] += len(parsed_file.get('arguments', []))
            stats['total_try_catch'] += len(parsed_file.get('try_catch_blocks', []))
            stats['total_logs'] += len(parsed_file.get('log_messages', []))

            commented = parsed_file.get('commented_code', {})
            if commented.get('commented_lines', 0) > 0:
                stats['files_with_commented_code'] += 1
                stats['total_commented_lines'] += commented.get('commented_lines', 0)

        return stats
    
    def _calculate_score(self, stats: Dict) -> Dict:
        """
        Calcular score del proyecto (0-100) usando penalización personalizable por regla

        Args:
            stats: Estadísticas del análisis (debe incluir 'findings_by_rule')

        Returns:
            Diccionario con score y detalles
        """
        from src.rules_manager import get_rules_manager

        # Puntuación base
        base_score = 100

        # Pesos de severidad predeterminados (para modo severity_default)
        error_weight = self.config.get('scoring', {}).get('error_weight', -10)
        warning_weight = self.config.get('scoring', {}).get('warning_weight', -3)
        info_weight = self.config.get('scoring', {}).get('info_weight', -0.5)

        # Obtener gestor de reglas
        rules_manager = get_rules_manager()

        # Agrupar findings por regla
        findings_by_rule = stats.get('findings_by_rule', {})

        # Calcular penalización por cada regla
        total_penalty = 0
        penalty_details = {}

        for rule_id, count in findings_by_rule.items():
            if count == 0:
                continue

            # Obtener configuración de la regla
            rule = rules_manager.get_rule_by_id(rule_id)
            if not rule:
                continue

            # Obtener parámetros de penalización
            params = rule.get('parameters', {})
            penalty_mode = params.get('penalty_mode', 'severity_default')
            penalty_value = params.get('penalty_value', 2)
            use_penalty_cap = params.get('use_penalty_cap', False)
            penalty_cap = params.get('penalty_cap', 10)
            severity = rule.get('severity', 'warning')

            # Calcular penalización según el modo
            rule_penalty = 0

            # Si penalty_value es 0, no penalizar independientemente del modo
            if penalty_value == 0:
                rule_penalty = 0

            elif penalty_mode == 'severity_default':
                # Usar pesos globales según severidad
                if severity == 'error':
                    rule_penalty = count * abs(error_weight)
                elif severity == 'warning':
                    rule_penalty = count * abs(warning_weight)
                elif severity == 'info':
                    rule_penalty = count * abs(info_weight)

            elif penalty_mode == 'individual':
                # Cada hallazgo suma penalty_value%
                rule_penalty = count * penalty_value

            elif penalty_mode == 'global':
                # Penalización fija sin importar cantidad
                rule_penalty = penalty_value

            # Aplicar límite máximo si está configurado
            if use_penalty_cap and penalty_mode in ['severity_default', 'individual']:
                rule_penalty = min(rule_penalty, penalty_cap)

            # Acumular penalización
            total_penalty += rule_penalty
            penalty_details[rule_id] = {
                'count': count,
                'mode': penalty_mode,
                'penalty': round(rule_penalty, 2)
            }

        # Ajuste por tamaño del proyecto (SCALING_FACTOR)
        total_activities = max(1, stats.get('total_activities', 1))
        penalty_per_activity = total_penalty / total_activities

        # Factor de sensibilidad (configurable desde config)
        SCALING_FACTOR = self.config.get('scoring', {}).get('scaling_factor', 5)

        adjusted_penalty = penalty_per_activity * SCALING_FACTOR

        # Score final (mínimo 0, máximo 100)
        if total_activities < 10:
            # Proyectos pequeños: penalización directa amortiguada
            final_score = max(0, base_score - (total_penalty * 0.5))
        else:
            # Proyectos grandes: penalización ajustada por actividad
            final_score = max(0, base_score - adjusted_penalty)

        # Determinar calificación
        if final_score >= 90:
            grade = 'A - Excelente'
            color = 'green'
        elif final_score >= 80:
            grade = 'B - Muy Bien'
            color = 'lightgreen'
        elif final_score >= 70:
            grade = 'C - Bien'
            color = 'yellow'
        elif final_score >= 60:
            grade = 'D - Aceptable'
            color = 'orange'
        else:
            grade = 'F - Necesita Mejoras'
            color = 'red'

        return {
            'score': round(final_score, 2),
            'grade': grade,
            'color': color,
            'penalties': {
                'total': round(total_penalty, 2),
                'by_rule': penalty_details,
                'penalty_per_activity': round(penalty_per_activity, 2),
                'adjusted_penalty': round(adjusted_penalty, 2),
                'scaling_factor': SCALING_FACTOR
            }
        }
    
    def get_summary(self) -> str:
        """Obtener resumen textual del análisis"""
        if not self.parsed_files:
            return "No se ha realizado ningún análisis todavía."
        
        stats = self._calculate_statistics()
        score = self._calculate_score(stats)
        
        summary = f"""
╔═══════════════════════════════════════════════════════════════╗
║           RESUMEN DEL ANÁLISIS DE BUENAS PRÁCTICAS            ║
╚═══════════════════════════════════════════════════════════════╝

📁 PROYECTO: {self.project_info.get('name', 'Unknown')}
📂 Tipo: {self.project_info.get('type', 'Unknown')}
🔧 UiPath Studio: {self.project_info.get('studio_version', 'Unknown')}

📊 SCORE GLOBAL: {score['score']}/100 - {score['grade']}

📈 ESTADÍSTICAS:
   • Archivos analizados: {len(self.parsed_files)}
   • Total actividades: {stats['total_activities']}
   • Total variables: {stats['total_variables']}
   • Total argumentos: {stats['total_arguments']}

⚠️  HALLAZGOS:
   • ❌ Errors: {stats['errors']}
   • ⚠️  Warnings: {stats['warnings']}
   • ℹ️  Info: {stats['infos']}
   • Total: {stats['total_findings']}

📝 POR CATEGORÍA:
"""
        
        for category, count in stats['by_category'].items():
            summary += f"   • {category}: {count}\n"
        
        if stats['files_with_commented_code'] > 0:
            # Calcular porcentaje promedio
            total_commented = stats['total_commented_lines']
            total_lines = sum(f.get('total_lines', 0) for f in self.parsed_files)
            avg_percentage = (total_commented / total_lines * 100) if total_lines > 0 else 0
            
            summary += f"\n💬 CÓDIGO COMENTADO:\n"
            summary += f"   • Encontrado {avg_percentage:.1f}% promedio de código comentado en:\n"
            
            # Listar archivos con porcentajes individuales
            for parsed_file in self.parsed_files:
                commented_lines = parsed_file.get('commented_lines', 0)
                if commented_lines > 0:
                    file_total_lines = parsed_file.get('total_lines', 0)
                    file_percentage = (commented_lines / file_total_lines * 100) if file_total_lines > 0 else 0
                    file_name = Path(parsed_file.get('file_path', '')).stem  # Sin extensión
                    summary += f"     - {file_name} ({file_percentage:.1f}%)\n"
            
            summary += f"   • Total líneas comentadas: {total_commented}\n"
        
        # Información de dependencias
        dependencies = self.project_info.get('dependencies', [])
        if dependencies:
            summary += f"\n📦 DEPENDENCIAS ({len(dependencies)} paquetes):\n"
            
            # Mostrar primeros 10 paquetes
            for pkg in dependencies[:10]:
                name = pkg.get('name', 'Unknown')
                # Soporte para formato antiguo y nuevo
                version = pkg.get('installed_version') or pkg.get('version') or 'No instalada'
                status = pkg.get('status_label', '')
                
                if status:
                    summary += f"   • {name}: {version} ({status})\n"
                else:
                    summary += f"   • {name}: {version}\n"
            
            if len(dependencies) > 10:
                summary += f"   ... y {len(dependencies) - 10} paquetes más\n"
        
        return summary
