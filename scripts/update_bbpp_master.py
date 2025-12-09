import json
from pathlib import Path

# Cargar BBPP_Master.json
bbpp_path = Path(r"c:\Users\Imrik\Documents\Proyectos Git\AnalizadorBBPP_UiPath\config\bbpp\BBPP_Master.json")
with open(bbpp_path, 'r', encoding='utf-8') as f:
    bbpp_data = json.load(f)

# Nueva regla NOMENCLATURA_005
new_rule = {
    "id": "NOMENCLATURA_005",
    "name": "Variables en PascalCase",
    "description": "Las variables deben seguir el patrón PascalCase (primera letra mayúscula, cada palabra inicia con mayúscula)",
    "category": "nomenclatura",
    "severity": "warning",
    "penalty": 2,
    "enabled": False,
    "sets": ["UiPath", "NTTData"],
    "implementation_status": "implemented",
    "rule_type": "variable_naming_pascal"
}

# Insertar después de NOMENCLATURA_004 (índice 3)
bbpp_data['rules'].insert(4, new_rule)

# Actualizar NOMENCLATURA_003 para añadir parámetros de formato
for rule in bbpp_data['rules']:
    if rule['id'] == 'NOMENCLATURA_003':
        rule['description'] = "Los argumentos deben tener prefijos según su dirección (in_, out_, io_) y seguir el formato especificado después del prefijo"
        rule['parameters']['validate_format_after_prefix'] = True
        rule['parameters']['format_after_prefix'] = "camelCase"  # Por defecto camelCase
        break

# Actualizar metadata
bbpp_data['metadata']['version'] = "2.2.0"
bbpp_data['metadata']['last_updated'] = "2025-11-28"
bbpp_data['metadata']['changelog'] = "v2.2.0: Añadida regla PascalCase para variables y validación de formato en argumentos"

# Guardar
with open(bbpp_path, 'w', encoding='utf-8') as f:
    json.dump(bbpp_data, f, indent=2, ensure_ascii=False)

print("✅ BBPP_Master.json actualizado correctamente")
print(f"✅ Total de reglas: {len(bbpp_data['rules'])}")
print("✅ Nueva regla NOMENCLATURA_005 añadida")
print("✅ NOMENCLATURA_003 actualizada con parámetros de formato")
