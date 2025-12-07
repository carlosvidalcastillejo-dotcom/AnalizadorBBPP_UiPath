# 🧪 Instrucciones para Probar el Instalador

## ✅ Instalador Compilado Exitosamente

**Archivo:** `AnalizadorBBPP_Installer.exe`  
**Tamaño:** 13.98 MB  
**Ubicación:** Raíz del proyecto

---

## 🎯 Opciones para Probar

### Opción 1: Prueba Visual (Sin Instalación Real)

**Recomendado para ver la interfaz sin instalar nada**

1. **Ejecuta el instalador:**
   ```bash
   .\AnalizadorBBPP_Installer.exe
   ```

2. **Navega por las páginas:**
   - Página 1: Bienvenida - Verás las 8 características
   - Página 2: Opciones - Configura opciones (pero NO instales aún)
   - Click "Cancelar" para salir sin instalar

3. **Verifica:**
   - ✅ La interfaz se ve correctamente
   - ✅ Los botones funcionan
   - ✅ El diseño es atractivo
   - ✅ No hay errores al abrir

---

### Opción 2: Instalación de Prueba (Requiere GitHub)

**Para probar la instalación completa**

#### Preparación:

1. **Hacer el repositorio público temporalmente:**
   - Ve a GitHub → Settings → Danger Zone
   - Change visibility → Public
   - Confirma

2. **O crear una release:**
   ```bash
   git add .
   git commit -m "feat: Sistema de instalador"
   git push origin main
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```
   
   Luego en GitHub:
   - Releases → Create new release
   - Tag: v1.0.0
   - Publish release

#### Instalación:

1. **Ejecuta el instalador:**
   ```bash
   .\AnalizadorBBPP_Installer.exe
   ```

2. **Sigue el proceso:**
   - Página 1: Click "Siguiente"
   - Página 2: Configura opciones
     - Cambia la ruta a: `C:\Temp\AnalizadorBBPP_Test`
     - Desmarca "Iniciar al completar" (para evitar conflictos)
   - Click "Instalar"
   - Espera la descarga e instalación
   - Verifica que completa exitosamente

3. **Verifica la instalación:**
   ```bash
   dir C:\Temp\AnalizadorBBPP_Test
   ```
   
   Deberías ver:
   - Carpeta `src/`
   - Carpeta `config/`
   - Archivo `installation_config.json`
   - Acceso directo en el escritorio (si lo marcaste)

---

### Opción 3: Prueba Rápida con Mock (Sin GitHub)

**Para probar sin conexión a GitHub**

Voy a crear una versión modificada del instalador que simula la descarga:

1. **Edita temporalmente** `installer/git_downloader.py`:
   
   Busca la función `download_from_github_release` y añade al inicio:
   ```python
   # MODO PRUEBA - Simular descarga exitosa
   if True:  # Cambiar a False para descarga real
       self._report_progress("MODO PRUEBA: Simulando descarga...", 50)
       import time
       time.sleep(2)
       self._report_progress("MODO PRUEBA: Descarga simulada completada", 100)
       return True
   ```

2. **Recompila:**
   ```bash
   cd installer
   python build_installer.py
   ```

3. **Prueba el instalador** - Ahora simulará la descarga sin conectar a GitHub

---

## 🎬 Demostración Paso a Paso

### 1. Ejecutar el Instalador
```bash
# Desde la raíz del proyecto
.\AnalizadorBBPP_Installer.exe
```

### 2. Página de Bienvenida
- Verás el header azul con "🚀 Bienvenido al Instalador"
- Grid de 8 características en 2 columnas
- Botones: [Cancelar] [Siguiente →]

**Acción:** Click en "Siguiente →"

### 3. Página de Opciones
- Campo de ruta de instalación
- 4 checkboxes de opciones
- Botones: [← Atrás] [Instalar]

