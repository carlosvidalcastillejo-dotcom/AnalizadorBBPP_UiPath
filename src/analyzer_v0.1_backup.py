"""
Analizador de Buenas Prácticas
Aplica reglas de BBPP al código XAML parseado
"""

from typing import Dict, List
from pathlib import Path
import re
from src.config import (
    SEVERITY_ERROR, SEVERITY_WARNING, SEVERITY_INFO,
    PATTERN_CAMEL_CASE, PATTERN_PASCAL_CASE,
    PATTERN_GENERIC_VARIABLE_NAME, GENERIC_NAMES
)


class Finding:
    """Representa un hallazgo (error, warning o info)"""
    
    def __init__(
        self,
        category: str,
        severity: str,
        rule_name: str,
        description: str,
        file_path: str,
        location: str = "",
        details: Dict = None
    ):
        self.category = category
        self.severity = severity
        self.rule_name = rule_name
        self.description = description
        self.file_path = file_path
        self.location = location
        self.details = details or {}
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario"""
        return {
            'category': self.category,
            'severity': self.severity,
            'rule_name': self.rule_name,
            'description': self.description,
            'file_path': self.file_path,
            'location': self.location,
            'details': self.details,
        }


class BBPPAnalyzer:
    """Analizador de Buenas Prácticas para UiPath"""
    
    def __init__(self, config: Dict = None):
        """
        Inicializar analizador con configuración
        
        Args:
            config: Diccionario con configuración de umbrales y validaciones
        """
        self.config = config or {}
        self.findings = []
        
    def analyze(self, parsed_xaml: Dict) -> List[Finding]:
        """
        Analizar un XAML parseado y retornar lista de hallazgos
        
        Args:
            parsed_xaml: Diccionario con datos del XAML parseado
            
        Returns:
            Lista de hallazgos (Finding objects)
        """
        self.findings = []
        
        # Aplicar cada regla
        self._check_nomenclature(parsed_xaml)
        self._check_hardcoded_values(parsed_xaml)
        self._check_nesting(parsed_xaml)
        self._check_try_catch(parsed_xaml)
        self._check_modularization(parsed_xaml)
        self._check_commented_code(parsed_xaml)
        self._check_logs(parsed_xaml)
        
        return self.findings
    
    def _add_finding(
        self,
        category: str,
        severity: str,
        rule_name: str,
        description: str,
        file_path: str,
        location: str = "",
        details: Dict = None
    ):
        """Añadir un hallazgo a la lista"""
        finding = Finding(
            category=category,
            severity=severity,
            rule_name=rule_name,
            description=description,
            file_path=file_path,
            location=location,
            details=details
        )
        self.findings.append(finding)
    
    # ========================================================================
    # REGLAS DE NOMENCLATURA
    # ========================================================================
    
    def _check_nomenclature(self, data: Dict):
        """Verificar nomenclatura de variables y argumentos"""
        file_path = data.get('file_path', '')
        
        # Verificar variables
        for var in data.get('variables', []):
            var_name = var.get('name', '')
            
            # Verificar nombres genéricos
            if self._is_generic_name(var_name):
                self._add_finding(
                    category='nomenclatura',
                    severity=SEVERITY_WARNING,
                    rule_name='generic_variable_name',
                    description=f'Variable con nombre genérico: "{var_name}"',
                    file_path=file_path,
                    location=f'Variable: {var_name}',
                    details={'variable_name': var_name}
                )
            
            # Verificar camelCase (sin prefijo)
            if not self._is_camel_case(var_name) and not self._has_prefix(var_name):
                self._add_finding(
                    category='nomenclatura',
                    severity=SEVERITY_WARNING,
                    rule_name='camelCase_violation',
                    description=f'Variable no usa camelCase: "{var_name}"',
                    file_path=file_path,
                    location=f'Variable: {var_name}',
                    details={'variable_name': var_name, 'expected_format': 'camelCase'}
                )
        
        # Verificar argumentos
        for arg in data.get('arguments', []):
            arg_name = arg.get('name', '')
            description = arg.get('description', '')
            
            # Verificar que argumentos tengan descripción
            validate_descriptions = self.config.get('validations', {}).get('validate_argument_descriptions', True)
            if validate_descriptions and not description:
                self._add_finding(
                    category='nomenclatura',
                    severity=SEVERITY_WARNING,
                    rule_name='missing_argument_description',
                    description=f'Argumento sin descripción: "{arg_name}"',
                    file_path=file_path,
                    location=f'Argument: {arg_name}',
                    details={'argument_name': arg_name}
                )
            
            # Verificar prefijos (in_, out_, io_)
            validate_prefixes = self.config.get('validations', {}).get('validate_variable_prefixes', True)
            if validate_prefixes and not self._has_valid_prefix(arg_name):
                self._add_finding(
                    category='nomenclatura',
                    severity=SEVERITY_INFO,
                    rule_name='missing_argument_prefix',
                    description=f'Argumento sin prefijo estándar (in_/out_/io_): "{arg_name}"',
                    file_path=file_path,
                    location=f'Argument: {arg_name}',
                    details={'argument_name': arg_name}
                )
    
    def _is_generic_name(self, name: str) -> bool:
        """Verificar si es un nombre genérico"""
        name_lower = name.lower().replace('_', '')
        return any(generic in name_lower for generic in GENERIC_NAMES)
    
    def _is_camel_case(self, name: str) -> bool:
        """Verificar si usa camelCase"""
        # Remover prefijos conocidos
        clean_name = re.sub(r'^(in_|out_|io_|config_|const_)', '', name)
        return re.match(PATTERN_CAMEL_CASE, clean_name) is not None
    
    def _has_prefix(self, name: str) -> bool:
        """Verificar si tiene algún prefijo"""
        return any(name.startswith(prefix) for prefix in ['in_', 'out_', 'io_', 'config_', 'const_'])
    
    def _has_valid_prefix(self, name: str) -> bool:
        """Verificar si tiene prefijo válido para argumentos"""
        return any(name.startswith(prefix) for prefix in ['in_', 'out_', 'io_'])
    
    # ========================================================================
    # REGLAS DE HARDCODEO
    # ========================================================================
    
    def _check_hardcoded_values(self, data: Dict):
        """Verificar valores hardcodeados"""
        file_path = data.get('file_path', '')
        
        # Buscar hardcodeo en actividades específicas
        for activity in data.get('activities', []):
            activity_type = activity.get('type', '')
            display_name = activity.get('display_name', '')
            
            # TypeInto, Click, etc. no deberían tener valores hardcodeados
            risky_activities = ['TypeInto', 'Click', 'Type', 'SendHotkey', 'SetText']
            
            if any(risky in activity_type for risky in risky_activities):
                # Esta verificación requeriría acceso al contenido XML completo
                # Por ahora, marcamos como potencial para revisión manual
                pass
        
        # Buscar URLs hardcodeadas en cualquier parte
        # (Esto se haría con búsqueda en el XML raw)
        pass
    
    # ========================================================================
    # REGLAS DE ANIDAMIENTO
    # ========================================================================
    
    def _check_nesting(self, data: Dict):
        """Verificar anidamiento de IFs"""
        file_path = data.get('file_path', '')
        max_nested_ifs = self.config.get('thresholds', {}).get('max_nested_ifs', 3)
        
        for if_activity in data.get('if_activities', []):
            nesting_level = if_activity.get('nesting_level', 0)
            display_name = if_activity.get('display_name', '')
            
            if nesting_level > max_nested_ifs:
                self._add_finding(
                    category='anidamiento',
                    severity=SEVERITY_WARNING,
                    rule_name='excessive_if_nesting',
                    description=f'IF con anidamiento excesivo ({nesting_level} niveles, máximo {max_nested_ifs})',
                    file_path=file_path,
                    location=f'If: {display_name}',
                    details={'nesting_level': nesting_level, 'max_allowed': max_nested_ifs}
                )
    
    # ========================================================================
    # REGLAS DE TRY-CATCH
    # ========================================================================
    
    def _check_try_catch(self, data: Dict):
        """Verificar bloques Try-Catch"""
        file_path = data.get('file_path', '')
        
        for try_catch in data.get('try_catch_blocks', []):
            display_name = try_catch.get('display_name', '')
            is_catch_empty = try_catch.get('is_catch_empty', False)
            
            if is_catch_empty:
                self._add_finding(
                    category='try_catch',
                    severity=SEVERITY_INFO,
                    rule_name='empty_catch_block',
                    description=f'Try-Catch con bloque Catch vacío',
                    file_path=file_path,
                    location=f'TryCatch: {display_name}',
                    details={'display_name': display_name}
                )
    
    # ========================================================================
    # REGLAS DE MODULARIZACIÓN
    # ========================================================================
    
    def _check_modularization(self, data: Dict):
        """Verificar modularización del código"""
        file_path = data.get('file_path', '')
        workflow_type = data.get('workflow_type', '')
        total_activities = len(data.get('activities', []))
        
        max_activities = self.config.get('thresholds', {}).get('max_activities_sequence', 20)
        
        # Si es Sequence y tiene muchas actividades
        if workflow_type == 'Sequence' and total_activities > max_activities:
            self._add_finding(
                category='modularizacion',
                severity=SEVERITY_WARNING,
                rule_name='excessive_sequence_length',
                description=f'Sequence con muchas actividades ({total_activities}, máximo recomendado {max_activities})',
                file_path=file_path,
                location='Workflow principal',
                details={
                    'total_activities': total_activities,
                    'max_recommended': max_activities,
                    'suggestion': 'Considera dividir en múltiples workflows o usar State Machine'
                }
            )
            
            # Sugerencia adicional de State Machine
            if total_activities > max_activities * 1.5:
                self._add_finding(
                    category='modularizacion',
                    severity=SEVERITY_INFO,
                    rule_name='consider_state_machine',
                    description='Considera usar State Machine en lugar de Sequence para mejor organización',
                    file_path=file_path,
                    location='Workflow principal',
                    details={'total_activities': total_activities}
                )
    
    # ========================================================================
    # REGLAS DE CÓDIGO COMENTADO
    # ========================================================================
    
    def _check_commented_code(self, data: Dict):
        """Verificar código comentado"""
        file_path = data.get('file_path', '')
        commented_data = data.get('commented_code', {})
        
        commented_lines = commented_data.get('commented_lines', 0)
        total_lines = data.get('total_lines', 1)
        
        if commented_lines > 0:
            percentage = (commented_lines / total_lines) * 100
            max_percent = self.config.get('thresholds', {}).get('max_commented_code_percent', 5)
            
            if percentage > max_percent:
                self._add_finding(
                    category='codigo_comentado',
                    severity=SEVERITY_WARNING,
                    rule_name='excessive_commented_code',
                    description=f'Código comentado excesivo ({commented_lines} líneas, {percentage:.1f}%)',
                    file_path=file_path,
                    location='Todo el archivo',
                    details={
                        'commented_lines': commented_lines,
                        'total_lines': total_lines,
                        'percentage': round(percentage, 2)
                    }
                )
            else:
                # Info si hay código comentado pero no excesivo
                self._add_finding(
                    category='codigo_comentado',
                    severity=SEVERITY_INFO,
                    rule_name='has_commented_code',
                    description=f'Archivo contiene código comentado ({commented_lines} líneas, {percentage:.1f}%)',
                    file_path=file_path,
                    location='Todo el archivo',
                    details={
                        'commented_lines': commented_lines,
                        'total_lines': total_lines,
                        'percentage': round(percentage, 2)
                    }
                )
    
    # ========================================================================
    # REGLAS DE LOGS
    # ========================================================================
    
    def _check_logs(self, data: Dict):
        """Verificar uso de logs"""
        file_path = data.get('file_path', '')
        logs = data.get('log_messages', [])
        
        # Por ahora, solo reportamos información
        # En el futuro podemos validar patrones específicos
        if len(logs) == 0:
            self._add_finding(
                category='logs',
                severity=SEVERITY_INFO,
                rule_name='no_log_messages',
                description='Workflow sin mensajes de log',
                file_path=file_path,
                location='Todo el archivo',
                details={'log_count': 0}
            )
