#!/usr/bin/env python3
"""
Script de compilación del Analizador BBPP UiPath
Pregunta configuración antes de compilar
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Importar módulos de versionado
try:
    from src.version_manager import (
        get_current_version,
        increment_version,
        suggest_version_bump,
        update_version_in_config
    )
    from src.release_notes_generator import (
        create_simple_changelog_entry,
        update_changelog
    )
    from src.change_detector import (
        get_change_summary,
        format_changes_for_preview
    )
    VERSION_MANAGER_AVAILABLE = True
except ImportError:
    VERSION_MANAGER_AVAILABLE = False
    print("⚠️  Módulos de versionado no disponibles")

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Imprimir cabecera"""
    print(Colors.HEADER + "=" * 70 + Colors.END)
    print(Colors.HEADER + Colors.BOLD + "  COMPILADOR - Analizador BBPP UiPath" + Colors.END)
    print(Colors.HEADER + "=" * 70 + Colors.END)
    print()

def get_changelog_description_interactive(bump_type: str = 'patch') -> str:
    """Obtener descripción de changelog con detección automática y preview editable"""
    print(Colors.BLUE + "📝 Generación de Descripción de Cambios" + Colors.END)
    print()
    
    # Detectar cambios automáticamente
    if VERSION_MANAGER_AVAILABLE:
        try:
            project_root = Path(__file__).parent
            summary = get_change_summary(project_root, hours=24)
            
            if summary['total_files'] > 0:
                print(Colors.YELLOW + f"🔍 Detectados {summary['total_files']} archivos modificados en las últimas 24h" + Colors.END)
                print()
                
                # Mostrar preview
                print(Colors.GREEN + "📋 PREVIEW DE CAMBIOS DETECTADOS:" + Colors.END)
                print(Colors.GREEN + "=" * 70 + Colors.END)
                print(summary['description'])
                print(Colors.GREEN + "=" * 70 + Colors.END)
                print()
                
                # Preguntar si quiere editar
                print(Colors.YELLOW + "Opciones:" + Colors.END)
                print("  1. Usar descripción generada automáticamente")
                print("  2. Editar descripción (se abrirá editor de texto)")
                print("  3. Escribir descripción manualmente (una línea)")
                print("  4. Omitir descripción")
                print("  0. Cancelar compilación")
                
                opcion = input("\n   Seleccione (1/2/3/4/0) [1]: ").strip()
                
                if opcion == '0':
                    print(Colors.RED + "\n❌ Compilación cancelada por el usuario" + Colors.END)
                    sys.exit(0)
                elif opcion == '2':
                    # Editar en archivo temporal
                    import tempfile
                    import subprocess
                    
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
                        f.write(summary['description'])
                        temp_path = f.name
                    
                    try:
                        # Abrir en notepad (Windows)
                        subprocess.run(['notepad', temp_path], check=True)
                        
                        # Leer contenido editado
                        with open(temp_path, 'r', encoding='utf-8') as f:
                            edited_desc = f.read().strip()
                        
                        os.unlink(temp_path)
                        return edited_desc
                    except Exception as e:
                        print(Colors.YELLOW + f"⚠️  Error al abrir editor: {e}" + Colors.END)
                        return summary['description']
                
                elif opcion == '3':
                    desc = input("\n   Ingrese descripción: ").strip()
                    return desc if desc else summary['description']
                
                elif opcion == '4':
                    return ""
                
                else:  # Opción 1 o Enter
                    return summary['description']
            else:
                print(Colors.YELLOW + "ℹ️  No se detectaron cambios recientes" + Colors.END)
                print()
        except Exception as e:
            print(Colors.YELLOW + f"⚠️  Error al detectar cambios: {e}" + Colors.END)
            print()
    
    # Fallback: pedir descripción manual
    desc = input("   Descripción breve para CHANGELOG.md (Enter para omitir): ").strip()
    return desc