**Acción:** 
- Cambia la ruta a `C:\Temp\AnalizadorBBPP_Test`
- Desmarca "Iniciar al completar"
- Click en "Instalar"

### 4. Página de Instalación
- Verás la barra de progreso
- Mensajes de estado en tiempo real
- Log detallado con scroll

**Proceso:**
1. Conectando con GitHub... (10%)
2. Descargando archivos... (30-70%)
3. Extrayendo archivos... (75%)
4. Instalando dependencias... (85%)
5. Creando accesos directos... (92%)
6. ¡Instalación completada! (100%)

### 5. Página de Finalización
- Header verde con "✅ ¡Instalación Completada!"
- Ruta de instalación
- Resumen de acciones
- Botones: [🚀 Iniciar Aplicación] [Finalizar]

**Acción:** Click en "Finalizar"

---

## 🐛 Solución de Problemas

### Error: "No se puede descargar el repositorio"

**Causa:** El repositorio es privado o no existe la release

**Solución:**
1. Hacer el repo público temporalmente
2. O crear una release en GitHub
3. O usar el modo de prueba (Opción 3)

### Error: "No se pueden crear accesos directos"

**Causa:** Falta pywin32

**Solución:**
```bash
pip install pywin32
python -m pywin32_postinstall -install
```

### El instalador no abre

**Causa:** Windows Defender puede bloquearlo

**Solución:**
1. Click derecho → Propiedades
2. Desbloquear
3. O añadir excepción en Windows Defender

---

## ✅ Checklist de Prueba

### Prueba Visual (Sin Instalación)
- [ ] El instalador abre correctamente
- [ ] Página de Bienvenida se ve bien
- [ ] Las 8 características se muestran correctamente
- [ ] Botón "Siguiente" funciona
- [ ] Página de Opciones se carga
- [ ] Botón "Examinar" abre diálogo
- [ ] Checkboxes funcionan
- [ ] Botón "Cancelar" cierra el instalador

### Prueba de Instalación Completa
- [ ] Descarga desde GitHub funciona
- [ ] Barra de progreso se actualiza
- [ ] Log muestra mensajes correctos
- [ ] Archivos se extraen correctamente
- [ ] Accesos directos se crean
- [ ] Página de finalización se muestra
- [ ] Instalación en la ruta correcta

### Verificación Post-Instalación
- [ ] Carpeta de instalación existe
- [ ] Archivos src/ y config/ presentes
- [ ] installation_config.json creado
- [ ] Acceso directo en escritorio (si se marcó)
- [ ] Acceso directo en menú inicio (si se marcó)

---

## 📝 Notas Importantes

### Para Distribución Real:

1. **Crear una release en GitHub** con el código fuente
2. **El instalador descargará** automáticamente esa release
3. **Los usuarios solo necesitan** el archivo .exe del instalador
4. **No necesitas redistribuir** el instalador para cada actualización

### Para Desarrollo:

1. **Usa el modo de prueba** (Opción 3) para probar sin GitHub
2. **Prueba primero visualmente** antes de instalar
3. **Usa una ruta de prueba** como `C:\Temp\` para no afectar tu instalación actual

---

## 🚀 Próximos Pasos

Después de probar el instalador:

1. **Si funciona correctamente:**
   - Crear release en GitHub
   - Distribuir el instalador
   - ¡Listo!

2. **Si necesitas ajustes:**
   - Edita `installer/config_installer.json` para cambiar textos
   - Edita `installer/installer_gui.py` para cambiar colores
   - Recompila con `python build_installer.py`

---

## 💡 Recomendación

**Para la primera prueba, te recomiendo:**

1. Ejecutar el instalador
2. Ver la interfaz (Páginas 1 y 2)
3. Click en "Cancelar" para salir
4. Verificar que todo se ve bien
5. Luego decidir si hacer una instalación completa

**Comando:**
```bash
.\AnalizadorBBPP_Installer.exe
```

¡Disfruta probando tu nuevo instalador profesional! 🎉
