"""
Script para corregir el campo 'sets' en archivos BBPP

Problema: Las reglas en BBPP_X.json tienen el campo 'sets' incorrecto,
causando que al modificar una regla en un conjunto, se modifique en otro.

Solución: Asegurar que cada regla en BBPP_X.json tenga "sets": ["X"]
"""

import json
from pathlib import Path

def fix_sets_field():
    """Corregir campo 'sets' en todos los archivos BBPP"""

    # Ruta a archivos BBPP
    bbpp_dir = Path(__file__).parent.parent / 'config' / 'bbpp'

    # Buscar archivos BBPP_*.json (excepto Master)
    bbpp_files = [f for f in bbpp_dir.glob('BBPP_*.json')
                 if f.name != 'BBPP_Master.json']

    if not bbpp_files:
        print("ERROR: No se encontraron archivos BBPP")
        return False

    for bbpp_file in bbpp_files:
        # Extraer nombre del conjunto (BBPP_UiPath.json -> UiPath)
        set_name = bbpp_file.stem.replace('BBPP_', '')

        print(f"\n>> Procesando: {bbpp_file.name}")
        print(f"   Conjunto: {set_name}")

        # Cargar JSON
        with open(bbpp_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Contar reglas corregidas
        corrected = 0
        total = len(data.get('rules', []))

        # Corregir campo 'sets' en cada regla
        for rule in data.get('rules', []):
            current_sets = rule.get('sets', [])

            # El 'sets' correcto es simplemente el nombre del conjunto actual
            correct_sets = [set_name]

            if current_sets != correct_sets:
                rule['sets'] = correct_sets
                corrected += 1
                print(f"   OK Corregida regla {rule['id']}: {current_sets} -> {correct_sets}")

        # Guardar archivo corregido
        with open(bbpp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"   COMPLETADO {bbpp_file.name}: {corrected}/{total} reglas corregidas")

    print(f"\nOK Correccion completada")
    return True

if __name__ == '__main__':
    fix_sets_field()
