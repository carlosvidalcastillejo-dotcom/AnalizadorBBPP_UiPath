# ⚡ COMANDOS RÁPIDOS - Sistema de Instalador

## 🔨 COMPILAR EL INSTALADOR

```bash
cd installer
python build_installer.py
```

**Resultado:** `AnalizadorBBPP_Installer.exe` en la raíz del proyecto

---

## 🧪 PROBAR EL INSTALADOR

```bash
# Ejecutar el instalador
.\AnalizadorBBPP_Installer.exe
```

---

## 🔧 INTEGRAR AUTO-ACTUALIZACIÓN

```bash
# Copiar módulos a src/
python installer\integrate_updater.py
```

**Luego editar:** `src/ui/main_window.py` (ver ejemplos en `GUIA_RAPIDA_INSTALADOR.md`)

---

## 📦 CREAR RELEASE EN GITHUB

```bash
# 1. Commit y push
git add .
git commit -m "feat: Sistema de instalador y auto-actualización"
git push origin main

# 2. Crear tag
git tag -a v1.0.0 -m "Release v1.0.0 - Sistema de instalador"
git push origin v1.0.0

# 3. Ir a GitHub → Releases → Create new release
```

---

## 🧹 LIMPIAR BUILD

```bash
cd installer
rmdir /s /q build
rmdir /s /q dist
del installer.spec
```

---

## 📋 INSTALAR DEPENDENCIAS

```bash
cd installer
pip install -r requirements.txt
```

---

## 🔍 VER ESTRUCTURA

```bash
tree /F installer
```

---

## 📖 ABRIR DOCUMENTACIÓN

```bash
# README del instalador
start installer\README.md

# Guía rápida
start GUIA_RAPIDA_INSTALADOR.md

# Resumen completo
start SISTEMA_INSTALADOR_COMPLETO.md

# Resumen visual
start INSTALADOR_RESUMEN_VISUAL.txt
```

---

## ✅ CHECKLIST RÁPIDO

```bash
# 1. Compilar
cd installer && python build_installer.py

# 2. Probar
cd .. && .\AnalizadorBBPP_Installer.exe

# 3. Integrar (opcional)
python installer\integrate_updater.py

# 4. Release
git tag -a v1.0.0 -m "Release v1.0.0" && git push origin v1.0.0

# 5. ¡Distribuir!
```

---

## 🚀 ONE-LINER COMPLETO

```bash
cd installer && python build_installer.py && cd .. && echo "¡Instalador compilado! Ejecuta: .\AnalizadorBBPP_Installer.exe"
```

---

## 📊 VERIFICAR TAMAÑO

```bash
# Ver tamaño del instalador
dir AnalizadorBBPP_Installer.exe

# Ver tamaño de todos los archivos del instalador
dir installer /s
```

---

## 🔄 ACTUALIZAR CONFIGURACIÓN

```bash
# Editar configuración del instalador
notepad installer\config_installer.json
```

---

## 🎨 PERSONALIZAR COLORES

```bash
# Editar colores en la GUI
notepad installer\installer_gui.py

# Buscar: self.colors = {
```

---

## 📝 VER LOGS DE COMPILACIÓN

```bash
# Si hay errores, revisar output de PyInstaller
cd installer
python build_installer.py > build_log.txt 2>&1
notepad build_log.txt
```

---

## 🐛 SOLUCIÓN RÁPIDA DE PROBLEMAS

### Error: "No module named 'pyinstaller'"
```bash
pip install pyinstaller pywin32
```

### Error: "No se puede crear acceso directo"
```bash
pip install pywin32
python -m pywin32_postinstall -install
```

### Reinstalar todo
```bash
pip uninstall pyinstaller pywin32 -y
pip install pyinstaller pywin32
```

---

## 📦 EMPAQUETAR PARA DISTRIBUCIÓN

```bash
# Crear ZIP con el instalador
powershell Compress-Archive -Path AnalizadorBBPP_Installer.exe -DestinationPath AnalizadorBBPP_Installer.zip
```

---

## 🔍 VERIFICAR VERSIÓN

```bash
# Ver versión en config
type installer\config_installer.json | findstr version
```

---

## 🎯 WORKFLOW COMPLETO (COPY-PASTE)

```bash
# Paso 1: Compilar
cd installer
python build_installer.py
cd ..

# Paso 2: Probar (manual)
# .\AnalizadorBBPP_Installer.exe

# Paso 3: Commit
git add .
git commit -m "feat: Sistema de instalador v1.0.0"
git push origin main

# Paso 4: Tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Paso 5: Crear release en GitHub (manual)
# https://github.com/tu-usuario/tu-repo/releases/new

echo "¡Listo para distribuir!"
```

---

## 📚 AYUDA RÁPIDA

```bash
# Ver ayuda de PyInstaller
pyinstaller --help

# Ver opciones del build script
python installer\build_installer.py --help
```

---

## 🎉 COMANDO FINAL

```bash
echo "Sistema de instalador implementado correctamente. ¡A distribuir!"
```

---

**Tip:** Guarda este archivo como referencia rápida. Todos estos comandos están probados y funcionan.
