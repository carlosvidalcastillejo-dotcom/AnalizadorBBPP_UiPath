# 🚀 Instalador Analizador BBPP UiPath

Sistema de instalación profesional con auto-actualización para el Analizador de Buenas Prácticas UiPath.

## 📋 Características del Instalador

### ✨ Funcionalidades Principales

- **🎨 Interfaz Moderna y Atractiva**
  - Diseño visual profesional con efectos hover
  - Múltiples páginas (Bienvenida, Opciones, Instalación, Finalización)
  - Barra de progreso en tiempo real
  - Log detallado de instalación

- **📥 Descarga Automática desde Git**
  - Descarga la última versión desde GitHub automáticamente
  - No requiere autenticación (usa releases públicas)
  - Fallback a git clone si es necesario
  - Barra de progreso durante la descarga

- **⚙️ Opciones Personalizables**
  - Selección de ruta de instalación
  - Crear acceso directo en escritorio
  - Crear acceso directo en menú Inicio
  - Iniciar aplicación al finalizar
  - Habilitar auto-actualización

- **🔄 Sistema de Auto-Actualización**
  - Verifica automáticamente nuevas versiones
  - Descarga e instala actualizaciones
  - Crea backup antes de actualizar
  - Restaura automáticamente si falla
  - Preserva configuración y datos del usuario

- **🛡️ Seguridad**
  - No almacena credenciales en texto plano
  - Usa GitHub Personal Access Tokens (opcional)
  - Repositorio público no requiere autenticación
  - Backups automáticos antes de actualizar

## 🗂️ Estructura del Instalador

```
installer/
├── main_installer.py          # Punto de entrada del instalador
├── installer_gui.py            # Interfaz gráfica moderna
├── git_downloader.py           # Descarga desde GitHub
├── updater.py                  # Sistema de auto-actualización
├── config_installer.json       # Configuración del instalador
├── build_installer.py          # Script para compilar a .exe
├── resources/                  # Recursos (iconos, imágenes)
│   └── (vacío por ahora)
└── README.md                   # Este archivo
```

## 🔨 Compilar el Instalador

### Requisitos

- Python 3.8 o superior
- PyInstaller
- pywin32

### Pasos para Compilar

1. **Navegar al directorio del instalador:**
   ```bash
   cd installer
   ```

2. **Ejecutar el script de compilación:**
   ```bash
   python build_installer.py
   ```

3. **El script automáticamente:**
   - Verifica e instala dependencias necesarias
   - Crea el archivo .spec para PyInstaller
   - Compila el instalador a .exe
   - Limpia archivos temporales
   - Copia el ejecutable a la raíz del proyecto

4. **Resultado:**
   - `installer/dist/AnalizadorBBPP_Installer.exe` (en carpeta dist)
   - `AnalizadorBBPP_Installer.exe` (copiado a la raíz)

## 📦 Distribución

### Opción 1: Instalador Standalone (Recomendado)

Distribuye solo el archivo `AnalizadorBBPP_Installer.exe`:
- ✅ Tamaño pequeño (~10-15 MB)
- ✅ Descarga automáticamente la última versión
- ✅ Siempre instala la versión más reciente
- ✅ No requiere redistribuir para actualizaciones

### Opción 2: Instalador + Aplicación Empaquetada

Si quieres incluir la aplicación en el instalador:
1. Modifica `config_installer.json`
2. Cambia `use_releases` a `false`
3. Incluye los archivos de la aplicación en el instalador

## 🎯 Flujo de Instalación

```
1. Usuario ejecuta: AnalizadorBBPP_Installer.exe
   ↓
2. Página de Bienvenida
   - Muestra características principales
   - Descripción de la aplicación
   ↓
3. Página de Opciones
   - Seleccionar ubicación de instalación
   - Configurar accesos directos
   - Opciones de auto-actualización
   ↓
4. Página de Instalación
   - Descarga desde GitHub
   - Instala dependencias Python
   - Crea accesos directos
   - Muestra progreso en tiempo real
   ↓
5. Página de Finalización
   - Confirmación de instalación exitosa
   - Opción para iniciar aplicación
   ↓
6. ¡Aplicación instalada y lista para usar!
```

## 🔄 Sistema de Auto-Actualización

### Cómo Funciona

1. **Verificación Automática:**
   - Al iniciar la aplicación (si está habilitado)
   - Consulta la API de GitHub para la última release

2. **Notificación al Usuario:**
   - Diálogo visual con información de la actualización
   - Muestra changelog y novedades
   - Usuario decide si actualizar ahora o más tarde

3. **Proceso de Actualización:**
   - Crea backup de la instalación actual
   - Descarga nueva versión
   - Instala actualización preservando config y datos
   - Si falla, restaura automáticamente el backup

4. **Configuración:**
   - Se puede habilitar/deshabilitar desde la aplicación
   - Configuración guardada en `installation_config.json`

### Uso Programático

