"""
Script para compilar el instalador a un ejecutable .exe
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path


def create_spec_file():
    """Crea el archivo .spec para PyInstaller"""
    
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main_installer.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config_installer.json', '.'),
        ('resources', 'resources'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'win32com.client',
        'pythoncom',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AnalizadorBBPP_Installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Puedes añadir un icono aquí
    version_file=None,
)
"""
    
    spec_path = Path(__file__).parent / 'installer.spec'
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"✓ Archivo .spec creado: {spec_path}")
    return spec_path


def check_dependencies():
    """Verifica que las dependencias necesarias estén instaladas"""
    print("\n📦 Verificando dependencias...")
    
    dependencies = [
        'pyinstaller',
        'pywin32',
    ]
    
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ✗ {dep} - NO INSTALADO")
            missing.append(dep)
    
    if missing:
        print(f"\n⚠️  Faltan dependencias. Instalando...")
        for dep in missing:
            print(f"\nInstalando {dep}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], check=True)
        print("\n✓ Todas las dependencias instaladas")
    else:
        print("\n✓ Todas las dependencias están instaladas")


def build_installer():
    """Compila el instalador"""
    print("\n🔨 Compilando instalador...")
    
    installer_dir = Path(__file__).parent
    os.chdir(installer_dir)
    
    # Crear archivo .spec
    spec_file = create_spec_file()
    
    # Ejecutar PyInstaller
    print("\n⏳ Ejecutando PyInstaller (esto puede tardar varios minutos)...")
    
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm',
        str(spec_file)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("\n✅ ¡Instalador compilado exitosamente!")
        
        # Mostrar ubicación del ejecutable
        exe_path = installer_dir / 'dist' / 'AnalizadorBBPP_Installer.exe'
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n📦 Ejecutable generado:")
            print(f"   Ubicación: {exe_path}")
            print(f"   Tamaño: {size_mb:.2f} MB")
            
            # Copiar a la raíz del proyecto para fácil acceso
            root_exe = installer_dir.parent / 'AnalizadorBBPP_Installer.exe'
            shutil.copy2(exe_path, root_exe)
            print(f"\n✓ Copiado también a: {root_exe}")
        else:
            print("\n⚠️  Advertencia: No se encontró el ejecutable en la ubicación esperada")
    else:
        print("\n❌ Error al compilar el instalador:")
        print(result.stderr)
        return False
    
    return True


def clean_build_files():
    """Limpia archivos temporales de compilación"""
    print("\n🧹 Limpiando archivos temporales...")
    
    installer_dir = Path(__file__).parent
    
    dirs_to_clean = ['build', '__pycache__']
    files_to_clean = ['installer.spec']
    
    for dir_name in dirs_to_clean:
        dir_path = installer_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  ✓ Eliminado: {dir_name}/")
    
    for file_name in files_to_clean:
        file_path = installer_dir / file_name
        if file_path.exists():
            file_path.unlink()
            print(f"  ✓ Eliminado: {file_name}")
    
    print("✓ Limpieza completada")


def main():
    """Función principal"""
    print("=" * 60)
    print("🚀 COMPILADOR DE INSTALADOR - Analizador BBPP UiPath")
    print("=" * 60)
    
    try:
        # Verificar dependencias
        check_dependencies()
        
        # Compilar instalador
        if build_installer():
            # Limpiar archivos temporales
            clean_build_files()
            
            print("\n" + "=" * 60)
            print("✅ PROCESO COMPLETADO EXITOSAMENTE")
            print("=" * 60)
            print("\n📝 Próximos pasos:")
            print("   1. Prueba el instalador ejecutando AnalizadorBBPP_Installer.exe")
            print("   2. Distribuye el instalador a los usuarios")
            print("   3. Los usuarios podrán instalar y actualizar la aplicación fácilmente")
            print("\n💡 Nota: El instalador descargará automáticamente la última versión")
            print("   desde GitHub, por lo que no necesitas recompilar el instalador")
            print("   cada vez que actualices la aplicación.")
            
        else:
            print("\n❌ La compilación falló. Revisa los errores anteriores.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Compilación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
