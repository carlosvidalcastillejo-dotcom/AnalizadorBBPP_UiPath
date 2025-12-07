# Script para arreglar main_window.py eliminando código duplicado
import shutil

# Hacer backup
shutil.copy('src/ui/main_window.py', 'src/ui/main_window.py.backup')

# Leer archivo
with open('src/ui/main_window.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Eliminar líneas duplicadas (1125-1373)
# Mantener solo líneas 1-1124 y desde 1374 en adelante
clean_lines = lines[:1124] + lines[1373:]

# Escribir archivo limpio
with open('src/ui/main_window.py', 'w', encoding='utf-8') as f:
    f.writelines(clean_lines)

print(f"✅ Archivo limpiado")
print(f"   Líneas originales: {len(lines)}")
print(f"   Líneas finales: {len(clean_lines)}")
print(f"   Líneas eliminadas: {len(lines) - len(clean_lines)}")