def ask_build_config():
    """Preguntar configuración de compilación con auto-versionado"""
    print(Colors.BLUE + "📋 Configuración de la Compilación" + Colors.END)
    print()
    
    # Cargar configuración de usuario para obtener autor guardado
    user_config_path = Path('config/user_config.json')
    saved_author = "Carlos Vidal Castillejo"
    
    if user_config_path.exists():
        try:
            with open(user_config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                saved_author = user_config.get('build_author', saved_author)
        except:
            pass
    
    # Autor
    print(Colors.YELLOW + "👤 Autor del Build:" + Colors.END)
    autor = input(f"   Ingrese su nombre completo (Enter para '{saved_author}', 0 para cancelar): ").strip()
    if autor == '0':
        print(Colors.RED + "\n❌ Compilación cancelada por el usuario" + Colors.END)
        sys.exit(0)
    if not autor:
        autor = saved_author
    
    print()
    
    # Versión con auto-incremento
    if VERSION_MANAGER_AVAILABLE:
        try:
            config_path = Path('src/config.py')
            current_version = get_current_version(config_path)
            suggestions = suggest_version_bump(current_version)
            
            print(Colors.YELLOW + f"🔢 Versión Actual: {current_version}" + Colors.END)
            print(Colors.YELLOW + "   Seleccione tipo de build:" + Colors.END)
            print(f"   1. Patch  ({current_version} → {suggestions['patch']})  - Correcciones de bugs")
            print(f"   2. Minor  ({current_version} → {suggestions['minor']})  - Nuevas funcionalidades")
            print(f"   3. Major  ({current_version} → {suggestions['major']})  - Cambios importantes")
            print(f"   4. Custom - Ingresar versión manualmente")
            print(f"   5. Recompilar ({current_version}) - Sin cambios de versión ni changelog")
            print(f"   0. Cancelar compilación")
            
            version_opcion = input("   Seleccione (1/2/3/4/5/0) [1]: ").strip()
            
            if version_opcion == '0':
                print(Colors.RED + "\n❌ Compilación cancelada por el usuario" + Colors.END)
                sys.exit(0)
            elif version_opcion == '1' or version_opcion == '':
                nueva_version = suggestions['patch']
                bump_type = 'patch'
            elif version_opcion == '2':
                nueva_version = suggestions['minor']
                bump_type = 'minor'
            elif version_opcion == '3':
                nueva_version = suggestions['major']
                bump_type = 'major'
            elif version_opcion == '4':
                nueva_version = input(f"   Ingrese nueva versión (0 para cancelar): ").strip()
                if nueva_version == '0':
                    print(Colors.RED + "\n❌ Compilación cancelada por el usuario" + Colors.END)
                    sys.exit(0)
                if not nueva_version:
                    nueva_version = current_version
                bump_type = 'custom'
            elif version_opcion == '5':
                nueva_version = current_version
                bump_type = 'recompile'
            else:
                nueva_version = current_version
                bump_type = 'none'
        except Exception as e:
            print(Colors.YELLOW + f"⚠️  Error al obtener versión: {e}" + Colors.END)
            from src.config import APP_VERSION
            current_version = APP_VERSION
            nueva_version = input(f"   Nueva versión (Enter para mantener {current_version}, 0 para cancelar): ").strip()
            if nueva_version == '0':
                print(Colors.RED + "\n❌ Compilación cancelada por el usuario" + Colors.END)
                sys.exit(0)
            if not nueva_version:
                nueva_version = current_version
            bump_type = 'custom'
    else:
        # Fallback si no está disponible version_manager
        from src.config import APP_VERSION
        print(Colors.YELLOW + f"🔢 Versión Actual: {APP_VERSION}" + Colors.END)
        nueva_version = input(f"   Nueva versión (Enter para mantener {APP_VERSION}, 0 para cancelar): ").strip()
        if nueva_version == '0':
            print(Colors.RED + "\n❌ Compilación cancelada por el usuario" + Colors.END)
            sys.exit(0)
        if not nueva_version:
            nueva_version = APP_VERSION
        bump_type = 'custom'
    
    print()
    
    # Descripción de cambios para changelog (solo si no es recompile)
    if bump_type == 'recompile':
        changelog_desc = ""  # No generar changelog para recompilaciones
    else:
        changelog_desc = get_changelog_description_interactive(bump_type)
    
    print()
    
    # Tipo de versión
    print(Colors.YELLOW + "🏷️  Tipo de Versión:" + Colors.END)
    print("   1. Beta")
    print("   2. Release Candidate (RC)")
    print("   3. Release Estable")
    print("   0. Cancelar compilación")
    tipo_opcion = input("   Seleccione (1/2/3/0) [1]: ").strip()
    
    if tipo_opcion == '0':
        print(Colors.RED + "\n❌ Compilación cancelada por el usuario" + Colors.END)
        sys.exit(0)
    
    tipo_map = {
        '1': 'Beta',
        '2': 'RC',
        '3': 'Release',
        '': 'Beta'
    }
    version_type = tipo_map.get(tipo_opcion, 'Beta')
    
    print()
    
    # Fecha de compilación
    build_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    build_date_short = datetime.now().strftime("%Y-%m-%d")
    
    # Resumen
    print()
    print(Colors.GREEN + "=" * 70 + Colors.END)
    print(Colors.GREEN + Colors.BOLD + "  RESUMEN DE CONFIGURACIÓN" + Colors.END)
    print(Colors.GREEN + "=" * 70 + Colors.END)
    print(f"  👤 Autor:           {autor}")
    print(f"  🔢 Versión:         {nueva_version}")
    if bump_type != 'none' and bump_type != 'custom':
        print(f"  📈 Tipo de cambio:  {bump_type.capitalize()}")
    print(f"  🏷️  Tipo:            {version_type}")
    print(f"  📅 Fecha Build:     {build_date}")
    if changelog_desc:
        print(f"  📝 Changelog:       {changelog_desc[:50]}..." if len(changelog_desc) > 50 else f"  📝 Changelog:       {changelog_desc}")
    print(Colors.GREEN + "=" * 70 + Colors.END)
    print()
    
    confirmar = input(Colors.YELLOW + "¿Proceder con la compilación? (s/n) [s]: " + Colors.END).strip().lower()
    if confirmar and confirmar != 's':
        print(Colors.RED + "\n❌ Compilación cancelada" + Colors.END)
        sys.exit(0)
    
    return {
        'autor': autor,
        'version': nueva_version,
        'version_type': version_type,
        'build_date': build_date,
        'build_date_short': build_date_short,
        'bump_type': bump_type,
        'changelog_description': changelog_desc
    }

def update_config_file(config):
    """Actualizar archivo de configuración con los valores de compilación"""
    config_path = Path(__file__).parent / 'src' / 'config.py'
    
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Usar regex para reemplazar valores (funciona con cualquier versión actual)
    import re
    
    # Reemplazar APP_VERSION
    content = re.sub(
        r'APP_VERSION\s*=\s*["\'][^"\']+["\']',
        f'APP_VERSION = "{config["version"]}"',
        content
    )
    
    # Reemplazar APP_VERSION_TYPE
    content = re.sub(
        r'APP_VERSION_TYPE\s*=\s*["\'][^"\']+["\'](\s*#.*)?',
        f'APP_VERSION_TYPE = "{config["version_type"]}"\\1',
        content
    )
    
    # Reemplazar APP_AUTHOR
    content = re.sub(
        r'APP_AUTHOR\s*=\s*["\'][^"\']+["\'](\s*#.*)?',
        f'APP_AUTHOR = "{config["autor"]}"\\1',
        content
    )
    
    # Reemplazar BUILD_DATE
    content = re.sub(
        r'BUILD_DATE\s*=\s*[^#\n]+(\s*#.*)?',
        f'BUILD_DATE = "{config["build_date"]}"\\1',
        content
    )
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(Colors.GREEN + "✅ Configuración actualizada en src/config.py" + Colors.END)

def create_build_info():
    """Crear archivo con información del build"""
    from src.config import APP_VERSION, APP_VERSION_TYPE, APP_AUTHOR, BUILD_DATE
    
    build_info = {
        'version': APP_VERSION,
        'version_type': APP_VERSION_TYPE,
        'author': APP_AUTHOR,
        'build_date': BUILD_DATE,
        'company': 'NTT Data'
    }
    
    build_info_path = Path(__file__).parent / 'build_info.json'
    with open(build_info_path, 'w', encoding='utf-8') as f:
        json.dump(build_info, f, indent=2, ensure_ascii=False)
    
    print(Colors.GREEN + "✅ Información del build guardada en build_info.json" + Colors.END)

def update_changelog_file(config):
    """Actualizar CHANGELOG.md con nueva entrada"""
    # No actualizar changelog si es recompilación
    if config.get('bump_type') == 'recompile':
        print(Colors.YELLOW + "ℹ️  Recompilación: No se actualiza CHANGELOG.md" + Colors.END)
        return
    
    if not VERSION_MANAGER_AVAILABLE:
        print(Colors.YELLOW + "⚠️  Módulos de changelog no disponibles, omitiendo actualización" + Colors.END)
        return
    
    try:
        # Crear entrada de changelog
        entry = create_simple_changelog_entry(
            version=config['version'],
            date=config['build_date_short'],
            author=config['autor'],
            description=config.get('changelog_description', ''),
            bump_type=config.get('bump_type', 'custom')
        )
        
        # Actualizar CHANGELOG.md
        changelog_path = Path(__file__).parent / 'CHANGELOG.md'
        update_changelog(entry, changelog_path, create_if_missing=True)
        
        print(Colors.GREEN + "✅ CHANGELOG.md actualizado" + Colors.END)
    except Exception as e:
        print(Colors.YELLOW + f"⚠️  Error al actualizar CHANGELOG.md: {e}" + Colors.END)

def save_author_to_config(author: str):
    """Guardar autor en user_config.json para próximas compilaciones"""
    try:
        user_config_path = Path('config/user_config.json')
        
        # Leer config actual
        if user_config_path.exists():
            with open(user_config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
        else:
            user_config = {}
        
        # Actualizar autor
        user_config['build_author'] = author
        user_config['last_updated'] = datetime.now().strftime("%Y-%m-%d")
        
        # Guardar
        with open(user_config_path, 'w', encoding='utf-8') as f:
            json.dump(user_config, f, indent=2, ensure_ascii=False)
        
        print(Colors.GREEN + f"✅ Autor '{author}' guardado en configuración" + Colors.END)
    except Exception as e:
        print(Colors.YELLOW + f"⚠️  Error al guardar autor: {e}" + Colors.END)

def compile_with_pyinstaller():
    """Compilar con PyInstaller"""
    print()
    print(Colors.BLUE + "🔨 Compilando con PyInstaller..." + Colors.END)
    print()
    
    import subprocess
    
    # Comando de PyInstaller
    cmd = [
        'pyinstaller',
        '--onefile',  # Un solo archivo ejecutable
        '--windowed',  # Sin consola (para GUI)
        '--name', 'AnalizadorBBPP_UiPath',
    ]
    
    # Añadir icono solo si existe
    icon_path = Path('assets/icon.ico')
    if icon_path.exists():
        cmd.extend(['--icon', str(icon_path)])
    
    # Añadir resto de argumentos
    cmd.extend([
        '--add-data', 'src;src',  # Usar ; en Windows
        '--add-data', 'config;config',
        '--hidden-import', 'tkinter',
        'run.py'
    ])
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(Colors.GREEN + "✅ Compilación exitosa!" + Colors.END)
        print(Colors.GREEN + "📦 Ejecutable generado en: dist/AnalizadorBBPP_UiPath.exe" + Colors.END)
        return True
    except subprocess.CalledProcessError as e:
        print(Colors.RED + f"❌ Error en compilación: {e}" + Colors.END)
        print(Colors.RED + e.stderr + Colors.END)
        return False
    except FileNotFoundError:
        print(Colors.YELLOW + "⚠️  PyInstaller no está instalado" + Colors.END)
        print(Colors.YELLOW + "   Instálalo con: pip install pyinstaller" + Colors.END)
        return False

def main():
    """Función principal"""
    print_header()
    
    # Verificar que estamos en el directorio correcto
    if not Path('src').exists() or not Path('run.py').exists():
        print(Colors.RED + "❌ Error: Ejecuta este script desde la raíz del proyecto" + Colors.END)
        sys.exit(1)
    
    # Preguntar configuración
    config = ask_build_config()
    
    # Actualizar archivo de configuración
    print()
    print(Colors.BLUE + "📝 Actualizando configuración..." + Colors.END)
    update_config_file(config)
    
    # Actualizar CHANGELOG.md
    update_changelog_file(config)
    
    # Guardar autor en configuración de usuario
    save_author_to_config(config['autor'])
    
    # Crear archivo de info del build
    create_build_info()
    
    print()
    print(Colors.BLUE + "🎯 ¿Deseas compilar ahora? (requiere PyInstaller)" + Colors.END)
    compilar = input("   (s/n) [n]: ").strip().lower()
    
    if compilar == 's':
        if compile_with_pyinstaller():
            print()
            print(Colors.GREEN + Colors.BOLD + "🎉 ¡BUILD COMPLETADO CON ÉXITO!" + Colors.END)
        else:
            print()
            print(Colors.YELLOW + "⚠️  Configuración actualizada pero compilación falló" + Colors.END)
            print(Colors.YELLOW + "   Puedes compilar manualmente con:" + Colors.END)
            print(Colors.YELLOW + "   pyinstaller --onefile --windowed run.py" + Colors.END)
    else:
        print()
        print(Colors.GREEN + "✅ Configuración actualizada" + Colors.END)
        print(Colors.BLUE + "   Compila manualmente cuando estés listo con:" + Colors.END)
        print(Colors.BLUE + "   python build.py" + Colors.END)
    
    print()
    print(Colors.HEADER + "=" * 70 + Colors.END)
    print(Colors.HEADER + "  Gracias por usar el Analizador BBPP UiPath - NTT Data" + Colors.END)
    print(Colors.HEADER + "=" * 70 + Colors.END)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print(Colors.RED + "\n❌ Compilación cancelada por el usuario" + Colors.END)
        sys.exit(0)
