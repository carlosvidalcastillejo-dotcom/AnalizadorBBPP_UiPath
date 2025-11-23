"""
Parser de archivos XAML de UiPath
Extrae información de workflows, actividades, variables, etc.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

class XamlParser:
    """Parser para archivos XAML de UiPath"""
    
    # Namespaces de UiPath
    NAMESPACES = {
        'x': 'http://schemas.microsoft.com/winfx/2006/xaml',
        'ui': 'http://schemas.uipath.com/workflow/activities',
        'sap': 'http://schemas.microsoft.com/netfx/2009/xaml/activities/presentation',
        'sap2010': 'http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation',
        'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    }
    
    def __init__(self, xaml_path: Path):
        """
        Inicializar parser con ruta del archivo XAML
        
        Args:
            xaml_path: Ruta al archivo .xaml
        """
        self.xaml_path = Path(xaml_path)
        self.tree = None
        self.root = None
        self.workflow_type = None
        self.parsed_data = {}
        
    def parse(self) -> Dict:
        """
        Parsear el archivo XAML y extraer toda la información relevante
        
        Returns:
            Diccionario con información del workflow
        """
        try:
            # Leer y parsear el XML
            self.tree = ET.parse(self.xaml_path)
            self.root = self.tree.getroot()
            
            # Detectar tipo de workflow
            self.workflow_type = self._detect_workflow_type()
            
            # Detectar código comentado
            commented_code_data = self._detect_commented_code()
            
            # Extraer información
            self.parsed_data = {
                'file_path': str(self.xaml_path),
                'file_name': self.xaml_path.name,
                'workflow_type': self.workflow_type,
                'display_name': self._get_display_name(),
                'annotation': self._get_annotation(),
                'variables': self._extract_variables(),
                'arguments': self._extract_arguments(),
                'activities': self._extract_activities(),
                'invoke_workflow_files': self._extract_invoke_workflows(),
                'log_messages': self._extract_log_messages(),
                'try_catch_blocks': self._extract_try_catch_blocks(),
                'if_activities': self._extract_if_activities(),
                'commented_code': commented_code_data,
                'commented_lines': commented_code_data.get('commented_lines', 0),  # Para el analizador
                'total_lines': self._count_lines(),
            }
            
            return self.parsed_data
            
        except ET.ParseError as e:
            return {
                'file_path': str(self.xaml_path),
                'error': f'Error parsing XML: {str(e)}',
                'parse_success': False
            }
        except Exception as e:
            return {
                'file_path': str(self.xaml_path),
                'error': f'Error: {str(e)}',
                'parse_success': False
            }
    
    def _detect_workflow_type(self) -> str:
        """Detectar tipo de workflow (StateMachine, Sequence, Flowchart)"""
        # Buscar elemento principal
        if self.root.find('.//StateMachine', self.NAMESPACES) is not None:
            return 'StateMachine'
        elif self.root.find('.//Sequence', self.NAMESPACES) is not None:
            return 'Sequence'
        elif self.root.find('.//Flowchart', self.NAMESPACES) is not None:
            return 'Flowchart'
        else:
            return 'Unknown'
    
    def _get_display_name(self) -> Optional[str]:
        """Obtener DisplayName del workflow principal"""
        main_element = self.root.find('.//*[@DisplayName]', self.NAMESPACES)
        if main_element is not None:
            return main_element.get('DisplayName')
        return None
    
    def _get_annotation(self) -> Optional[str]:
        """Obtener anotación del workflow"""
        annotation_attr = f"{{{self.NAMESPACES['sap2010']}}}Annotation.AnnotationText"
        for elem in self.root.iter():
            if annotation_attr in elem.attrib:
                return elem.attrib[annotation_attr]
        return None
    
    def _extract_variables(self) -> List[Dict]:
        """Extraer todas las variables del workflow"""
        variables = []
        
        # Iterar por todos los elementos buscando Variable
        for elem in self.root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            
            if tag == 'Variable':
                # Obtener el tipo de la variable
                type_arg = elem.get(f"{{{self.NAMESPACES['x']}}}TypeArguments")
                if not type_arg:
                    # Intentar sin namespace completo
                    type_arg = elem.get('TypeArguments', 'Unknown')
                
                var_data = {
                    'name': elem.get('Name', ''),
                    'type': type_arg,
                    'default': elem.get('Default', None),
                }
                variables.append(var_data)
        
        return variables
    
    def _extract_arguments(self) -> List[Dict]:
        """Extraer argumentos (in/out/io) del workflow"""
        arguments = []
        
        # Buscar en x:Members
        members = self.root.find(f".//{{{self.NAMESPACES['x']}}}Members", self.NAMESPACES)
        if members is not None:
            for prop in members.findall(f".//{{{self.NAMESPACES['x']}}}Property", self.NAMESPACES):
                annotation_attr = f"{{{self.NAMESPACES['sap2010']}}}Annotation.AnnotationText"
                arg_data = {
                    'name': prop.get('Name', ''),
                    'type': prop.get('Type', ''),
                    'description': prop.get(annotation_attr, ''),
                }
                arguments.append(arg_data)
        
        return arguments
    
    def _extract_activities(self) -> List[Dict]:
        """Extraer todas las actividades del workflow"""
        activities = []
        activity_count = {}
        
        # Buscar todos los elementos con DisplayName (son actividades)
        for elem in self.root.iter():
            display_name = elem.get('DisplayName')
            if display_name:
                activity_type = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                
                # Contar actividades por tipo
                activity_count[activity_type] = activity_count.get(activity_type, 0) + 1
                
                activities.append({
                    'type': activity_type,
                    'display_name': display_name,
                    'tag': elem.tag,
                })
        
        return activities
    
    def _extract_invoke_workflows(self) -> List[Dict]:
        """Extraer todos los InvokeWorkflowFile"""
        invokes = []
        
        for elem in self.root.iter():
            if 'InvokeWorkflowFile' in elem.tag:
                workflow_file = elem.get('WorkflowFileName', '')
                invokes.append({
                    'workflow_file': workflow_file,
                    'display_name': elem.get('DisplayName', ''),
                })
        
        return invokes
    
    def _extract_log_messages(self) -> List[Dict]:
        """Extraer todos los LogMessage (excluyendo los comentados)"""
        logs = []
        
        # Primero, identificar todos los elementos dentro de CommentOut
        commented_elements = set()
        for elem in self.root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if tag == 'CommentOut':
                # Marcar todos los descendientes como comentados
                for child in elem.iter():
                    commented_elements.add(child)
        
        # Ahora buscar LogMessages excluyendo los comentados
        for elem in self.root.iter():
            if elem in commented_elements:
                continue  # Saltar elementos dentro de CommentOut
                
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if tag == 'LogMessage':
                logs.append({
                    'message': elem.get('Message', ''),
                    'level': elem.get('Level', 'Info'),
                    'display_name': elem.get('DisplayName', ''),
                })
        
        return logs
    
    def _extract_try_catch_blocks(self) -> List[Dict]:
        """Extraer bloques Try-Catch"""
        try_catches = []
        
        for elem in self.root.iter():
            if elem.tag.endswith('TryCatch'):
                # Verificar si tiene Catch
                has_catch = elem.find('.//Catch', self.NAMESPACES) is not None
                has_finally = elem.find('.//Finally', self.NAMESPACES) is not None
                
                # Verificar si el Catch está vacío
                catch_elem = elem.find('.//Catch', self.NAMESPACES)
                is_catch_empty = False
                if catch_elem is not None:
                    # Un Catch está vacío si no tiene actividades hijas significativas
                    catch_children = list(catch_elem.iter())
                    is_catch_empty = len(catch_children) <= 3  # Solo estructura básica
                
                try_catches.append({
                    'display_name': elem.get('DisplayName', ''),
                    'has_catch': has_catch,
                    'has_finally': has_finally,
                    'is_catch_empty': is_catch_empty,
                })
        
        return try_catches
    
    def _extract_if_activities(self) -> List[Dict]:
        """Extraer actividades If y calcular anidamiento"""
        ifs = []
        
        def get_nesting_level(element, level=0):
            """Calcular nivel de anidamiento de un If"""
            parent = element.getparent() if hasattr(element, 'getparent') else None
            if parent is None:
                return level
            if parent.tag.endswith('If'):
                return get_nesting_level(parent, level + 1)
            return get_nesting_level(parent, level)
        
        for elem in self.root.iter():
            if elem.tag.endswith('If'):
                # Calcular nivel de anidamiento
                nesting = 0
                parent = elem
                for _ in range(10):  # Límite de seguridad
                    parent_candidates = [p for p in self.root.iter() if elem in list(p)]
                    if parent_candidates:
                        for p in parent_candidates:
                            if p.tag.endswith('If'):
                                nesting += 1
                    else:
                        break
                
                ifs.append({
                    'display_name': elem.get('DisplayName', ''),
                    'condition': elem.get('Condition', ''),
                    'nesting_level': nesting,
                })
        
        return ifs
    
    def _detect_commented_code(self) -> Dict:
        """Detectar código XML comentado y actividades CommentOut"""
        try:
            with open(self.xaml_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 1. Buscar comentarios XML estándar (<!-- -->)
            comment_pattern = r'<!--.*?-->'
            xml_comments = re.findall(comment_pattern, content, re.DOTALL)
            
            # Contar líneas en comentarios XML
            xml_commented_lines = sum(comment.count('\n') + 1 for comment in xml_comments)
            
            # 2. Buscar actividades CommentOut y contar sus líneas REALES
            comment_out_activities = []
            comment_out_lines = 0
            
            # Buscar todos los elementos que contengan "CommentOut" en su tag
            for elem in self.root.iter():
                tag_name = elem.tag
                # Quitar namespace si existe
                if '}' in tag_name:
                    tag_name = tag_name.split('}')[1]
                
                if tag_name == 'CommentOut':
                    # Contar actividades dentro del CommentOut
                    activities_inside = self._count_activities_recursive(elem)
                    
                    # Contar LÍNEAS REALES del CommentOut en el archivo
                    # Buscar el bloque completo en el contenido
                    display_name = elem.get('DisplayName', '')
                    
                    # Buscar el bloque CommentOut en el contenido usando regex
                    # Patrón: desde <CommentOut hasta </CommentOut>
                    comment_out_pattern = r'<[^:]*:?CommentOut[^>]*DisplayName="' + re.escape(display_name) + r'"[^>]*>.*?</[^:]*:?CommentOut>'
                    match = re.search(comment_out_pattern, content, re.DOTALL)
                    
                    if match:
                        # Contar líneas en el match
                        comment_block = match.group(0)
                        lines_in_block = comment_block.count('\n') + 1
                    else:
                        # Fallback: estimar por actividades (por si no se encuentra el patrón)
                        lines_in_block = activities_inside * 4
                    
                    comment_out_activities.append({
                        'display_name': display_name,
                        'activities_inside': activities_inside,
                        'lines': lines_in_block
                    })
                    
                    comment_out_lines += lines_in_block
            
            # Total de líneas comentadas
            total_commented_lines = xml_commented_lines + comment_out_lines
            
            # Detectar si hay actividades comentadas
            has_commented_activities = (
                any('DisplayName' in comment or 'Activity' in comment or 'Sequence' in comment 
                    for comment in xml_comments)
                or len(comment_out_activities) > 0
            )
            
            return {
                'total_comments': len(xml_comments) + len(comment_out_activities),
                'xml_comments': len(xml_comments),
                'comment_out_activities': len(comment_out_activities),
                'commented_lines': total_commented_lines,
                'xml_commented_lines': xml_commented_lines,
                'comment_out_lines': comment_out_lines,
                'has_commented_activities': has_commented_activities,
                'comments': xml_comments[:3],  # Primeros 3 comentarios XML como muestra
                'comment_out_details': comment_out_activities,  # Detalles de CommentOut
            }
        except Exception as e:
            return {
                'error': str(e),
                'total_comments': 0,
                'commented_lines': 0,
            }
    
    def _count_activities_recursive(self, element) -> int:
        """Contar actividades dentro de un elemento recursivamente"""
        count = 0
        for child in element:
            # Si el elemento tiene DisplayName, es probablemente una actividad
            if child.get('DisplayName'):
                count += 1
            # Contar recursivamente
            count += self._count_activities_recursive(child)
        return count
    
    def _count_lines(self) -> int:
        """Contar líneas totales del archivo"""
        try:
            with open(self.xaml_path, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except:
            return 0
    
    def get_activity_count(self) -> int:
        """Obtener número total de actividades"""
        if 'activities' in self.parsed_data:
            return len(self.parsed_data['activities'])
        return 0
    
    def find_hardcoded_values(self) -> List[Dict]:
        """
        Buscar valores hardcodeados en actividades específicas
        (TypeInto, Click, etc.)
        """
        hardcoded = []
        
        # Buscar actividades que no deberían tener valores hardcodeados
        risky_activities = ['TypeInto', 'Click', 'Type', 'SendHotkey']
        
        for elem in self.root.iter():
            activity_type = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            
            if any(risky in activity_type for risky in risky_activities):
                # Buscar atributos que puedan contener valores hardcodeados
                text_attr = elem.get('Text', '')
                input_attr = elem.get('Input', '')
                
                # Detectar si es un valor literal (no variable)
                if text_attr and not text_attr.startswith('['):
                    hardcoded.append({
                        'activity_type': activity_type,
                        'display_name': elem.get('DisplayName', ''),
                        'hardcoded_value': text_attr,
                        'attribute': 'Text',
                    })
                
                if input_attr and not input_attr.startswith('['):
                    hardcoded.append({
                        'activity_type': activity_type,
                        'display_name': elem.get('DisplayName', ''),
                        'hardcoded_value': input_attr,
                        'attribute': 'Input',
                    })
        
        return hardcoded


# Función auxiliar para uso rápido
def parse_xaml_file(xaml_path: str) -> Dict:
    """
    Función de conveniencia para parsear un archivo XAML
    
    Args:
        xaml_path: Ruta al archivo XAML
        
    Returns:
        Diccionario con información parseada
    """
    parser = XamlParser(xaml_path)
    return parser.parse()