```python
from updater import Updater

# Crear instancia del actualizador
updater = Updater(install_path="C:\\Program Files\\AnalizadorBBPP")

# Verificar actualizaciones
update_info = updater.check_for_updates()

if update_info:
    print(f"Nueva versión: {update_info['version']}")
    
    # Actualizar
    success = updater.update(progress_callback=my_callback)
    
    if success:
        print("Actualización completada")
```

## ⚙️ Configuración

### Archivo: `config_installer.json`

```json
{
  "app_info": {
    "name": "Analizador BBPP UiPath",
    "version": "1.0.0",
    "author": "Carlos Vidal Castillejo",
    "description": "..."
  },
  "git_config": {
    "repository_url": "https://github.com/...",
    "branch": "main",
    "use_releases": true,
    "fallback_to_clone": true
  },
  "installation": {
    "default_path": "C:\\Program Files\\AnalizadorBBPP",
    "create_desktop_shortcut": true,
    "create_start_menu_shortcut": true,
    "auto_update_enabled": true,
    "launch_after_install": true
  },
  "features": [
    {
      "icon": "✅",
      "title": "...",
      "description": "..."
    }
  ]
}
```

### Personalización

Para personalizar el instalador:

1. **Cambiar información de la app:**
   - Edita `app_info` en `config_installer.json`

2. **Configurar repositorio Git:**
   - Edita `git_config` con tu URL de repositorio

3. **Modificar características mostradas:**
   - Edita el array `features` en la configuración

4. **Añadir icono personalizado:**
   - Coloca tu icono en `resources/icon.ico`
   - Actualiza `build_installer.py` para incluirlo

## 🎨 Características Visuales

### Página de Bienvenida

- **Header atractivo** con gradiente azul
- **Título principal** con emoji y texto grande
- **Descripción** de la aplicación
- **Grid de características** en 2 columnas con:
  - ✅ Análisis de Buenas Prácticas
  - ⚙️ Configuración Personalizada
  - 📊 Reportes Profesionales
  - 📈 Dashboard de Métricas
  - 🎨 Branding Personalizable
  - 🔄 Auto-actualización
  - 📦 Gestión de Conjuntos BBPP
  - 🛡️ Sistema de Excepciones

### Página de Opciones

- **Campo de ruta** con botón "Examinar"
- **Checkboxes estilizados** para opciones
- **Botones modernos** con efectos hover

### Página de Instalación

- **Barra de progreso** animada
- **Porcentaje** en tiempo real
- **Log detallado** con scroll
- **Mensajes de estado** descriptivos

### Página de Finalización

- **Confirmación visual** con check verde
- **Resumen** de lo instalado
- **Botones** para finalizar o iniciar app

## 🐛 Solución de Problemas

### El instalador no descarga el repositorio

1. Verifica tu conexión a internet
2. Comprueba que la URL del repositorio es correcta
3. Si el repositorio es privado, considera hacerlo público o usar tokens

### Error al crear accesos directos

1. Verifica que tienes permisos de escritorio
2. Instala `pywin32`: `pip install pywin32`
3. Ejecuta el instalador como administrador

### La actualización falla

1. El sistema crea automáticamente un backup
2. Si falla, restaura el backup automáticamente
3. Verifica espacio en disco suficiente
4. Comprueba permisos de escritura en la carpeta de instalación

## 📝 Notas Importantes

### Ventajas del Sistema

- ✅ **Instalador pequeño**: Solo ~10-15 MB
- ✅ **Siempre actualizado**: Descarga la última versión
- ✅ **Fácil distribución**: Un solo archivo .exe
- ✅ **Auto-actualización**: Los usuarios siempre tienen la última versión
- ✅ **Seguro**: Backups automáticos antes de actualizar

### Consideraciones

- ⚠️ Requiere conexión a internet para instalar
- ⚠️ El repositorio debe ser público o usar tokens para privados
- ⚠️ Las actualizaciones preservan config pero no código modificado
- ⚠️ Requiere Python instalado en el sistema del usuario (o incluir Python en el instalador)

## 🚀 Próximos Pasos

1. **Compilar el instalador:**
   ```bash
   python build_installer.py
   ```

2. **Probar el instalador:**
   - Ejecuta `AnalizadorBBPP_Installer.exe`
   - Verifica que descarga correctamente
   - Prueba la instalación completa

3. **Crear una release en GitHub:**
   - Tag la versión (ej: v1.0.0)
   - Sube el código fuente
   - El instalador descargará automáticamente esta release

4. **Distribuir el instalador:**
   - Comparte `AnalizadorBBPP_Installer.exe`
   - Los usuarios lo ejecutan y listo

## 📞 Soporte

Para problemas o sugerencias:
- Abre un issue en el repositorio de GitHub
- Contacta al desarrollador: Carlos Vidal Castillejo

---

**Última actualización:** 1 de Diciembre de 2024
**Versión del Instalador:** 1.0.0
