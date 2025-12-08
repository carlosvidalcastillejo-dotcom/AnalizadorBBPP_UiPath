"""
Gestor de Reglas de Buenas Prácticas
Maneja la carga, guardado y gestión de reglas desde BBPP_Master.json
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

class RulesManager:
    """Gestor centralizado de reglas BBPP"""
    
    def __init__(self, bbpp_dir: Optional[Path] = None):
        """
        Inicializar gestor de reglas
        
        Args:
            bbpp_dir: Directorio con archivos BBPP (BBPP_UiPath.json, BBPP_NTTData.json)
        """
        if bbpp_dir is None:
            # Ruta por defecto
            base_path = Path(__file__).parent.parent
            bbpp_dir = base_path / 'config' / 'bbpp'
        
        self.bbpp_dir = Path(bbpp_dir)
        
        # Diccionario de configuraciones por conjunto
        # Estructura: {"UiPath": {metadata, enabled, dependencies, rules}, "NTTData": {...}}
        self.bbpp_sets = {}
        
        # Para compatibilidad con código existente
        self.rules = []  # Todas las reglas (sin duplicados)
        self.sets = {}   # Metadata de conjuntos
        self.metadata = {}  # Metadata general
        
        self.load_rules()
    
    def load_rules(self) -> bool:
        """
        Cargar reglas desde archivos individuales de conjuntos
        
        Returns:
            True si se cargó correctamente
        """
        try:
            # Buscar archivos BBPP_*.json (excepto BBPP_Master.json)
            bbpp_files = [f for f in self.bbpp_dir.glob('BBPP_*.json') 
                         if f.name != 'BBPP_Master.json']
            
            if not bbpp_files:
                print(f"ERROR: No se encontraron archivos BBPP en {self.bbpp_dir}")
                return False
            
            # Cargar cada conjunto
            all_rules_dict = {}  # Para evitar duplicados: {rule_id: rule}

            for bbpp_file in bbpp_files:
                # Extraer nombre del conjunto del archivo (BBPP_UiPath.json -> UiPath)
                set_name = bbpp_file.stem.replace('BBPP_', '')

                with open(bbpp_file, 'r', encoding='utf-8') as f:
                    set_data = json.load(f)

                # Guardar configuración completa del conjunto
                self.bbpp_sets[set_name] = set_data

                # Agregar metadata del conjunto
                self.sets[set_name] = {
                    'name': set_data.get('metadata', {}).get('name', set_name),
                    'description': set_data.get('metadata', {}).get('description', ''),
                    'enabled': set_data.get('enabled', True),
                    'dependencies': set_data.get('dependencies', {})
                }

                # Agregar reglas al diccionario global (COPIAS PROFUNDAS para evitar referencias compartidas)
                for rule in set_data.get('rules', []):
                    rule_id = rule.get('id')
                    if rule_id and rule_id not in all_rules_dict:
                        # Hacer copia profunda para evitar referencias compartidas
                        all_rules_dict[rule_id] = json.loads(json.dumps(rule))

                print(f"OK: Cargado conjunto '{set_name}' desde {bbpp_file.name}")

            # Convertir diccionario a lista para compatibilidad (son copias independientes)
            self.rules = list(all_rules_dict.values())

            print(f"OK: Total {len(self.rules)} reglas unicas cargadas de {len(self.bbpp_sets)} conjuntos")
            return True
            
        except FileNotFoundError as e:
            print(f"ERROR: Archivo no encontrado: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"ERROR al parsear JSON: {e}")
            return False
        except Exception as e:
            print(f"ERROR inesperado al cargar reglas: {e}")
            return False
    
    def save_rules(self, set_name: Optional[str] = None) -> bool:
        """
        Guardar reglas a archivos individuales de conjuntos
        
        Args:
            set_name: Nombre del conjunto a guardar. Si es None, guarda todos.
        
        Returns:
            True si se guardó correctamente
        """
        try:
            sets_to_save = [set_name] if set_name else list(self.bbpp_sets.keys())
            
            for sname in sets_to_save:
                if sname not in self.bbpp_sets:
                    print(f"ADVERTENCIA: Conjunto '{sname}' no existe")
                    continue
                
                # Construir ruta del archivo
                file_path = self.bbpp_dir / f"BBPP_{sname}.json"
                
                # Guardar archivo del conjunto
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.bbpp_sets[sname], f, indent=2, ensure_ascii=False)
                
                print(f"OK: Conjunto '{sname}' guardado en {file_path.name}")
            
            return True
            
        except Exception as e:
            print(f"ERROR al guardar reglas: {e}")
            return False
    
    def get_all_rules(self) -> List[Dict]:
        """Obtener todas las reglas"""
        return self.rules
    
    def get_rules_by_set(self, set_name: str) -> List[Dict]:
        """
        Obtener reglas de un conjunto específico con su configuración
        
        Args:
            set_name: Nombre del conjunto (UiPath, NTTData)
        
        Returns:
            Lista de reglas con configuración específica del conjunto
        """
        if set_name not in self.bbpp_sets:
            return []
        
        return self.bbpp_sets[set_name].get('rules', [])
    
    def get_active_rules(self, active_sets: Optional[List[str]] = None) -> List[Dict]:
        """
        Obtener reglas activas
        
        Args:
            active_sets: Lista de conjuntos activos. Si es None, devuelve todas las activas.
        
        Returns:
            Lista de reglas activas
        """
        active = [rule for rule in self.rules if rule.get('enabled', True)]
        
        if active_sets:
            # Filtrar por conjuntos activos
            active = [
                rule for rule in active 
                if any(s in rule.get('sets', []) for s in active_sets)
            ]
        
        return active
    
    def get_rule_by_id(self, rule_id: str) -> Optional[Dict]:
        """
        Obtener una regla por su ID
        
        Args:
            rule_id: ID de la regla
        
        Returns:
            Diccionario de la regla o None si no existe
        """
        for rule in self.rules:
            if rule.get('id') == rule_id:
                return rule
        return None
    
    def update_rule(self, rule_id: str, updates: Dict, set_name: Optional[str] = None) -> bool:
        """
        Actualizar una regla en un conjunto específico
        
        Args:
            rule_id: ID de la regla a actualizar
            updates: Diccionario con los campos a actualizar
            set_name: Nombre del conjunto donde actualizar. Si es None, actualiza en todos.
        
        Returns:
            True si se actualizó correctamente
        """
        updated = False

        # Determinar en qué conjuntos actualizar
        sets_to_update = [set_name] if set_name else list(self.bbpp_sets.keys())

        for sname in sets_to_update:
            if sname not in self.bbpp_sets:
                continue

            # Actualizar en el conjunto específico
            rules = self.bbpp_sets[sname].get('rules', [])
            for i, rule in enumerate(rules):
                if rule.get('id') == rule_id:
                    self.bbpp_sets[sname]['rules'][i].update(updates)
                    updated = True

        # Si no se especificó conjunto (actualizar todos), también actualizar self.rules para compatibilidad
        if set_name is None:
            for i, rule in enumerate(self.rules):
                if rule.get('id') == rule_id:
                    self.rules[i].update(updates)

        return updated
    
    def get_sets_info(self) -> Dict:
        """Obtener información de los conjuntos"""
        info = {}
        for set_name, set_data in self.sets.items():
            rules_count = len(self.get_rules_by_set(set_name))
            info[set_name] = {
                **set_data,
                'rules_count': rules_count
            }
        return info
    
    def get_statistics(self) -> Dict:
        """
        Obtener estadísticas de las reglas
        
        Returns:
            Diccionario con estadísticas
        """
        total = len(self.rules)
        enabled = len([r for r in self.rules if r.get('enabled', True)])
        implemented = len([r for r in self.rules if r.get('implementation_status') == 'implemented'])
        pending = len([r for r in self.rules if r.get('implementation_status') == 'pending'])
        
        by_severity = {}
        for rule in self.rules:
            sev = rule.get('severity', 'warning')
            by_severity[sev] = by_severity.get(sev, 0) + 1
        
        by_category = {}
        for rule in self.rules:
            cat = rule.get('category', 'general')
            by_category[cat] = by_category.get(cat, 0) + 1
        
        return {
            'total_rules': total,
            'enabled_rules': enabled,
            'implemented_rules': implemented,
            'pending_rules': pending,
            'by_severity': by_severity,
            'by_category': by_category
        }
    
    def get_rule_parameter(self, rule_id: str, param_name: str) -> Optional[any]:
        """
        Obtener el valor de un parámetro de una regla

        Args:
            rule_id: ID de la regla
            param_name: Nombre del parámetro

        Returns:
            Valor del parámetro o None si no existe
        """
        rule = self.get_rule_by_id(rule_id)
        if not rule:
            return None

        parameters = rule.get('parameters', {})
        param = parameters.get(param_name)

        if param is None:
            return None

        # Si el parámetro es un dict con 'value', devolver value
        # Sino, devolver el parámetro directamente (para penalty_mode, penalty_value, etc.)
        if isinstance(param, dict) and 'value' in param:
            return param.get('value')
        else:
            return param
    
    def update_rule_parameter(self, rule_id: str, param_name: str, value: any) -> bool:
        """
        Actualizar el valor de un parámetro de una regla
        
        Args:
            rule_id: ID de la regla
            param_name: Nombre del parámetro
            value: Nuevo valor
        
        Returns:
            True si se actualizó correctamente
        """
        rule = self.get_rule_by_id(rule_id)
        if not rule:
            return False
        
        parameters = rule.get('parameters', {})
        if param_name not in parameters:
            return False
        
        param = parameters[param_name]
        
        # Validar tipo y rango
        if param.get('type') == 'number':
            try:
                value = int(value)
                min_val = param.get('min', float('-inf'))
                max_val = param.get('max', float('inf'))
                
                if value < min_val or value > max_val:
                    print(f"⚠️ Valor {value} fuera de rango [{min_val}, {max_val}]")
                    return False
            except (ValueError, TypeError):
                print(f"⚠️ Valor {value} no es un número válido")
                return False
        
        # Actualizar valor
        param['value'] = value
        
        # Actualizar en la lista de reglas
        for i, r in enumerate(self.rules):
            if r.get('id') == rule_id:
                if 'parameters' not in self.rules[i]:
                    self.rules[i]['parameters'] = {}
                self.rules[i]['parameters'][param_name] = param
                return True
        
        return False
    
    def get_rule_parameters(self, rule_id: str) -> Dict:
        """
        Obtener todos los parámetros de una regla
        
        Args:
            rule_id: ID de la regla
        
        Returns:
            Diccionario con los parámetros de la regla
        """
        rule = self.get_rule_by_id(rule_id)
        if not rule:
            return {}
        
        return rule.get('parameters', {})
    
    def get_set_dependencies(self, set_name: str) -> Dict[str, str]:
        """
        Obtener dependencias configuradas para un conjunto
        
        Args:
            set_name: Nombre del conjunto (ej: 'NTTData')
            
        Returns:
            Diccionario con dependencias {paquete: version}
        """
        if set_name not in self.sets:
            return {}
        
        return self.sets[set_name].get('dependencies', {})

    def set_set_dependencies(self, set_name: str, dependencies: Dict[str, str]) -> bool:
        """
        Establecer dependencias para un conjunto

        Args:
            set_name: Nombre del conjunto
            dependencies: Diccionario de dependencias

        Returns:
            True si se actualizó correctamente
        """
        if set_name not in self.sets:
            return False

        # Actualizar en metadata de conjuntos
        self.sets[set_name]['dependencies'] = dependencies

        # Actualizar en bbpp_sets para guardar en archivo
        if set_name in self.bbpp_sets:
            self.bbpp_sets[set_name]['dependencies'] = dependencies

        return True

    def create_new_set(self, set_name: str, description: str, author: str, copy_from: Optional[str] = None, rules_to_copy: Optional[List[str]] = None) -> bool:
        """
        Crear un nuevo conjunto de BBPP
        
        Args:
            set_name: Nombre del nuevo conjunto (sin espacios ni caracteres especiales)
            description: Descripción del conjunto
            author: Autor del conjunto
            copy_from: Nombre del conjunto del que copiar reglas (opcional)
            rules_to_copy: Lista de IDs de reglas a copiar (opcional)
            
        Returns:
            True si se creó correctamente
        """
        try:
            # Validar nombre
            # Solo permitir alfanuméricos y guiones bajos
            clean_name = "".join(c for c in set_name if c.isalnum() or c == '_')
            if not clean_name:
                print("ERROR: Nombre de conjunto inválido")
                return False
            
            if clean_name in self.bbpp_sets:
                print(f"ERROR: El conjunto '{clean_name}' ya existe")
                return False
            
            # Crear estructura básica
            new_set_data = {
                "metadata": {
                    "name": clean_name,
                    "description": description,
                    "version": "1.0.0",
                    "author": author,
                    "last_updated": "2025-12-07"
                },
                "enabled": True,
                "dependencies": {},
                "rules": []
            }
            
            # Copiar reglas si se solicita
            if copy_from and copy_from in self.bbpp_sets:
                source_rules = self.bbpp_sets[copy_from].get('rules', [])
                
                for rule in source_rules:
                    # Si rules_to_copy es None, copiamos todas. Si no, solo las que estén en la lista.
                    if rules_to_copy is None or rule.get('id') in rules_to_copy:
                        # Crear copia profunda de la regla
                        new_rule = json.loads(json.dumps(rule))
                        
                        # Actualizar el array 'sets' en la regla para incluir el nuevo conjunto
                        if 'sets' in new_rule:
                            if clean_name not in new_rule['sets']:
                                new_rule['sets'].append(clean_name)
                        else:
                            new_rule['sets'] = [clean_name]
                            
                        new_set_data["rules"].append(new_rule)
            
            # Guardar en memoria
            self.bbpp_sets[clean_name] = new_set_data
            
            # Actualizar metadata
            self.sets[clean_name] = {
                'name': clean_name,
                'description': description,
                'enabled': True,
                'dependencies': {}
            }
            
            # Guardar archivo
            file_path = self.bbpp_dir / f"BBPP_{clean_name}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(new_set_data, f, indent=2, ensure_ascii=False)
            
            print(f"OK: Creado nuevo conjunto '{clean_name}' con {len(new_set_data['rules'])} reglas")
            
            # Recargar reglas para actualizar índices globales
            self.load_rules()
            
            return True
            
        except Exception as e:
            print(f"ERROR al crear conjunto: {e}")
            return False



# Función helper para obtener instancia global
_rules_manager_instance = None

def get_rules_manager() -> RulesManager:
    """Obtener instancia global del gestor de reglas"""
    global _rules_manager_instance
    if _rules_manager_instance is None:
        _rules_manager_instance = RulesManager()
    return _rules_manager_instance


if __name__ == '__main__':
    # Test del módulo
    manager = RulesManager()
    
    print("\n📊 Estadísticas:")
    stats = manager.get_statistics()
    print(f"  Total reglas: {stats['total_rules']}")
    print(f"  Activas: {stats['enabled_rules']}")
    print(f"  Implementadas: {stats['implemented_rules']}")
    print(f"  Pendientes: {stats['pending_rules']}")
    
    print("\n📦 Conjuntos:")
    sets_info = manager.get_sets_info()
    for set_name, info in sets_info.items():
        print(f"  {set_name}: {info['rules_count']} reglas - {'✅ Activo' if info['enabled'] else '❌ Inactivo'}")
    
    print("\n✅ Reglas activas del conjunto NTTData:")
    ntt_rules = manager.get_active_rules(['NTTData'])
    for rule in ntt_rules[:5]:
        print(f"  - {rule['name']} ({rule['severity']})")
