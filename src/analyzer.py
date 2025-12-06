"""
Analizador de Buenas Prácticas
Aplica reglas de BBPP al código XAML parseado
VERSIÓN 0.2 - Reglas desde JSON
"""

from typing import Dict, List
from pathlib import Path
import re
from src.config import (
    SEVERITY_ERROR, SEVERITY_WARNING, SEVERITY_INFO,
    PATTERN_CAMEL_CASE, PATTERN_PASCAL_CASE,
    PATTERN_GENERIC_VARIABLE_NAME, GENERIC_NAMES,
    get_active_rules
)


class Finding:
    """Representa un hallazgo de análisis"""
    def __init__(self, category: str, severity: str, rule_name: str, description: str,
                 file_path: str, location: str = "", details: Dict = None, rule_id: str = "", penalty: float = 0):
        self.category = category
        self.severity = severity
        self.rule_name = rule_name
        self.rule_id = rule_id
        self.description = description
        self.file_path = file_path
        self.location = location
        self.details = details or {}
        self.penalty = penalty  # Penalización calculada
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario"""
        return {
            'category': self.category,
            'severity': self.severity,
            'rule_name': self.rule_name,
            'rule_id': self.rule_id,
            'description': self.description,
            'file_path': self.file_path,
            'location': self.location,
            'details': self.details,
            'penalty': self.penalty
        }


class BBPPAnalyzer:
    """Analizador de Buenas Prácticas para UiPath - v0.3 con RulesManager"""
    
    def __init__(self, config: Dict = None, rules: List[Dict] = None, active_sets: List[str] = None):
        """
        Inicializar analizador con configuración
        
        Args:
            config: Diccionario con configuración de umbrales y validaciones
            rules: Lista de reglas a aplicar (si None, carga desde RulesManager)
            active_sets: Lista de conjuntos activos (ej: ['UiPath', 'NTTData'])
        """
        # Importar rules_manager
        from src.rules_manager import get_rules_manager

        self.rules_manager = get_rules_manager()
        self.config = config or {}

        # Si no se especifican conjuntos activos, usar todos los conjuntos habilitados
        if active_sets is None:
            # Obtener todos los conjuntos habilitados dinámicamente
            all_sets = self.rules_manager.get_sets_info()
            self.active_sets = [name for name, info in all_sets.items() if info.get('enabled', True)]
        else:
            self.active_sets = active_sets
        
        # Cargar reglas activas desde BBPP_Master.json
        if rules is None:
            self.rules = self.rules_manager.get_active_rules(self.active_sets)
        else:
            self.rules = rules
        
        self.findings = []
        
        # Agrupar reglas por tipo para acceso rápido
        self.rules_by_type = {}
        for rule in self.rules:
            rule_type = rule.get('rule_type', '')
            if rule_type not in self.rules_by_type:
                self.rules_by_type[rule_type] = []
            self.rules_by_type[rule_type].append(rule)
        
    def analyze(self, parsed_xaml: Dict) -> List[Finding]:
        """
        Analizar un XAML parseado y retornar lista de hallazgos
        
        Args:
            parsed_xaml: Diccionario con datos del XAML parseado
            
        Returns:
            Lista de hallazgos (Finding objects)
        """
        self.findings = []
        
        # Aplicar reglas dinámicamente según su tipo
        self._apply_rules(parsed_xaml)
        
        return self.findings
    
    def analyze_project(self, project_info: Dict) -> List[Finding]:
        """
        Analizar dependencias y configuración del proyecto
        
        Args:
            project_info: Información extraída del project.json
            
        Returns:
            Lista de hallazgos
        """
        # Usar conjuntos activos del constructor
        # Verificar dependencias
        self._check_dependencies(project_info, self.active_sets)
        
        return self.findings
    
    def _apply_rules(self, data: Dict):
        """Aplicar todas las reglas habilitadas al XAML"""
        
        # Reglas de nomenclatura
        self._check_variable_naming(data, self.rules)
        self._check_variable_naming_pascal(data, self.rules)  # Nueva regla PascalCase
        self._check_generic_names(data, self.rules)
        self._check_argument_prefixes(data, self.rules)
        self._check_argument_descriptions(data, self.rules)
        
        # Reglas de estructura y complejidad
        self._check_nested_ifs(data, self.rules)
        self._check_empty_catch(data, self.rules)
        # ELIMINADO: self._check_sequence_size - Duplicado de _check_long_sequences
        
        # Reglas de calidad de código
        self._check_commented_code(data, self.rules)
        self._check_missing_logs(data, self.rules)
        self._check_init_end_pattern(data)
        
        # Reglas organizadas por categoría
        self._check_critical_activities_in_try_catch(data, self.rules)
        self._check_orchestrator_assets(data, self.rules)
        self._check_invoke_workflow_usage(data, self.rules)
        self._check_explicit_timeouts(data, self.rules)
        self._check_stable_selectors(data, self.rules)
        self._check_adequate_logging(data, self.rules)
        # ELIMINADO: self._check_version_control - Regla eliminada
    
    def _add_finding(self, rule: Dict, file_path: str, location: str, 
                     details: Dict = None, count: int = 1):
        """
        Agregar un hallazgo a la lista
        
        Args:
            rule: Regla que generó el hallazgo
            file_path: Ruta del archivo
            location: Ubicación específica del problema
            details: Detalles adicionales
            count: Número de casos encontrados (para penalty_mode individual)
        """
        # Obtener penalty_mode de la regla
        penalty_mode = self.rules_manager.get_rule_parameter(
            rule['id'],
            'penalty_mode'
        ) or 'total'
        
        # Calcular penalización según el modo
        base_penalty = rule.get('penalty', 0)
        
        if penalty_mode == 'individual':
            # Penalización multiplicada por número de casos
            actual_penalty = base_penalty * count
        else:  # 'total'
            # Penalización fija sin importar cuántos casos
            actual_penalty = base_penalty
        
        # Asegurarse de que details no sea None antes de modificarlo
        if details is None:
            details = {}

        # Añadir información de penalización al detalle
        details['penalty_mode'] = penalty_mode
        details['base_penalty'] = base_penalty
        details['cases_found'] = count
        details['actual_penalty'] = actual_penalty

        finding = Finding(
            category=rule.get('category', 'custom'), # Mantener category
            rule_id=rule['id'],
            rule_name=rule['name'],
            severity=rule['severity'],
            file_path=file_path,
            location=location,
            description=rule['description'],
            penalty=actual_penalty,
            details=details
        )
        
        self.findings.append(finding)
    
    # ========================================================================
    # IMPLEMENTACIÓN DE REGLAS
    # ========================================================================
    
    def _check_variable_naming(self, data: Dict, rules: List[Dict]):
        """Verificar nomenclatura de variables según patrón camelCase"""
        rule = next((r for r in rules if r.get('rule_type') == 'variable_naming'), None)
        if not rule or not rule.get('enabled'):
            return

        file_path = data.get('file_path', '')

        # Obtener configuración de prefijos de tipo
        params = rule.get('parameters', {})
        allow_type_prefixes = params.get('allow_type_prefixes', False)
        type_prefixes = params.get('type_prefixes', [])
        
        # NUEVO: Obtener excepciones del REFramework
        exceptions = params.get('exceptions', [])

        for var in data.get('variables', []):
            var_name = var.get('name', '')

            # Ignorar variables vacías o muy cortas
            if len(var_name) < 2:
                continue
            
            # NUEVO: Verificar si es una excepción (REFramework)
            if var_name in exceptions:
                continue  # Saltar validación

            # Verificar y quitar prefijo de tipo si está permitido
            name_to_check = var_name
            detected_type_prefix = None

            if allow_type_prefixes and type_prefixes:
                for type_prefix in type_prefixes:
                    if var_name.startswith(type_prefix):
                        detected_type_prefix = type_prefix
                        name_to_check = var_name[len(type_prefix):]
                        break

            # Patrón camelCase: primera letra minúscula, resto puede ser PascalCase
            # Ejemplos válidos: myVariable, userName, data123, myVar_temp
            # Con prefijos: dt_myVariable, str_userName
            # Ejemplos inválidos: MyVariable, MYVARIABLE, my_variable

            is_valid_camel_case = self._is_camel_case(name_to_check)

            if not is_valid_camel_case:
                # Generar sugerencia
                suggestion = self._to_camel_case(name_to_check)
                if detected_type_prefix:
                    suggestion = f'{detected_type_prefix}{suggestion}'

                self._add_finding(
                    rule=rule,
                    file_path=file_path,
                    location=f"Variable: {var_name}",
                    details={
                        'variable_name': var_name,
                        'expected_pattern': 'camelCase (primera letra minúscula)' + (' con prefijo de tipo opcional' if allow_type_prefixes else ''),
                        'suggestion': f'Renombrar a: {suggestion}',
                        'detected_type_prefix': detected_type_prefix
                    }
                )
    
    def _is_camel_case(self, name: str) -> bool:
        """Verificar si un nombre sigue el patrón camelCase"""
        if not name:
            return False
        
        # Primera letra debe ser minúscula
        if not name[0].islower():
            return False
        
        # No debe tener guiones bajos al inicio (excepto casos especiales como _temp)
        # Permitimos guiones bajos en medio para casos como myVar_temp
        if name.startswith('_'):
            return False
        
        # No debe estar todo en mayúsculas
        if name.isupper():
            return False
        
        # No debe estar todo en minúsculas con guiones bajos (snake_case)
        if '_' in name and name.islower():
            return False
        
        return True
    
    def _to_camel_case(self, name: str) -> str:
        """Convertir un nombre a camelCase (sugerencia)"""
        # Si empieza con mayúscula, convertir primera letra a minúscula
        if name and name[0].isupper():
            return name[0].lower() + name[1:]
        
        # Si es snake_case, convertir a camelCase
        if '_' in name:
            parts = name.split('_')
            return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])
        
        return name
    
    def _is_pascal_case(self, name: str) -> bool:
        """Verificar si un nombre sigue el patrón PascalCase"""
        if not name:
            return False
        
        # Primera letra debe ser mayúscula
        if not name[0].isupper():
            return False
        
        # No debe tener guiones bajos (excepto casos especiales)
        if '_' in name:
            return False
        
        # No debe estar todo en mayúsculas
        if name.isupper():
            return False
        
        return True
    
    def _to_pascal_case(self, name: str) -> str:
        """Convertir un nombre a PascalCase (sugerencia)"""
        # Si empieza con minúscula, convertir primera letra a mayúscula
        if name and name[0].islower():
            return name[0].upper() + name[1:]
        
        # Si es snake_case, convertir a PascalCase
        if '_' in name:
            parts = name.split('_')
            return ''.join(word.capitalize() for word in parts)
        
        return name
    
    def _check_variable_naming_pascal(self, data: Dict, rules: List[Dict]):
        """Verificar nomenclatura de variables según patrón PascalCase"""
        rule = next((r for r in rules if r.get('rule_type') == 'variable_naming_pascal'), None)
        if not rule or not rule.get('enabled'):
            return

        file_path = data.get('file_path', '')

        # Obtener configuración de prefijos de tipo
        params = rule.get('parameters', {})
        allow_type_prefixes = params.get('allow_type_prefixes', False)
        type_prefixes = params.get('type_prefixes', [])
        
        # NUEVO: Obtener excepciones del REFramework
        exceptions = params.get('exceptions', [])

        for var in data.get('variables', []):
            var_name = var.get('name', '')

            # Ignorar variables vacías o muy cortas
            if len(var_name) < 2:
                continue
            
            # NUEVO: Verificar si es una excepción (REFramework)
            if var_name in exceptions:
                continue  # Saltar validación

            # Verificar y quitar prefijo de tipo si está permitido
            name_to_check = var_name
            detected_type_prefix = None

            if allow_type_prefixes and type_prefixes:
                for type_prefix in type_prefixes:
                    if var_name.startswith(type_prefix):
                        detected_type_prefix = type_prefix
                        name_to_check = var_name[len(type_prefix):]
                        break

            # Patrón PascalCase: primera letra mayúscula, cada palabra inicia con mayúscula
            # Ejemplos válidos: MyVariable, UserName, Data123
            # Con prefijos: dt_MyVariable, str_UserName
            # Ejemplos inválidos: myVariable, MYVARIABLE, my_variable

            is_valid_pascal_case = self._is_pascal_case(name_to_check)

            if not is_valid_pascal_case:
                # Generar sugerencia
                suggestion = self._to_pascal_case(name_to_check)
                if detected_type_prefix:
                    suggestion = f'{detected_type_prefix}{suggestion}'

                self._add_finding(
                    rule=rule,
                    file_path=file_path,
                    location=f"Variable: {var_name}",
                    details={
                        'variable_name': var_name,
                        'expected_pattern': 'PascalCase (primera letra mayúscula)' + (' con prefijo de tipo opcional' if allow_type_prefixes else ''),
                        'suggestion': f'Renombrar a: {suggestion}',
                        'detected_type_prefix': detected_type_prefix
                    }
                )
    
    def _check_generic_names(self, data: Dict, rules: List[Dict]):
        """Detectar nombres de variables genéricos"""
        file_path = data.get('file_path', '')

        for rule in rules:
            params = rule.get('parameters', {})
            forbidden_names = params.get('forbidden_names', [])
            generic_patterns = params.get('generic_patterns', [])
            
            # NUEVO: Obtener excepciones del REFramework
            exceptions = params.get('exceptions', [])

            if not forbidden_names and not generic_patterns:
                continue

            for var in data.get('variables', []):
                var_name = var.get('name', '')
                
                # NUEVO: Verificar si es una excepción (REFramework)
                if var_name in exceptions:
                    continue  # Saltar validación
                
                var_name = var_name.lower()
                is_generic = False
                reason = ''

                # 1. Verificar nombres exactos
                if forbidden_names and var_name in [name.lower() for name in forbidden_names]:
                    is_generic = True
                    reason = 'Nombre genérico exacto'

                # 2. Verificar patrones configurables
                if not is_generic and generic_patterns:
                    import re
                    for pattern in generic_patterns:
                        if re.match(pattern, var_name):
                            is_generic = True
                            reason = 'Nombre genérico con número'
                            break

                if is_generic:
                    self._add_finding(
                        rule=rule,
                        file_path=file_path,
                        location=f"Variable: {var.get('name')}",
                        details={'variable_name': var.get('name'), 'reason': reason}
                    )
    
    def _check_argument_prefixes(self, data: Dict, rules: List[Dict]):
        """Verificar prefijos de argumentos y formato después del prefijo"""
        # Buscar la regla específica de prefijos
        rule = next((r for r in rules if r.get('rule_type') == 'argument_prefixes'), None)
        if not rule or not rule.get('enabled'):
            return
        
        file_path = data.get('file_path', '')
        params = rule.get('parameters', {})
        
        if not params.get('check_prefixes', False):
            return
        
        prefix_in = params.get('prefix_in', 'in_')
        prefix_out = params.get('prefix_out', 'out_')
        prefix_inout = params.get('prefix_inout', 'io_')
        
        # Nuevos parámetros para validar formato
        validate_format = params.get('validate_format_after_prefix', False)
        expected_format = params.get('format_after_prefix', 'camelCase')  # 'camelCase' o 'PascalCase'
        
        # NUEVO: Obtener excepciones del REFramework
        exceptions = params.get('exceptions', [])
        
        for arg in data.get('arguments', []):
            arg_name = arg.get('name', '')
            arg_direction = arg.get('direction', '').lower()
            
            # NUEVO: Verificar si es una excepción (REFramework)
            if arg_name in exceptions:
                continue  # Saltar validación
            
            # Determinar prefijo esperado
            expected_prefix = None
            if arg_direction == 'in' and not arg_name.startswith(prefix_in):
                expected_prefix = prefix_in
            elif arg_direction == 'out' and not arg_name.startswith(prefix_out):
                expected_prefix = prefix_out
            elif arg_direction == 'inout' and not arg_name.startswith(prefix_inout):
                expected_prefix = prefix_inout
            
            # Reportar falta de prefijo
            if expected_prefix:
                self._add_finding(
                    rule=rule,
                    file_path=file_path,
                    location=f"Argumento: {arg_name} ({arg_direction})",
                    details={
                        'argument_name': arg_name,
                        'direction': arg_direction,
                        'expected_prefix': expected_prefix,
                        'issue': 'Falta prefijo'
                    }
                )
                continue  # No validar formato si falta el prefijo
            
            # Validar formato después del prefijo (si está configurado)
            if validate_format:
                # LÓGICA INTELIGENTE: Detectar qué regla de nomenclatura está activa
                camel_case_active = any(
                    r.get('id') == 'NOMENCLATURA_001' and r.get('enabled') 
                    for r in self.rules
                )
                pascal_case_active = any(
                    r.get('id') == 'NOMENCLATURA_005' and r.get('enabled') 
                    for r in self.rules
                )
                
                # Determinar formatos aceptados
                accepted_formats = []
                if camel_case_active and pascal_case_active:
                    # Ambas activas: aceptar cualquiera
                    accepted_formats = ['camelCase', 'PascalCase']
                elif pascal_case_active:
                    accepted_formats = ['PascalCase']
                elif camel_case_active:
                    accepted_formats = ['camelCase']
                else:
                    # Ninguna activa: no validar formato (solo prefijos)
                    accepted_formats = []
                
                # Si no hay formatos aceptados, saltar validación
                if not accepted_formats:
                    continue
                
                # Determinar el prefijo actual
                current_prefix = None
                if arg_name.startswith(prefix_in):
                    current_prefix = prefix_in
                elif arg_name.startswith(prefix_out):
                    current_prefix = prefix_out
                elif arg_name.startswith(prefix_inout):
                    current_prefix = prefix_inout
                
                if current_prefix:
                    # Extraer la parte después del prefijo
                    name_after_prefix = arg_name[len(current_prefix):]

                    if name_after_prefix:  # Solo validar si hay algo después del prefijo
                        # Configuración de prefijos de tipo
                        allow_type_prefixes = params.get('allow_type_prefixes', False)
                        type_prefixes = params.get('type_prefixes', [])

                        # Verificar y quitar prefijo de tipo si está permitido
                        name_to_check = name_after_prefix
                        detected_type_prefix = None

                        if allow_type_prefixes and type_prefixes:
                            for type_prefix in type_prefixes:
                                if name_after_prefix.startswith(type_prefix):
                                    detected_type_prefix = type_prefix
                                    name_to_check = name_after_prefix[len(type_prefix):]
                                    break

                        # Verificar si cumple ALGUNO de los formatos aceptados
                        is_valid = False

                        for fmt in accepted_formats:
                            if fmt == 'PascalCase':
                                if self._is_pascal_case(name_to_check):
                                    is_valid = True
                                    break
                            elif fmt == 'camelCase':
                                if self._is_camel_case(name_to_check):
                                    is_valid = True
                                    break

                        # Solo reportar si NO cumple ningún formato aceptado
                        if not is_valid:
                            # Generar mensaje y sugerencia según formatos aceptados
                            if len(accepted_formats) == 2:
                                expected_pattern = 'camelCase o PascalCase'
                                # Sugerir el formato que esté más cerca
                                if name_to_check[0].isupper():
                                    suggestion_base = self._to_pascal_case(name_to_check)
                                else:
                                    suggestion_base = self._to_camel_case(name_to_check)
                            elif accepted_formats[0] == 'PascalCase':
                                expected_pattern = 'PascalCase (primera letra mayúscula)'
                                suggestion_base = self._to_pascal_case(name_to_check)
                            else:  # camelCase
                                expected_pattern = 'camelCase (primera letra minúscula)'
                                suggestion_base = self._to_camel_case(name_to_check)

                            # Construir sugerencia completa con prefijos
                            suggestion = current_prefix
                            if detected_type_prefix:
                                suggestion += detected_type_prefix
                                expected_pattern += ' (con prefijo de tipo permitido)'
                            suggestion += suggestion_base

                            self._add_finding(
                                rule=rule,
                                file_path=file_path,
                                location=f"Argumento: {arg_name} ({arg_direction})",
                                details={
                                    'argument_name': arg_name,
                                    'direction': arg_direction,
                                    'issue': f'No usa {expected_pattern} después del prefijo',
                                    'expected_pattern': expected_pattern,
                                    'suggestion': f'Renombrar a: {suggestion}',
                                    'accepted_formats': accepted_formats,
                                    'detected_type_prefix': detected_type_prefix
                                }
                            )
    
    def _check_state_machine_pattern(self, data: Dict, rules: List[Dict]):
        """Verificar patrón Init/End en State Machines"""
        rule = next((r for r in rules if r.get('rule_type') == 'init_end_pattern'), None)
        if not rule or not rule.get('enabled'):
            return
        
        # Solo aplicar a State Machines
        if data.get('workflow_type') != 'StateMachine':
            return
        
        file_path = data.get('file_path', '')
        states = data.get('states', [])
        
        if not states:
            return
        
        # Obtener nombres de estados
        state_names = [s.get('name', '').lower() for s in states]
        
        # Verificar que existan estados Init y End
        has_init = any('init' in name for name in state_names)
        has_end = any('end' in name or 'final' in name for name in state_names)
        
        # MEJORA: Verificar que Init sea el primer estado y End el último
        first_state = state_names[0] if state_names else ''
        last_state = state_names[-1] if state_names else ''
        
        init_is_first = 'init' in first_state
        end_is_last = 'end' in last_state or 'final' in last_state
        
        issues = []
        
        if not has_init:
            issues.append('Falta estado Init')
        elif not init_is_first:
            issues.append('Estado Init no es el primero')
        
        if not has_end:
            issues.append('Falta estado End/Final')
        elif not end_is_last:
            issues.append('Estado End no es el último')
        
        if issues:
            self._add_finding(
                rule=rule,
                file_path=file_path,
                location="State Machine",
                details={
                    'has_init': has_init,
                    'has_end': has_end,
                    'init_is_first': init_is_first,
                    'end_is_last': end_is_last,
                    'first_state': states[0].get('name', '') if states else '',
                    'last_state': states[-1].get('name', '') if states else '',
                    'total_states': len(states),
                    'issues': issues,
                    'suggestion': '; '.join(issues)
                }
            )
    
    def _check_long_sequences(self, data: Dict, rules: List[Dict]):
        """Detectar Sequences muy largos (cuenta recursivamente hasta Invoke)"""
        rule = next((r for r in rules if r.get('rule_type') == 'long_sequence'), None)
        if not rule or not rule.get('enabled'):
            return
        
        file_path = data.get('file_path', '')
        
        # Obtener parámetro configurable
        max_activities = self.rules_manager.get_rule_parameter(
            rule['id'],
            'max_activities'
        )
        if isinstance(max_activities, dict):
            max_activities = max_activities.get('value', 20)
        if max_activities is None:
            max_activities = 20
        
        # Solo aplicar a workflows tipo Sequence
        if data.get('workflow_type') == 'Sequence':
            # El parser ya cuenta recursivamente
            total_activities = data.get('activity_count', 0)
            
            # Contar Invokes (cada Invoke es un nuevo módulo, deja de contar)
            invoke_count = len([a for a in data.get('activities', []) 
                               if 'InvokeWorkflowFile' in a.get('type', '')])
            
            if total_activities > max_activities:
                self._add_finding(
                    rule=rule,
                    file_path=file_path,
                    location="Sequence principal",
                    details={
                        'activity_count': total_activities,
                        'max_allowed': max_activities,
                        'invoke_count': invoke_count,
                        'suggestion': f'Dividir Sequence de {total_activities} actividades en módulos más pequeños (<{max_activities} actividades cada uno)'
                    },
                    count=1  # Penalización total
                )
    
    def _check_argument_descriptions(self, data: Dict, rules: List[Dict]):
        """Verificar que argumentos tengan descripción"""
        file_path = data.get('file_path', '')
        
        for rule in rules:
            params = rule.get('parameters', {})
            require_description = params.get('require_description', True)
            min_description_length = params.get('min_description_length', 5)
            
            # NUEVO: Obtener excepciones del REFramework
            exceptions = params.get('exceptions', [])
            
            if not require_description:
                continue # Skip this rule if description is not required
            
            for arg in data.get('arguments', []):
                arg_name = arg.get('name', '')
                
                # NUEVO: Verificar si es una excepción (REFramework)
                if arg_name in exceptions:
                    continue  # Saltar validación para este argumento
                
                description = arg.get('annotation', '').strip()
                
                if not description or len(description) < min_description_length:
                    self._add_finding(
                        rule=rule,
                        file_path=file_path,
                        location=f"Argumento: {arg_name}",
                        details={
                            'argument_name': arg_name,
                            'current_description': description or '(vacío)',
                            'min_length_required': min_description_length
                        }
                    )
    
    def _check_nested_ifs(self, data: Dict, rules: List[Dict]):
        """Verificar niveles de IFs anidados"""
        rule = next((r for r in rules if r.get('rule_type') == 'nested_ifs'), None)
        if not rule or not rule.get('enabled'):
            return
        
        file_path = data.get('file_path', '')
        
        # Obtener parámetro configurable
        max_levels = self.rules_manager.get_rule_parameter(
            rule['id'],
            'max_nested_levels'
        )
        
        # Si el parámetro tiene estructura compleja, extraer el valor
        if isinstance(max_levels, dict):
            max_levels = max_levels.get('value', 3)
        
        if max_levels is None:
            max_levels = 3  # Default
        
        # Obtener IFs con nesting_level calculado por el parser
        if_activities = data.get('if_activities', [])
        
        if not if_activities:
            return
        
        # Buscar el máximo nivel de anidamiento
        max_nesting_found = max((if_act.get('nesting_level', 0) for if_act in if_activities), default=0)
        
        # Reportar si excede el máximo permitido
        if max_nesting_found > max_levels:
            # Encontrar todos los IFs que exceden el límite
            problematic_ifs = [
                if_act for if_act in if_activities 
                if if_act.get('nesting_level', 0) > max_levels
            ]
            
            self._add_finding(
                rule=rule,
                file_path=file_path,
                location=f"IFs anidados (máximo encontrado: {max_nesting_found} niveles)",
                details={
                    'max_nesting_found': max_nesting_found,
                    'max_allowed': max_levels,
                    'total_ifs': len(if_activities),
                    'problematic_ifs_count': len(problematic_ifs),
                    'problematic_ifs': [
                        {
                            'display_name': if_act.get('display_name', 'Sin nombre'),
                            'nesting_level': if_act.get('nesting_level', 0)
                        }
                        for if_act in problematic_ifs[:5]  # Mostrar primeros 5
                    ],
                    'suggestion': f'Reducir anidamiento de {max_nesting_found} a máximo {max_levels} niveles. Considera usar variables booleanas o métodos auxiliares.'
                }
            )
    
    def _check_empty_catch(self, data: Dict, rules: List[Dict]):
        """Detectar bloques Try-Catch con Catch vacío"""
        file_path = data.get('file_path', '')
        
        for rule in rules:
            if not rule.get('parameters', {}).get('allow_empty_catch', False):
                for tc in data.get('try_catch_blocks', []):
                    if tc.get('catch_empty', False):
                        self._add_finding(
                            rule=rule,
                            file_path=file_path,
                            location=f"Try-Catch (línea aprox. {tc.get('line', '?')})",
                            details={'try_catch_info': tc}
                        )
    
    # ELIMINADO: _check_sequence_size - Duplicado de _check_long_sequences
    
    def _check_commented_code(self, data: Dict, rules: List[Dict]):
        """Detectar código comentado excesivo"""
        rule = next((r for r in rules if r.get('rule_type') == 'commented_code'), None)
        if not rule or not rule.get('enabled'):
            return
        
        # Obtener parámetro configurable desde rules_manager
        max_percentage = self.rules_manager.get_rule_parameter(
            rule['id'],
            'max_percentage'
        ) or 5  # Default si no existe
        
        file_path = data.get('file_path', '')
        total_activities = data.get('activity_count', 0)
        commented_activities = sum(1 for act in data.get('activities', []) 
                                  if 'CommentOut' in act.get('type', ''))
        
        if total_activities > 0:
            percentage = (commented_activities / total_activities) * 100
            
            if percentage > max_percentage:
                self._add_finding(
                    rule=rule,
                    file_path=file_path,
                    location="Workflow completo",
                    details={
                        'commented_count': commented_activities,
                        'total_activities': total_activities,
                        'percentage': round(percentage, 1),
                        'max_allowed': max_percentage
                    }
                )
     
    def _check_missing_logs(self, data: Dict, rules: List[Dict]):
        """Detectar workflows con ratio insuficiente de logs por actividades"""
        rule = next((r for r in rules if r.get('rule_type') == 'insufficient_logging'), None)
        if not rule or not rule.get('enabled'):
            return
        
        file_path = data.get('file_path', '')
        
        # Obtener parámetro configurable desde rules_manager
        max_activities_per_log = self.rules_manager.get_rule_parameter(
            rule['id'],
            'max_activities_per_log'
        ) or 10  # Default si no existe
        
        # Contar actividades y logs
        total_activities = data.get('activity_count', 0)
        log_messages = data.get('log_messages', [])
        log_count = len(log_messages)
        
        # Evitar división por cero y workflows vacíos
        if total_activities == 0:
            return
        
        # Calcular ratio: actividades por log
        # Si log_count = 0, ratio = infinito (muy malo)
        # Si log_count = 1 y activities = 50, ratio = 50 (malo si max = 10)
        if log_count == 0:
            actual_ratio = total_activities  # Todas las actividades sin logs
        else:
            actual_ratio = total_activities / log_count
        
        # Reportar si el ratio excede el máximo permitido
        if actual_ratio > max_activities_per_log:
            self._add_finding(
                rule=rule,
                file_path=file_path,
                location="Workflow completo",
                details={
                    'total_activities': total_activities,
                    'log_count': log_count,
                    'actual_ratio': round(actual_ratio, 1),
                    'max_allowed_ratio': max_activities_per_log,
                    'suggestion': f'Agregar más LogMessage. Actualmente: 1 log cada {round(actual_ratio, 1)} actividades (máximo: {max_activities_per_log})'
                }
            )
    
    # ========================================================================
    # NUEVAS REGLAS EXCEL
    # ========================================================================
    
    def _check_critical_activities_in_try_catch(self, data: Dict, rules: List[Dict]):
        """Verificar que actividades críticas estén en Try-Catch (ESTRUCTURA_003)"""
        rule = next((r for r in rules if r['id'] == 'ESTRUCTURA_003'), None)
        if not rule or not rule.get('enabled'):
            return

        # Obtener lista configurable de actividades críticas
        params = rule.get('parameters', {})
        critical_activities = params.get('critical_activities', [])

        if not critical_activities:
            critical_activities = [
                'InvokeWorkflowFile', 'InvokeMethod', 'InvokeCode',
                'ReadRange', 'WriteRange', 'OpenBrowser', 'Click',
                'TypeInto', 'GetText'
            ]

        file_path = data.get('file_path', '')
        activities = data.get('activities', [])
        
        for activity in activities:
            activity_type = activity.get('type', '')
            if any(crit in activity_type for crit in critical_activities):
                parent = activity.get('parent_type', '')
                if 'TryCatch' not in parent:
                    self._add_finding(
                        rule, file_path,
                        location=activity.get('display_name', activity_type),
                        details={'activity_type': activity_type}
                    )
    
    def _check_orchestrator_assets(self, data: Dict, rules: List[Dict]):
        """Verificar uso de Orchestrator Assets (CONFIGURACION_001)"""
        rule = next((r for r in rules if r['id'] == 'CONFIGURACION_001'), None)
        if not rule or not rule.get('enabled'):
            return
        
        file_path = data.get('file_path', '')
        activities = data.get('activities', [])
        
        suspicious_patterns = [
            r'password\s*=\s*["\']', r'pwd\s*=\s*["\']',
            r'apikey\s*=\s*["\']', r'token\s*=\s*["\']'
        ]
        
        for activity in activities:
            properties = activity.get('properties', {})
            for prop_name, prop_value in properties.items():
                if isinstance(prop_value, str):
                    for pattern in suspicious_patterns:
                        if re.search(pattern, prop_value, re.IGNORECASE):
                            self._add_finding(
                                rule, file_path,
                                location=activity.get('display_name', ''),
                                details={'property': prop_name}
                            )
                            break
    
    def _check_invoke_workflow_usage(self, data: Dict, rules: List[Dict]):
        """Sugerir modularización con Invoke Workflow (MODULARIZACION_002)"""
        rule = next((r for r in rules if r['id'] == 'MODULARIZACION_002'), None)
        if not rule or not rule.get('enabled'):
            return
        
        file_path = data.get('file_path', '')
        
        # Obtener parámetro configurable
        min_activities = self.rules_manager.get_rule_parameter(
            rule['id'],
            'min_activities_for_modularization'
        )
        if isinstance(min_activities, dict):
            min_activities = min_activities.get('value', 50)
        if min_activities is None:
            min_activities = 50
        
        total_activities = data.get('activity_count', 0)
        invoke_count = len([a for a in data.get('activities', []) 
                           if 'InvokeWorkflowFile' in a.get('type', '')])
        
        # Sugerencia: si tiene muchas actividades y no usa Invoke
        if total_activities > min_activities and invoke_count == 0:
            self._add_finding(
                rule, file_path, 
                location='Workflow principal',
                details={
                    'total_activities': total_activities,
                    'min_threshold': min_activities,
                    'suggestion': f'Considera modularizar este workflow de {total_activities} actividades usando Invoke Workflow File'
                },
                count=1  # Penalización total (penalty=0 en JSON)
            )
    
    def _check_explicit_timeouts(self, data: Dict, rules: List[Dict]):
        """Verificar timeouts explícitos (RENDIMIENTO_001)"""
        rule = next((r for r in rules if r['id'] == 'RENDIMIENTO_001'), None)
        if not rule or not rule.get('enabled'):
            return
        
        file_path = data.get('file_path', '')
        
        # Obtener parámetro configurable
        default_timeout = self.rules_manager.get_rule_parameter(
            rule['id'],
            'default_timeout_ms'
        )
        if isinstance(default_timeout, dict):
            default_timeout = default_timeout.get('value', 30000)
        if default_timeout is None:
            default_timeout = 30000

        # Obtener lista configurable de actividades que requieren timeout
        params_timeout = rule.get('parameters', {})
        timeout_required = params_timeout.get('timeout_required_activities', [])

        if not timeout_required:
            timeout_required = ['Click', 'TypeInto', 'GetText', 'ElementExists', 'Find']

        activities = data.get('activities', [])

        # Contar casos con timeout por defecto
        problematic_activities = []
        
        for activity in activities:
            activity_type = activity.get('type', '')
            if any(req in activity_type for req in timeout_required):
                properties = activity.get('properties', {})
                timeout = properties.get('TimeoutMS') or properties.get('Timeout')
                
                # Verificar si usa timeout por defecto
                if not timeout or str(timeout) == str(default_timeout):
                    problematic_activities.append({
                        'display_name': activity.get('display_name', activity_type),
                        'type': activity_type
                    })
        
        # Reportar si hay casos encontrados
        if problematic_activities:
            self._add_finding(
                rule, file_path,
                location=f'{len(problematic_activities)} actividades con timeout por defecto',
                details={
                    'default_timeout': default_timeout,
                    'activities': problematic_activities[:10],  # Mostrar primeras 10
                    'suggestion': f'Definir timeouts explícitos según el contexto (evitar {default_timeout}ms por defecto)'
                },
                count=len(problematic_activities)  # Penalización individual
            )
    
    def _check_stable_selectors(self, data: Dict, rules: List[Dict]):
        """Verificar selectores estables (SELECTORES_001)"""
        rule = next((r for r in rules if r['id'] == 'SELECTORES_001'), None)
        if not rule or not rule.get('enabled'):
            return
        
        file_path = data.get('file_path', '')
        activities = data.get('activities', [])
        unstable_patterns = [
            (r'idx=', 'Uso de índice'), (r'tableRow=', 'Fila por índice'),
            (r'tableCol=', 'Columna por índice')
        ]
        
        for activity in activities:
            properties = activity.get('properties', {})
            selector = properties.get('Selector', '')
            if selector:
                for pattern, issue_desc in unstable_patterns:
                    if re.search(pattern, selector):
                        self._add_finding(
                            rule, file_path,
                            location=activity.get('display_name', ''),
                            details={'issue': issue_desc}
                        )
                        break
    
    def _check_adequate_logging(self, data: Dict, rules: List[Dict]):
        """Verificar logging adecuado al inicio y fin de workflows principales (LOGGING_002)"""
        rule = next((r for r in rules if r['id'] == 'LOGGING_002'), None)
        if not rule or not rule.get('enabled'):
            return
        
    def _check_dependencies(self, project_info: Dict, active_sets: List[str]):
        """
        Verificar dependencias del proyecto contra los conjuntos activos
        y enriquecer la información del proyecto con el estado de cada una.
        
        Args:
            project_info: Información del proyecto (se modifica in-place)
            active_sets: Lista de conjuntos activos
        """
        # Crear una regla virtual para dependencias si no existe
        rule_id = "DEPENDENCIAS_001"
        rule = next((r for r in self.rules if r['id'] == rule_id), None)
        
        if not rule:
            # Crear regla temporal si no está en BBPP_Master.json
            rule = {
                'id': rule_id,
                'name': 'Dependencias Desactualizadas',
                'description': 'Las dependencias deben cumplir con la versión mínima requerida',
                'category': 'dependencias',
                'severity': 'error',
                'penalty': 10,
                'enabled': True
            }
        
        # 1. Obtener dependencias del proyecto
        # Estructura actual: [{'name': 'UiPath.Excel.Activities', 'version': '2.12.3'}, ...]
        current_deps_list = project_info.get('dependencies', [])
        project_deps_map = {d['name']: d['version'] for d in current_deps_list}
        
        # 2. Obtener dependencias requeridas (BBPP)
        required_deps_map = {}
        for set_name in active_sets:
            deps = self.rules_manager.get_set_dependencies(set_name)
            for pkg, ver in deps.items():
                # Si hay conflicto entre sets, nos quedamos con la versión mayor (simplificación)
                if pkg in required_deps_map:
                    if self._compare_versions(ver, required_deps_map[pkg]) > 0:
                        required_deps_map[pkg] = ver
                else:
                    required_deps_map[pkg] = ver
        
        # 3. Construir lista unificada y comparada
        enriched_dependencies = []
        all_packages = set(project_deps_map.keys()) | set(required_deps_map.keys())
        
        for pkg in sorted(all_packages):
            installed_ver = project_deps_map.get(pkg)
            required_ver = required_deps_map.get(pkg)
            
            status = 'unknown'
            status_label = 'Desconocido'
            
            if installed_ver and not required_ver:
                # Caso: Dependencia Adicional (está en proyecto, no en BBPP)
                status = 'additional'
                status_label = 'N/A: Dependencia Adicional'
                
            elif not installed_ver and required_ver:
                # Caso: No instalada (está en BBPP, no en proyecto)
                status = 'missing'
                status_label = 'N/A: Dependencia no instalada'
                
                # Generar hallazgo (Error)
                self._add_finding(
                    rule=rule,
                    file_path="project.json",
                    location=f"Dependencia: {pkg}",
                    details={
                        'package': pkg,
                        'required_version': required_ver,
                        'current_version': 'No instalado',
                        'issue': 'Paquete requerido faltante'
                    }
                )
                
            elif installed_ver and required_ver:
                # Caso: Comparar versiones
                comparison = self._compare_versions(installed_ver, required_ver)
                
                if comparison < 0:
                    status = 'outdated'
                    status_label = 'Desactualizada'
                    
                    # Generar hallazgo (Error)
                    self._add_finding(
                        rule=rule,
                        file_path="project.json",
                        location=f"Dependencia: {pkg}",
                        details={
                            'package': pkg,
                            'required_version': required_ver,
                            'current_version': installed_ver,
                            'issue': 'Versión desactualizada'
                        }
                    )
                else:
                    status = 'ok'
                    status_label = 'Actualizada'
            
            enriched_dependencies.append({
                'name': pkg,
                'installed_version': installed_ver,
                'required_version': required_ver,
                'status': status,
                'status_label': status_label
            })
            
        # 4. Actualizar project_info con la lista enriquecida
        project_info['dependencies'] = enriched_dependencies

    def _compare_versions(self, v1: str, v2: str) -> int:
        """
        Comparar dos versiones semánticas (v1 vs v2)
        
        Returns:
            1 si v1 > v2
            0 si v1 == v2
            -1 si v1 < v2
        """
        def parse_version(v):
            # Eliminar caracteres no numéricos excepto puntos
            v = re.sub(r'[^\d.]', '', v)
            return [int(x) for x in v.split('.') if x.isdigit()]
            
        parts1 = parse_version(v1)
        parts2 = parse_version(v2)
        
        # Igualar longitud con ceros
        max_len = max(len(parts1), len(parts2))
        parts1 += [0] * (max_len - len(parts1))
        parts2 += [0] * (max_len - len(parts2))
        
        if parts1 > parts2:
            return 1
        elif parts1 < parts2:
            return -1
        else:
            return 0
        file_path = data.get('file_path', '')
        
        # Solo aplicar a workflows principales
        if not any(main in file_path for main in ['Main.xaml', 'Process.xaml', 'Transaction.xaml']):
            return
        
        # Obtener parámetros configurables
        check_start = self.rules_manager.get_rule_parameter(
            rule['id'],
            'check_start_activities'
        ) or 5
        
        check_end = self.rules_manager.get_rule_parameter(
            rule['id'],
            'check_end_activities'
        ) or 5
        
        activities = data.get('activities', [])
        total = len(activities)
        
        # Si el workflow es muy corto, no aplicar la regla
        if total < check_start + check_end:
            return
        
        # Buscar LogMessage en actividades
        log_activities = [a for a in activities if 'LogMessage' in a.get('type', '')]
        
        # Verificar logs al inicio (primeras N actividades)
        has_start_log = any(a.get('index', 999) < check_start for a in log_activities)
        
        # Verificar logs al final (últimas N actividades)
        has_end_log = any(a.get('index', 0) > total - check_end for a in log_activities)
        
        if not has_start_log or not has_end_log:
            missing = []
            if not has_start_log:
                missing.append(f'inicio (primeras {check_start} actividades)')
            if not has_end_log:
                missing.append(f'fin (últimas {check_end} actividades)')
            
            self._add_finding(
                rule, file_path,
                location='Workflow principal',
                details={
                    'has_start_log': has_start_log,
                    'has_end_log': has_end_log,
                    'check_start_activities': check_start,
                    'check_end_activities': check_end,
                    'total_activities': total,
                    'suggestion': f'Agregar LogMessage en: {", ".join(missing)}'
                }
            )
    
    # ELIMINADO: _check_version_control - Regla EXCEL_010 eliminada (no es mala práctica de código)
    
    def _check_init_end_pattern(self, data: Dict):
        """Verificar que State Machines tengan patrón Init/End"""
        # Buscar regla en JSON
        rule = next((r for r in self.rules if r['id'] == 'MODULARIZACION_003'), None)
        if not rule or not rule.get('enabled'):
            return
        
        file_path = data.get('file_path', '')
        workflow_type = data.get('workflow_type', '')
        
        # Solo aplica a State Machines
        if workflow_type != 'StateMachine':
            return
        
        # Buscar states en las actividades
        states = [act for act in data.get('activities', []) 
                  if 'State' in act.get('type', '')]
        
        if not states:
            return
        
        state_names = [s.get('name', '').lower() for s in states]
        
        has_init = any('init' in name for name in state_names)
        has_end = any('end' in name or 'final' in name for name in state_names)
        
        if not has_init or not has_end:
            missing = []
            if not has_init:
                missing.append('Init')
            if not has_end:
                missing.append('End/Final')
            
            # Usar regla del JSON
            self._add_finding(
                rule=rule,
                file_path=file_path,
                location="State Machine",
                details={
                    'found_states': [s.get('name', '') for s in states],
                    'missing_pattern': missing,
                    'suggestion': f'Agregar estados faltantes: {", ".join(missing)}'
                }
            )
