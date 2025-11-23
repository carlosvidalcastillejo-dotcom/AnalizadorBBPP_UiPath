"""
Script de testing para la pantalla de configuración
Prueba las nuevas funciones de configuración
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import (
    load_user_config, save_user_config, reset_to_defaults,
    get_threshold, set_threshold, get_validation_option, set_validation_option,
    get_output_option, set_output_option, get_custom_logo, set_custom_logo
)

def test_load_save_config():
    """Test 1: Cargar y guardar configuración"""
    print("\n" + "="*60)
    print("TEST 1: Cargar y Guardar Configuración")
    print("="*60)
    
    config = load_user_config()
    print(f"✅ Configuración cargada")
    print(f"   - Versión: {config.get('version', 'N/A')}")
    print(f"   - Última actualización: {config.get('last_updated', 'N/A')}")
    
    # Intentar guardar
    if save_user_config(config):
        print("✅ Configuración guardada correctamente")
    else:
        print("❌ Error al guardar configuración")
        return False
    
    return True


def test_thresholds():
    """Test 2: Funciones de umbrales"""
    print("\n" + "="*60)
    print("TEST 2: Funciones de Umbrales")
    print("="*60)
    
    # Obtener umbral
    max_activities = get_threshold("max_activities_sequence")
    print(f"✅ Umbral actual (max_activities_sequence): {max_activities}")
    
    # Modificar umbral
    new_value = 25
    if set_threshold("max_activities_sequence", new_value):
        print(f"✅ Umbral modificado a: {new_value}")
    else:
        print("❌ Error al modificar umbral")
        return False
    
    # Verificar cambio
    current_value = get_threshold("max_activities_sequence")
    if current_value == new_value:
        print(f"✅ Cambio verificado: {current_value}")
    else:
        print(f"❌ Error: valor esperado {new_value}, obtenido {current_value}")
        return False
    
    # Restaurar valor original
    set_threshold("max_activities_sequence", max_activities)
    print(f"✅ Valor restaurado a: {max_activities}")
    
    return True


def test_validations():
    """Test 3: Funciones de validaciones"""
    print("\n" + "="*60)
    print("TEST 3: Funciones de Validaciones")
    print("="*60)
    
    # Obtener validación
    validate_prefixes = get_validation_option("validate_variable_prefixes")
    print(f"✅ Validación actual (validate_variable_prefixes): {validate_prefixes}")
    
    # Cambiar validación
    new_value = not validate_prefixes
    if set_validation_option("validate_variable_prefixes", new_value):
        print(f"✅ Validación cambiada a: {new_value}")
    else:
        print("❌ Error al cambiar validación")
        return False
    
    # Verificar cambio
    current_value = get_validation_option("validate_variable_prefixes")
    if current_value == new_value:
        print(f"✅ Cambio verificado: {current_value}")
    else:
        print(f"❌ Error: valor esperado {new_value}, obtenido {current_value}")
        return False
    
    # Restaurar valor original
    set_validation_option("validate_variable_prefixes", validate_prefixes)
    print(f"✅ Valor restaurado a: {validate_prefixes}")
    
    return True


def test_output_options():
    """Test 4: Funciones de opciones de salida"""
    print("\n" + "="*60)
    print("TEST 4: Funciones de Opciones de Salida")
    print("="*60)
    
    # Obtener opción
    generate_html = get_output_option("generate_html")
    print(f"✅ Opción actual (generate_html): {generate_html}")
    
    # Cambiar opción
    new_value = not generate_html
    if set_output_option("generate_html", new_value):
        print(f"✅ Opción cambiada a: {new_value}")
    else:
        print("❌ Error al cambiar opción")
        return False
    
    # Verificar cambio
    current_value = get_output_option("generate_html")
    if current_value == new_value:
        print(f"✅ Cambio verificado: {current_value}")
    else:
        print(f"❌ Error: valor esperado {new_value}, obtenido {current_value}")
        return False
    
    # Restaurar valor original
    set_output_option("generate_html", generate_html)
    print(f"✅ Valor restaurado a: {generate_html}")
    
    return True


def test_logo():
    """Test 5: Funciones de logo personalizado"""
    print("\n" + "="*60)
    print("TEST 5: Funciones de Logo Personalizado")
    print("="*60)
    
    # Obtener logo actual
    current_logo = get_custom_logo()
    print(f"✅ Logo actual: {current_logo}")
    
    # Establecer logo personalizado (ruta ficticia para test)
    test_logo_path = Path("/test/logo.png")
    if set_custom_logo(test_logo_path):
        print(f"✅ Logo personalizado establecido: {test_logo_path}")
    else:
        print("❌ Error al establecer logo")
        return False
    
    # Restaurar logo por defecto
    if set_custom_logo(None):
        print("✅ Logo restaurado a valor por defecto")
    else:
        print("❌ Error al restaurar logo")
        return False
    
    return True


def test_reset_defaults():
    """Test 6: Restaurar valores por defecto"""
    print("\n" + "="*60)
    print("TEST 6: Restaurar Valores por Defecto")
    print("="*60)
    
    # Guardar configuración actual
    original_config = load_user_config()
    print("✅ Configuración original guardada")
    
    # Modificar algunos valores
    set_threshold("max_activities_sequence", 999)
    set_validation_option("validate_variable_prefixes", False)
    print("✅ Valores modificados temporalmente")
    
    # Restaurar a valores por defecto
    if reset_to_defaults():
        print("✅ Valores restaurados a por defecto")
    else:
        print("❌ Error al restaurar valores")
        return False
    
    # Verificar restauración
    config = load_user_config()
    if config.get("thresholds", {}).get("max_activities_sequence") == 20:
        print("✅ Verificación: umbral restaurado correctamente")
    else:
        print("❌ Error: umbral no restaurado correctamente")
        return False
    
    # Restaurar configuración original
    save_user_config(original_config)
    print("✅ Configuración original restaurada")
    
    return True


def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "="*60)
    print("INICIANDO TESTS DE PANTALLA DE CONFIGURACIÓN")
    print("="*60)
    
    tests = [
        ("Cargar y Guardar Configuración", test_load_save_config),
        ("Umbrales", test_thresholds),
        ("Validaciones", test_validations),
        ("Opciones de Salida", test_output_options),
        ("Logo Personalizado", test_logo),
        ("Restaurar Valores por Defecto", test_reset_defaults)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ ERROR en test '{test_name}': {e}")
            results.append((test_name, False))
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE TESTS")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASADO" if result else "❌ FALLADO"
        print(f"{status}: {test_name}")
    
    print(f"\n{'='*60}")
    print(f"RESULTADO FINAL: {passed}/{total} tests pasados")
    print(f"{'='*60}\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
