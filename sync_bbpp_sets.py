#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para sincronizar las 17 reglas del BBPP_Master.json a cada conjunto individual.
Crea archivos independientes para UiPath y NTTData con configuración completa.
"""

import json
from pathlib import Path
from datetime import datetime

def sync_bbpp_sets():
    """Sincroniza las reglas del Master a cada conjunto individual"""
    
    # Rutas de archivos
    config_dir = Path(__file__).parent / "config" / "bbpp"
    master_file = config_dir / "BBPP_Master.json"
    uipath_file = config_dir / "BBPP_UiPath.json"
    nttdata_file = config_dir / "BBPP_NTTData.json"
    
    print("=" * 60)
    print("SINCRONIZACIÓN DE CONJUNTOS BBPP")
    print("=" * 60)
    
    # Cargar Master
    print(f"\n📖 Leyendo {master_file.name}...")
    with open(master_file, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    rules = master_data.get('rules', [])
    sets_metadata = master_data.get('sets', {})
    
    print(f"   ✓ {len(rules)} reglas encontradas")
    print(f"   ✓ {len(sets_metadata)} conjuntos definidos: {', '.join(sets_metadata.keys())}")
    
    # Crear conjunto UiPath
    print(f"\n📝 Creando {uipath_file.name}...")
    uipath_data = {
        "metadata": {
            "name": "Buenas Prácticas UiPath",
            "description": "Reglas oficiales de UiPath",
            "version": "2.0.0",
            "author": "Carlos Vidal Castillejo",
            "company": "Your Company",
            "created": datetime.now().strftime("%Y-%m-%d"),
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "changelog": "v2.0.0: Sincronización completa con 17 reglas del Master"
        },
        "enabled": True,
        "dependencies": sets_metadata.get('UiPath', {}).get('dependencies', {}),
        "rules": rules  # Copia completa de las 17 reglas
    }
    
    with open(uipath_file, 'w', encoding='utf-8') as f:
        json.dump(uipath_data, f, indent=2, ensure_ascii=False)
    
    print(f"   ✓ {len(uipath_data['rules'])} reglas escritas")
    print(f"   ✓ {len(uipath_data['dependencies'])} dependencias configuradas")
    
    # Crear conjunto NTTData
    print(f"\n📝 Creando {nttdata_file.name}...")
    nttdata_data = {
        "metadata": {
            "name": "Buenas Prácticas NTT Data",
            "description": "Estándares personalizados de NTT Data",
            "version": "2.0.0",
            "author": "Carlos Vidal Castillejo",
            "company": "Your Company",
            "created": datetime.now().strftime("%Y-%m-%d"),
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "changelog": "v2.0.0: Sincronización completa con 17 reglas del Master"
        },
        "enabled": True,
        "dependencies": sets_metadata.get('NTTData', {}).get('dependencies', {}),
        "rules": rules  # Copia completa de las 17 reglas
    }
    
    with open(nttdata_file, 'w', encoding='utf-8') as f:
        json.dump(nttdata_data, f, indent=2, ensure_ascii=False)
    
    print(f"   ✓ {len(nttdata_data['rules'])} reglas escritas")
    print(f"   ✓ {len(nttdata_data['dependencies'])} dependencias configuradas")
    
    print("\n" + "=" * 60)
    print("✅ SINCRONIZACIÓN COMPLETADA")
    print("=" * 60)
    print(f"\nArchivos creados:")
    print(f"  • {uipath_file}")
    print(f"  • {nttdata_file}")
    print(f"\nAhora cada conjunto tiene las 17 reglas completas.")
    print(f"Puedes personalizar la configuración de cada conjunto de forma independiente.")

if __name__ == "__main__":
    sync_bbpp_sets()
