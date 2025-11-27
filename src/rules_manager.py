"""
Gestor de Reglas de Buenas Prácticas
Maneja la carga, guardado y gestión de reglas desde BBPP_Master.json
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

class RulesManager:
    """Gestor centralizado de reglas BBPP"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Inicializar gestor de reglas
        
        Args:
            config_path: Ruta al archivo BBPP_Master.json
        """
        if config_path is None:
            # Ruta por defecto
            base_path = Path(__file__).parent.parent
            config_path = base_path / 'config' / 'bbpp' / 'BBPP_Master.json'
        
        self.config_path = Path(config_path)
        self.rules = []
        self.sets = {}
        self.metadata = {}
        
        self.load_rules()
    
    def load_rules(self) -> bool:
        """
        Cargar reglas desde el archivo JSON
        
        Returns:
            True si se cargó correctamente
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.metadata = data.get('metadata', {})
            self.sets = data.get('sets', {})
            self.rules = data.get('rules', [])
            
            print(f"✅ Cargadas {len(self.rules)} reglas desde {self.config_path.name}")
            return True
            
        except FileNotFoundError:
            print(f"❌ No se encontró {self.config_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Error al parsear JSON: {e}")
            return False
    
    def save_rules(self) -> bool:
        """
        Guardar reglas al archivo JSON
        
        Returns:
            True si se guardó correctamente
        """
        try:
            data = {
                'metadata': self.metadata,
                'sets': self.sets,
                'rules': self.rules
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Reglas guardadas en {self.config_path.name}")
            return True
            
        except Exception as e:
            print(f"❌ Error al guardar reglas: {e}")
            return False
    
    def get_all_rules(self) -> List[Dict]:
        """Obtener todas las reglas"""
        return self.rules
    
    def get_rules_by_set(self, set_name: str) -> List[Dict]:
        """
        Obtener reglas de un conjunto específico
        
        Args:
            set_name: Nombre del conjunto (UiPath, NTTData)
        
        Returns:
            Lista de reglas que pertenecen al conjunto
        """
        return [rule for rule in self.rules if set_name in rule.get('sets', [])]
    
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
    
    def update_rule(self, rule_id: str, updates: Dict) -> bool:
        """
        Actualizar una regla
        
        Args:
            rule_id: ID de la regla a actualizar
            updates: Diccionario con los campos a actualizar
        
        Returns:
            True si se actualizó correctamente
        """
        for i, rule in enumerate(self.rules):
            if rule.get('id') == rule_id:
                self.rules[i].update(updates)
                return True
        return False
    
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
        param = parameters.get(param_name, {})
        return param.get('value')
    
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
            
        self.sets[set_name]['dependencies'] = dependencies
        return True


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
