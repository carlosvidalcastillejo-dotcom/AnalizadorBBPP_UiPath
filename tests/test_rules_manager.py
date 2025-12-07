#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test rapido de RulesManager con arquitectura modular"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.rules_manager import RulesManager

def test_rules_manager():
    print("=" * 60)
    print("TEST: RulesManager con Arquitectura Modular")
    print("=" * 60)

    # Cargar RulesManager
    rm = RulesManager()
    print("\nOK: RulesManager cargado correctamente")

    # Obtener informacion de conjuntos
    info = rm.get_sets_info()
    print(f"\nConjuntos disponibles: {list(info.keys())}")

    for name, data in info.items():
        print(f"\n  {name}:")
        print(f"    - Reglas: {data['rules_count']}")
        print(f"    - Activo: {'SI' if data['enabled'] else 'NO'}")
        print(f"    - Dependencias: {len(data['dependencies'])}")

    # Probar get_rules_by_set
    print("\n" + "=" * 60)
    print("TEST: get_rules_by_set()")
    print("=" * 60)

    for set_name in info.keys():
        rules = rm.get_rules_by_set(set_name)
        print(f"\n{set_name}: {len(rules)} reglas")
        if rules:
            print(f"  Primera regla: {rules[0]['id']} - {rules[0]['name']}")

    # Estadisticas
    print("\n" + "=" * 60)
    print("ESTADISTICAS GENERALES")
    print("=" * 60)
    stats = rm.get_statistics()
    print(f"\n  Total reglas: {stats['total_rules']}")
    print(f"  Activas: {stats['enabled_rules']}")
    print(f"  Implementadas: {stats['implemented_rules']}")
    print(f"  Pendientes: {stats['pending_rules']}")

    print("\nOK: TODOS LOS TESTS PASARON CORRECTAMENTE")

if __name__ == '__main__':
    test_rules_manager()
