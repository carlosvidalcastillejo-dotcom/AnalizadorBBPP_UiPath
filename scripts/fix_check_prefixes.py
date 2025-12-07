import json
from pathlib import Path

# Cargar BBPP_Master.json
bbpp_path = Path(r"c:\Users\Imrik\Documents\Proyectos Git\AnalizadorBBPP_UiPath\config\bbpp\BBPP_Master.json")
with open(bbpp_path, 'r', encoding='utf-8') as f:
    bbpp_data = json.load(f)

# Actualizar NOMENCLATURA_003 para asegurar que tiene check_prefixes
for rule in bbpp_data['rules']:
    if rule['id'] == 'NOMENCLATURA_003':
        if 'parameters' not in rule:
            rule['parameters'] = {}
        
        # Asegurar que tiene todos los parámetros necesarios
        if 'check_prefixes' not in rule['parameters']:
            rule['parameters']['check_prefixes'] = True
        
        print(f"✅ NOMENCLATURA_003 actualizada:")
        print(f"   Parámetros: {rule['parameters']}")
        break

# Guardar
with open(bbpp_path, 'w', encoding='utf-8') as f:
    json.dump(bbpp_data, f, indent=2, ensure_ascii=False)

print("\n✅ BBPP_Master.json actualizado correctamente")
