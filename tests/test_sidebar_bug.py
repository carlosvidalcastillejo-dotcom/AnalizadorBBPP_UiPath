"""
Script de prueba para detectar el bug del sidebar que desaparece
Simula las acciones del usuario para reproducir el problema
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import tkinter as tk
from src.ui.main_window import MainWindow

def test_sidebar_persistence():
    """
    Prueba para verificar que el sidebar no desaparece
    """
    print("=" * 60)
    print("🧪 TEST: Persistencia del Sidebar")
    print("=" * 60)
    
    # Crear ventana principal
    print("\n1️⃣ Creando MainWindow...")
    app = MainWindow()
    
    # Forzar actualización de UI para que Tkinter renderice todo
    app.root.update_idletasks()
    app.root.update()
    
    # Verificar que el sidebar existe
    print("\n2️⃣ Verificando sidebar inicial...")
    assert hasattr(app, 'sidebar'), "❌ ERROR: No existe app.sidebar"
    assert app.sidebar.winfo_exists(), "❌ ERROR: Sidebar no existe en Tkinter"
    
    # Verificar visibilidad (puede no ser visible inmediatamente)
    if not app.sidebar.winfo_viewable():
        print(f"⚠️ WARNING: Sidebar no visible inicialmente")
        print(f"   - Manager: {app.sidebar.winfo_manager()}")
        print(f"   - Geometry: {app.sidebar.winfo_geometry()}")
        # No es error crítico si no es visible inmediatamente
    else:
        print("✅ Sidebar inicial OK")
    
    # Simular navegación entre pantallas
    print("\n3️⃣ Navegando entre pantallas...")
    
    screens = [
        ("Análisis", app._show_analysis_screen),
        ("Gestión de BBPP", app._show_bbpp_management_screen),
        ("Configuración", app._show_config_screen),
        ("Métricas", app._show_metrics_dashboard),
    ]
    
    for screen_name, screen_func in screens:
        print(f"\n   📄 Mostrando pantalla: {screen_name}")
        try:
            screen_func()
            app.root.update()  # Forzar actualización de UI
            
            # Verificar que el sidebar sigue existiendo
            if not app.sidebar.winfo_exists():
                print(f"❌ ERROR: Sidebar desapareció al mostrar {screen_name}")
                return False
            
            if not app.sidebar.winfo_viewable():
                print(f"⚠️ WARNING: Sidebar no es visible después de mostrar {screen_name}")
                print(f"   - Manager: {app.sidebar.winfo_manager()}")
                print(f"   - Geometry: {app.sidebar.winfo_geometry()}")
                return False
            
            print(f"   ✅ Sidebar OK después de {screen_name}")
            
        except Exception as e:
            print(f"❌ ERROR al mostrar {screen_name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # Simular refresh del sidebar
    print("\n4️⃣ Probando refresh_sidebar()...")
    try:
        app.refresh_sidebar()
        app.root.update()
        
        if not app.sidebar.winfo_exists():
            print("❌ ERROR: Sidebar desapareció después de refresh_sidebar()")
            return False
        
        if not app.sidebar.winfo_viewable():
            print("⚠️ WARNING: Sidebar no es visible después de refresh_sidebar()")
            return False
        
        print("✅ Sidebar OK después de refresh")
        
    except Exception as e:
        print(f"❌ ERROR en refresh_sidebar(): {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✅ TODOS LOS TESTS PASARON - Sidebar persistente")
    print("=" * 60)
    
    # Cerrar ventana
    app.root.destroy()
    return True

def test_sidebar_after_config_save():
    """
    Prueba específica: Sidebar después de guardar configuración
    (Posible escenario donde desaparece)
    """
    print("\n" + "=" * 60)
    print("🧪 TEST: Sidebar después de guardar configuración")
    print("=" * 60)
    
    app = MainWindow()
    
    print("\n1️⃣ Mostrando pantalla de configuración...")
    app._show_config_screen()
    app.root.update()
    
    print("\n2️⃣ Verificando sidebar antes de guardar...")
    assert app.sidebar.winfo_exists(), "❌ Sidebar no existe antes de guardar"
    assert app.sidebar.winfo_viewable(), "❌ Sidebar no visible antes de guardar"
    print("✅ Sidebar OK antes de guardar")
    
    print("\n3️⃣ Simulando guardado de configuración...")
    try:
        # Simular guardado (sin hacer clic en botón)
        app.refresh_sidebar()
        app.root.update()
        
        print("\n4️⃣ Verificando sidebar después de guardar...")
        if not app.sidebar.winfo_exists():
            print("❌ ERROR: Sidebar desapareció después de guardar")
            app.root.destroy()
            return False
        
        if not app.sidebar.winfo_viewable():
            print("⚠️ WARNING: Sidebar no visible después de guardar")
            print(f"   - Manager: {app.sidebar.winfo_manager()}")
            app.root.destroy()
            return False
        
        print("✅ Sidebar OK después de guardar")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        app.root.destroy()
        return False
    
    app.root.destroy()
    return True

if __name__ == "__main__":
    print("\n🚀 Iniciando tests del sidebar...\n")
    
    # Test 1: Persistencia general
    test1_passed = test_sidebar_persistence()
    
    # Test 2: Después de guardar configuración
    test2_passed = test_sidebar_after_config_save()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS")
    print("=" * 60)
    print(f"Test 1 (Persistencia general): {'✅ PASÓ' if test1_passed else '❌ FALLÓ'}")
    print(f"Test 2 (Guardar configuración): {'✅ PASÓ' if test2_passed else '❌ FALLÓ'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 TODOS LOS TESTS PASARON")
        sys.exit(0)
    else:
        print("\n⚠️ ALGUNOS TESTS FALLARON - Revisar logs arriba")
        sys.exit(1)
