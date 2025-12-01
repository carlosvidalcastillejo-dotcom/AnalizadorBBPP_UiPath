# 🚀 Guía Rápida - Sistema de Instalador

## ⚡ Inicio Rápido (5 minutos)

### 1️⃣ Compilar el Instalador
```bash
cd installer
python build_installer.py
```

**Resultado:** `AnalizadorBBPP_Installer.exe` (~12 MB)

---

### 2️⃣ Probar el Instalador
```bash
# Ejecutar el instalador
.\AnalizadorBBPP_Installer.exe
```

**Flujo:**
1. Página de bienvenida → Click "Siguiente"
2. Configurar opciones → Click "Instalar"
3. Esperar descarga e instalación
4. ¡Listo!

---

### 3️⃣ Integrar Auto-Actualización en la App
```bash
# Desde la raíz del proyecto
python installer\integrate_updater.py
```

**Esto copia:**
- `updater.py` → `src/`
- `git_downloader.py` → `src/`
- `config_installer.json` → `config/`

---

### 4️⃣ Añadir Menú de Actualización

Editar `src/ui/main_window.py`:

```python
# Añadir al menú
def create_help_menu(self):
    help_menu = tk.Menu(self.menubar, tearoff=0)
    self.menubar.add_cascade(label="Ayuda", menu=help_menu)
    help_menu.add_command(
        label="Buscar actualizaciones",
        command=self.check_for_updates
    )

# Añadir método
def check_for_updates(self):
    from updater import Updater, UpdateDialog
    import os
    
    install_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    updater = Updater(install_path)
    update_info = updater.check_for_updates()
    
    if update_info:
        dialog = UpdateDialog(update_info, updater)
        dialog.show()
    else:
        from tkinter import messagebox
        messagebox.showinfo("Actualizaciones", "Ya tienes la última versión.")
```

---

### 5️⃣ Crear Release en GitHub

```bash
# 1. Commit y push
git add .
git commit -m "feat: Sistema de instalador y auto-actualización"
git push origin main

# 2. Crear tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 3. En GitHub:
# - Ve a "Releases"
# - Click "Create a new release"
# - Selecciona el tag v1.0.0
# - Añade título y descripción
# - Publish release
```

---

### 6️⃣ Distribuir

**Opción A: Subir a GitHub**
- Sube `AnalizadorBBPP_Installer.exe` como asset de la release
- Comparte el link de descarga

**Opción B: Compartir Directamente**
- Envía `AnalizadorBBPP_Installer.exe` por email/drive
- Los usuarios lo ejecutan
- El instalador descarga la última versión desde GitHub

---

## 🎯 Características Implementadas

### ✅ Instalador
- [x] Interfaz visual moderna con 4 páginas
- [x] Descarga automática desde GitHub
- [x] Barra de progreso en tiempo real
- [x] Creación de accesos directos (escritorio + menú inicio)
- [x] Instalación de dependencias Python
- [x] Configuración personalizable

### ✅ Auto-Actualización
- [x] Verificación de nuevas versiones
- [x] Descarga e instalación automática
- [x] Backup antes de actualizar
- [x] Restauración si falla
- [x] Preserva configuración y datos
- [x] Diálogo visual con changelog

---

## 📦 Archivos Importantes

```
installer/
├── main_installer.py          # Punto de entrada
├── installer_gui.py            # Interfaz gráfica (4 páginas)
├── git_downloader.py           # Descarga desde GitHub
├── updater.py                  # Auto-actualización
├── config_installer.json       # Configuración
├── build_installer.py          # Compilar a .exe
└── README.md                   # Documentación completa

Raíz del proyecto:
├── AnalizadorBBPP_Installer.exe       # ⭐ Instalador compilado
└── SISTEMA_INSTALADOR_COMPLETO.md     # Documentación completa
```

---

## 🔧 Comandos Útiles

### Compilar Instalador
```bash
cd installer
python build_installer.py
```

### Integrar en App Principal
```bash
python installer\integrate_updater.py
```

### Probar Instalador
```bash
.\AnalizadorBBPP_Installer.exe
```

### Limpiar Build
```bash
cd installer
rmdir /s /q build dist
del installer.spec
```

---

## 🐛 Solución Rápida de Problemas

### Error: "No module named 'pyinstaller'"
```bash
pip install pyinstaller pywin32
```

### Error: "No se puede descargar el repositorio"
- Verifica conexión a internet
- Comprueba URL del repositorio en `config_installer.json`
- Si es privado, considera hacerlo público

### Error al crear accesos directos
```bash
pip install pywin32
python -m pywin32_postinstall -install
```

### El instalador no encuentra Python
- Asegúrate de que Python está en el PATH
- O incluye Python en el instalador (avanzado)

---

## 💡 Tips

### Reducir Tamaño del Instalador
- Ya es pequeño (~12 MB)
- Descarga la app desde GitHub (no la incluye)
- Usa UPX para comprimir más (ya incluido)

### Personalizar Apariencia
- Edita colores en `installer_gui.py`
- Añade logo en `resources/`
- Modifica textos en `config_installer.json`

### Añadir Icono
1. Crea `resources/icon.ico`
2. Edita `build_installer.py`:
   ```python
   icon='resources/icon.ico'
   ```

---

## 📞 Ayuda

- **Documentación completa:** `installer/README.md`
- **Resumen del sistema:** `SISTEMA_INSTALADOR_COMPLETO.md`
- **Ejemplos de código:** `installer/integration_example.py`

---

## ✅ Checklist Final

Antes de distribuir:

- [ ] Compilar instalador
- [ ] Probar instalación completa
- [ ] Verificar accesos directos
- [ ] Probar auto-actualización
- [ ] Crear release en GitHub
- [ ] Documentar changelog
- [ ] Distribuir instalador

---

**¡Listo para usar!** 🎉

El sistema está **100% funcional**. Solo compila, prueba y distribuye.
