#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para sincronizar las reglas del BBPP_Master.json a cada conjunto individual.
VERSIÓN DINÁMICA: Sincroniza a TODOS los conjuntos definidos en BBPP_Master.json
"""

import json
from pathlib import Path
from datetime import datetime

def sync_bbpp_sets():
    """Sincroniza las reglas del Master a TODOS los conjuntos individuales dinámicamente"""

    # Rutas de archivos
    config_dir = Path(__file__).parent / "config" / "bbpp"
    master_file = config_dir / "BBPP_Master.json"

    print("=" * 60)
    print("SINCRONIZACIÓN DINÁMICA DE CONJUNTOS BBPP")
    print("=" * 60)

    # Cargar Master
    print(f"\n📖 Leyendo {master_file.name}...")
    with open(master_file, 'r', encoding='utf-8') as f:
        master_data = json.load(f)

    rules = master_data.get('rules', [])
    sets_metadata = master_data.get('sets', {})

    print(f"   ✓ {len(rules)} reglas encontradas")
    print(f"   ✓ {len(sets_metadata)} conjuntos definidos: {', '.join(sets_metadata.keys())}")

    created_files = []

    # Iterar dinámicamente sobre TODOS los conjuntos definidos en Master
    for set_name, set_info in sets_metadata.items():
        output_file = config_dir / f"BBPP_{set_name}.json"

        print(f"\n📝 Sincronizando conjunto: {set_name}")
        print(f"   Archivo: {output_file.name}")

        # Construir datos del conjunto
        set_data = {
            "metadata": {
                "name": set_info.get('name', f"Buenas Prácticas {set_name}"),
                "description": set_info.get('description', f"Estándares de {set_name}"),
                "version": "2.0.0",
                "author": "Carlos Vidal Castillejo",
                "company": "Your Company",
                "created": datetime.now().strftime("%Y-%m-%d"),
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "changelog": "v2.0.0: Sincronización automática con Master"
            },
            "enabled": set_info.get('enabled', True),
            "dependencies": set_info.get('dependencies', {}),
            "rules": rules  # Copia completa de las reglas
        }

        # Guardar archivo
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(set_data, f, indent=2, ensure_ascii=False)

        print(f"   ✓ {len(set_data['rules'])} reglas escritas")
        print(f"   ✓ {len(set_data['dependencies'])} dependencias configuradas")
        print(f"   ✓ Estado: {'Activo' if set_data['enabled'] else 'Inactivo'}")

        created_files.append(output_file)

    print("\n" + "=" * 60)
    print("✅ SINCRONIZACIÓN COMPLETADA")
    print("=" * 60)
    print(f"\nArchivos sincronizados ({len(created_files)}):")
    for f in created_files:
        print(f"  • {f.name}")
    print(f"\nCada conjunto ahora tiene las {len(rules)} reglas completas.")
    print(f"Puedes personalizar la configuración de cada conjunto de forma independiente.")

if __name__ == "__main__":
    sync_bbpp_sets()
