# Analizador BBPP UiPath v0.11.0 Beta
## Documentación Completa y Roadmap

**Autor:** Carlos Vidal Castillejo
**Fecha:** 30 de Noviembre de 2025
**Versión:** 0.11.0 Beta

---

## 📋 ÍNDICE

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Funcionalidades Implementadas](#funcionalidades-implementadas)
3. [Cambios Recientes (Sesión Actual)](#cambios-recientes-sesión-actual)
4. [Arquitectura del Sistema](#arquitectura-del-sistema)
5. [Roadmap de Mejoras](#roadmap-de-mejoras)
6. [Instalación y Configuración](#instalación-y-configuración)

---

## RESUMEN EJECUTIVO

El **Analizador BBPP UiPath** es una herramienta profesional para analizar proyectos UiPath y verificar el cumplimiento de Buenas Prácticas (BBPP). El sistema es completamente configurable, permitiendo personalizar reglas, penalizaciones, excepciones y dependencias según las necesidades de cada organización.

### Características Principales

- ✅ Análisis automatizado de proyectos UiPath
- ✅ Sistema de reglas completamente personalizable
- ✅ Gestión de conjuntos de BBPP (UiPath, NTT Data, Custom)
- ✅ Sistema de excepciones para frameworks oficiales (REFramework)
- ✅ Penalización configurable con 3 modos diferentes
- ✅ Reportes HTML (Normal y Detallado) y Excel
- ✅ Validación de dependencias de paquetes
- ✅ Base de datos de métricas históricas
- ✅ Interfaz gráfica Tkinter profesional

---

## FUNCIONALIDADES IMPLEMENTADAS

### 1. Sistema de Análisis de Proyectos UiPath

**Archivos:** `src/analyzer.py`, `src/project_scanner.py`, `src/xaml_parser.py`

#### Capacidades de Análisis:
- Parseo de archivos XAML
- Detección de actividades y secuencias
- Análisis de variables y argumentos
- Detección de Try-Catch blocks
- Análisis de LogMessages
- Detección de código comentado
- Análisis de selectores
- Validación de timeouts

#### Reglas Implementadas (17 reglas):

**Nomenclatura (5 reglas):**
- `NOMENCLATURA_001`: Variables en camelCase
- `NOMENCLATURA_002`: Evitar nombres genéricos
- `NOMENCLATURA_003`: Argumentos con prefijos (in_, out_, io_)
- `NOMENCLATURA_004`: Argumentos con descripción clara
- `NOMENCLATURA_005`: Variables en PascalCase

**Estructura (3 reglas):**
- `ESTRUCTURA_001`: IFs anidados excesivos
- `ESTRUCTURA_002`: Try-Catch vacíos
- `ESTRUCTURA_003`: Actividades críticas en Try-Catch

**Modularización (3 reglas):**
- `MODULARIZACION_001`: Sequences muy largos
- `MODULARIZACION_002`: Uso de Invoke Workflow
- `MODULARIZACION_003`: Patrón Init/End en State Machines

**Otros (6 reglas):**
- `CODIGO_001`: Código comentado excesivo
- `LOGGING_001`: Logging insuficiente
- `LOGGING_002`: Logging en inicio/fin
- `CONFIGURACION_001`: Uso de Orchestrator Assets
- `RENDIMIENTO_001`: Timeouts explícitos
- `SELECTORES_001`: Selectores dinámicos

### 2. Sistema de Penalización Personalizable ⭐ **NUEVO**

**Archivos:** `src/project_scanner.py`, `config/bbpp/BBPP_Master.json`

#### 3 Modos de Penalización:

**A) Severity Default (Predeterminado por severidad):**
```json
{
  "penalty_mode": "severity_default",
  "penalty_value": 2
}
```
- Usa pesos globales configurables (ERROR=10pts, WARNING=3pts, INFO=0.5pts)
- Cada hallazgo suma según su severidad
- Si `penalty_value = 0`, **no penaliza** (override del modo)

**B) Individual (Cada hallazgo penaliza):**
```json
{
  "penalty_mode": "individual",
  "penalty_value": 2
}
```
- Cada hallazgo suma `penalty_value%`
- Ejemplo: 20 hallazgos × 2% = 40% penalización

**C) Global (Penalización fija total):**
```json
{
  "penalty_mode": "global",
  "penalty_value": 5
}
```
- Penalización fija sin importar cantidad de hallazgos
- Útil para reglas que son "todo o nada"

#### Límite Máximo (Cap):
```json
{
  "use_penalty_cap": true,
  "penalty_cap": 10
}
```
- Solo aplica a modos "severity_default" e "individual"
- Limita la penalización máxima de esa regla
- Ejemplo: 30 hallazgos × 2% = 60%, pero si cap=10% → queda en 10%

### 3. Sistema de Excepciones (REFramework) ⭐ **NUEVO**

**Archivos:** `src/analyzer.py`, `config/bbpp/BBPP_Master.json`

Permite definir nombres de variables/argumentos que deben ignorarse durante la validación.

#### Excepciones Predefinidas (50 excepciones):
```python
# Sin prefijos
Config, TransactionItem, TransactionData, TransactionNumber,
TransactionField1, TransactionField2, TransactionID, RetryNumber,
SystemException, BusinessException, QueueRetry, ConsecutiveSystemExceptions,
ConfigFile, ConfigSheets, Folder, OrchestratorQueueFolder, OrchestratorQueueName,
FilePath

# Con prefijos in_
in_Config, in_TransactionItem, in_TransactionData, in_TransactionNumber,
in_TransactionField1, in_TransactionField2, in_TransactionID,
in_SystemException, in_BusinessException, in_QueueRetry, in_ConfigFile,
in_ConfigSheets, in_Folder, in_OrchestratorQueueFolder, in_OrchestratorQueueName

# Con prefijos out_
out_Config, out_TransactionItem, out_TransactionData, out_TransactionNumber,
out_TransactionField1, out_TransactionField2, out_TransactionID

# Con prefijos io_
io_TransactionItem, io_TransactionData, io_TransactionNumber, io_RetryNumber,
io_SystemException, io_BusinessException, io_QueueRetry,
io_ConsecutiveSystemExceptions, io_FilePath

# Con prefijos compuestos
io_dt_TransactionData
```

#### Gestión de Excepciones en UI:
- Listbox con todas las excepciones actuales
- Botón "Agregar" para nuevas excepciones
- Botón "Eliminar Seleccionado" para borrar excepciones
- Soporte para presionar Enter en el campo de texto

### 4. Gestión de Conjuntos de BBPP

**Archivos:** `src/ui/rules_management_screen.py`, `src/rules_manager.py`

#### Conjuntos Disponibles:
- **UiPath**: Buenas Prácticas oficiales de UiPath
- **NTT Data**: Estándares personalizados de NTT Data
- **Custom**: Posibilidad de crear más conjuntos

#### Funcionalidades:
- Activar/desactivar conjuntos completos
- Asignar reglas a múltiples conjuntos
- Configurar dependencias por conjunto
- Validación automática de versiones de paquetes

#### Dependencias Configurables:
```json
{
  "UiPath": {
    "dependencies": {
      "UiPath.Excel.Activities": "4.4.2",
      "UiPath.System.Activities": "24.10.2",
      "UiPath.Testing.Activities": "24.10.4",
      "UiPath.UIAutomation.Activities": "25.12.10"
    }
  }
}
```

### 5. Sistema de Prefijos de Tipo ⭐ **NUEVO**

**Archivos:** `src/analyzer.py`, `config/bbpp/BBPP_Master.json`

Permite reconocer prefijos de tipo en variables antes de validar nomenclatura.

#### Prefijos Soportados:
```python
dt_    # DataTable
dr_    # DataRow
str_   # String
int_   # Integer
dbl_   # Double
bool_  # Boolean
arr_   # Array
list_  # List
dict_  # Dictionary
obj_   # Object
exc_   # Exception
cfg_   # Configuration
msg_   # Message
```

#### Ejemplos Válidos:
- `dt_Excel` → se valida "Excel" (no "dt_Excel")
- `io_dt_TransactionData` → se valida "TransactionData"
- `str_nombreCliente` → se valida "nombreCliente"

### 6. Interfaz Gráfica Profesional

**Archivos:** `src/ui/main_window.py`, `src/ui/rules_management_screen.py`

#### Pantallas Principales:

**A) Pantalla de Análisis:**
- Selector de proyecto UiPath
- Checkboxes para conjuntos de BBPP
- Botones para generar HTML y Excel
- Área de resultados con scroll

**B) Gestión de Reglas BBPP:**
- Tabla TreeView con 17 reglas
- Columnas: ID, Nombre, Categoría, Severidad, Penalización, Activa, Estado
- Colores por severidad (rojo/amarillo/azul)
- Botones: Guardar Cambios, Recargar, Activar Todas, Desactivar Todas
- Botón "Gestión de Conjuntos" para gestión avanzada

**C) Edición de Regla Individual:**
- Checkbox "Regla Activa"
- Radio buttons para Severidad (ERROR/WARNING/INFO)
- **Configuración de Penalización** (3 modos + límite)
- **Parámetros de la Regla** (según tipo)
- **Prefijos de Tipo** (solo NOMENCLATURA_001, 003, 005)
- **Excepciones** (solo reglas de nomenclatura)
- Checkboxes para Conjuntos (UiPath, NTT Data)

**D) Gestión de Conjuntos:**
- Dropdown para seleccionar conjunto
- Checkbox "Conjunto Activo"
- Botón "Editar Dependencias"
- Lista de reglas con checkboxes para asignar/quitar

**E) Configuración:**
- Branding (logo, nombre empresa, colores)
- Umbrales de scoring (NO USADO - ahora en reglas)
- Otras configuraciones

**F) Métricas:**
- Dashboard con histórico de análisis
- Tabla con todos los análisis realizados
- Estadísticas y gráficos

### 7. Sistema de Reportes

**Archivos:** `src/report_generator.py`, `src/excel_generator.py`

#### Reporte HTML Normal:
- Header con logo y branding
- Score global con calificación (A/B/C/D/F)
- Resumen de hallazgos por severidad
- Tabla de hallazgos agrupados por categoría
- Filtros interactivos por severidad y categoría
- Hallazgos colapsables para mejor UX

#### Reporte HTML Detallado:
- Todo lo del reporte normal, más:
- **Pestaña de Dependencias**: Validación de paquetes instalados vs requeridos
- **Pestaña de Gráficos**: Visualizaciones interactivas (Chart.js)
  - Distribución por severidad (pie chart)
  - Distribución por categoría (bar chart)
  - Top 5 reglas más violadas

#### Reporte Excel:
- Hoja "Resumen" con estadísticas generales
- Hoja "Hallazgos" con tabla detallada
- Formato condicional por severidad
- Filtros automáticos

### 8. Base de Datos de Métricas

**Archivos:** `src/database/metrics_db.py`

#### Tablas:
- `analysis_history`: Histórico de análisis
- `findings`: Hallazgos por análisis
- `project_metrics`: Métricas del proyecto

#### Funcionalidades:
- Guardar automáticamente cada análisis
- Consultar histórico
- Generar estadísticas
- Exportar métricas

### 9. Configuración Global

**Archivos:** `config/config.json`, `config/bbpp/BBPP_Master.json`

#### config.json:
```json
{
  "branding": {
    "company_name": "Your Company",
    "logo_path": null,
    "primary_color": "#0067B1",
    "secondary_color": "#00A3E0"
  },
  "scoring": {
    "error_weight": -10,
    "warning_weight": -3,
    "info_weight": -0.5,
    "scaling_factor": 5
  }
}
```

#### BBPP_Master.json:
- 17 reglas completamente configuradas
- Parámetros personalizables por regla
- Excepciones para REFramework
- Prefijos de tipo
- Asignación a conjuntos

---

## CAMBIOS RECIENTES (SESIÓN ACTUAL)

### 1. Sistema de Excepciones REFramework
- ✅ Documentación técnica creada
- ✅ Backend implementado en `analyzer.py` (5 funciones)
- ✅ UI implementada en `rules_management_screen.py`
- ✅ 50 excepciones predefinidas agregadas al BBPP_Master.json
- ✅ Verificación: Variables estándar del REFramework ya no fallan

### 2. Sistema de Penalización Personalizable
- ✅ Diseño de 3 modos: severity_default, individual, global
- ✅ Implementación de límite máximo (cap)
- ✅ UI completa con radio buttons, spinboxes y checkbox
- ✅ Backend en `project_scanner.py` completamente refactorizado
- ✅ Configuración en todas las 17 reglas
- ✅ **Bug fix**: penalty_value=0 ahora funciona correctamente (no penaliza)

### 3. Ajuste del SCALING_FACTOR
- ✅ Reducido de 25 a 5 para scoring más realista
- ✅ REFramework oficial: de 0% a 70.92% (grado C - Bien)
- ✅ Ahora configurable en `config.json`

### 4. Validación de Dependencias
- ✅ Sistema de validación de paquetes NuGet
- ✅ Configuración por conjunto de BBPP
- ✅ Reporte de dependencias en HTML detallado
- ✅ Estados: OK, Warning, Critical, N/A

### 5. Correcciones de Encoding
- ✅ Eliminados emojis de print() en `rules_manager.py`
- ✅ Eliminados emojis de print() en `project_scanner.py`
- ✅ Solución al problema de codepage 1252 en Windows

### 6. Mejoras en RulesManager
- ✅ Método `get_rule_parameter()` mejorado
- ✅ Soporte para parámetros simples y complejos
- ✅ Métodos de gestión de dependencias

---

## ARQUITECTURA DEL SISTEMA

### Estructura de Carpetas
```
AnalizadorBBPP_UiPath/
├── config/
│   ├── bbpp/
│   │   └── BBPP_Master.json          # Catálogo de reglas
│   └── config.json                    # Configuración global
├── src/
│   ├── ui/
│   │   ├── main_window.py            # Ventana principal
│   │   ├── rules_management_screen.py # Gestión de reglas
│   │   ├── config_screen.py          # Configuración
│   │   └── metrics_dashboard.py      # Dashboard de métricas
│   ├── database/
│   │   └── metrics_db.py             # Base de datos SQLite
│   ├── analyzer.py                   # Motor de análisis
│   ├── project_scanner.py            # Escáner de proyectos
│   ├── xaml_parser.py                # Parser de XAML
│   ├── rules_manager.py              # Gestor de reglas
│   ├── report_generator.py           # Generador HTML
│   ├── excel_generator.py            # Generador Excel
│   └── branding_manager.py           # Gestión de branding
├── output/
│   ├── HTML/                         # Reportes HTML
│   └── Excel/                        # Reportes Excel
├── main.py                           # Punto de entrada
└── requirements.txt                  # Dependencias Python
```

### Flujo de Ejecución

```
1. Usuario selecciona proyecto UiPath
2. Usuario selecciona conjuntos de BBPP (UiPath, NTT Data)
3. ProjectScanner escanea archivos XAML
4. XamlParser parsea cada archivo
5. Analyzer aplica reglas activas del conjunto
6. RulesManager gestiona configuración de reglas
7. ProjectScanner calcula score con penalización personalizada
8. ReportGenerator crea HTML
9. ExcelGenerator crea Excel
10. MetricsDB guarda en base de datos
```

### Tecnologías Utilizadas

- **Python 3.13**
- **Tkinter**: Interfaz gráfica
- **SQLite**: Base de datos
- **openpyxl**: Generación de Excel
- **xml.etree.ElementTree**: Parseo de XAML
- **Pathlib**: Manejo de rutas
- **JSON**: Configuración

---

## ROADMAP DE MEJORAS

### 🔴 PRIORIDAD CRÍTICA (Hacer YA)

#### 1. **BUG CRÍTICO: Panel izquierdo desaparece**
**Problema:** El panel lateral de navegación desaparece en ciertas circunstancias.

**Solución propuesta:**
- Revisar `main_window.py` líneas de gestión del sidebar
- Verificar bindings de eventos de resize
- Asegurar que el frame lateral tiene `pack_propagate(False)`
- Agregar log de debug para detectar cuándo desaparece

**Archivos afectados:**
- `src/ui/main_window.py`

**Estimación:** 1-2 horas

---

### 🔴 ALTA PRIORIDAD

#### 2. **Mejorar UI - Gestión de Conjuntos con Dropdown**
**Estado actual:** Checkboxes estáticos "UiPath" y "NTT Data"

**Mejora propuesta:**
- Reemplazar checkboxes por un **Combobox dropdown** dinámico
- Cargar conjuntos desde `BBPP_Master.json` automáticamente
- Permitir crear nuevos conjuntos desde la UI
- Botón "+ Nuevo Conjunto" que abra un diálogo modal
- Campos del diálogo:
  - Nombre del conjunto
  - Descripción
  - Checkbox "Activo"
  - Botón "Crear"

**Archivos afectados:**
- `src/ui/rules_management_screen.py` (diálogo de gestión de conjuntos)
- `src/rules_manager.py` (método `create_set()`)
- `config/bbpp/BBPP_Master.json` (nueva sección `sets`)

**Estimación:** 4-6 horas

---

#### 3. **Mejorar UI - Selector de Conjunto en Análisis**
**Estado actual:** Checkboxes para cada conjunto

**Mejora propuesta:**
- Reemplazar checkboxes por un **Listbox con selección múltiple** o **CheckedListBox**
- Permitir seleccionar múltiples conjuntos a la vez
- Mostrar descripción del conjunto al hacer hover
- Indicador visual de cuántas reglas tiene cada conjunto

**Archivos afectados:**
- `src/ui/main_window.py` (pantalla de análisis)

**Estimación:** 2-3 horas

---

#### 4. **Interfaz Responsive y Scrollable**
**Problemas actuales:**
- Algunos diálogos se recortan en resoluciones pequeñas
- No hay barras de desplazamiento donde son necesarias
- Widgets se solapan en ventanas pequeñas

**Mejoras propuestas:**
- Agregar `Scrollbar` a todos los frames largos
- Usar `grid` con `sticky` para layout responsive
- Configurar `min_size` y `max_size` en ventanas
- Agregar botón "Volver al Menú Principal" en todas las pantallas

**Archivos afectados:**
- `src/ui/main_window.py`
- `src/ui/rules_management_screen.py`
- `src/ui/config_screen.py`
- `src/ui/metrics_dashboard.py`

**Estimación:** 6-8 horas

---

### 🟡 MEDIA PRIORIDAD

#### 5. **Control de Versiones - Git Integration**
**Tareas:**
- Crear `.gitignore` apropiado
- Inicializar repositorio Git
- Crear commits organizados por feature
- Subir a GitHub/GitLab
- Configurar GitHub Actions para CI/CD

**Archivos nuevos:**
- `.gitignore`
- `.github/workflows/ci.yml`
- `README.md` profesional

**Estimación:** 3-4 horas

---

#### 6. **Compilación y Empaquetado**
**Objetivo:** Generar un ejecutable standalone para Windows

**Herramientas:**
- **PyInstaller** o **cx_Freeze**

**Tareas:**
- Crear `build.spec` para PyInstaller
- Configurar inclusión de recursos (config/, templates/, icons/)
- Generar ejecutable `.exe`
- Crear instalador con **Inno Setup**
- Firmar digitalmente el ejecutable

**Archivos nuevos:**
- `build.spec`
- `installer_script.iss`
- `build_scripts/compile.bat`

**Estimación:** 8-10 horas

---

#### 7. **Sistema de Actualización Automática**
**Funcionalidad:**
- Comprobar versión actual vs versión en GitHub
- Descargar actualizaciones desde Git
- Aplicar parches sin reinstalar
- Notificar al usuario de nuevas versiones

**Implementación:**
- API de GitHub Releases
- Módulo `updater.py`
- Botón "Buscar Actualizaciones" en menú

**Archivos nuevos:**
- `src/updater.py`
- `version.json`

**Estimación:** 6-8 horas

---

#### 8. **Instalador con Descarga de Dependencias**
**Objetivo:** Instalador ligero que descargue componentes desde Git

**Flujo:**
1. Usuario descarga `installer_small.exe` (5-10 MB)
2. Instalador descarga componentes desde GitHub:
   - Python embebido
   - Librerías (openpyxl, etc.)
   - Templates y configuraciones
3. Configura paths y shortcuts
4. Lanza aplicación

**Herramientas:**
- Inno Setup con scripts custom
- PowerShell para descarga de archivos

**Estimación:** 10-12 horas

---

#### 9. **Sistema de Seguridad con Contraseña**
**Objetivo:** Proteger archivos de configuración críticos

**Funcionalidades:**
- Contraseña para acceder a "Gestión de Reglas BBPP"
- Contraseña para editar `BBPP_Master.json`
- Encriptación de archivos sensibles
- Roles: Admin, Analyst, Viewer

**Implementación:**
- Hash de contraseñas con `bcrypt`
- Archivo `users.db` con SQLite
- Decorador `@require_auth` para funciones críticas

**Archivos nuevos:**
- `src/security/auth_manager.py`
- `src/security/encryption.py`
- `data/users.db`

**Estimación:** 8-10 horas

---

### 🟢 BAJA PRIORIDAD / FUTURO

#### 10. **Integración con API de IA**
**Objetivo:** Análisis inteligente de buenas prácticas con IA

**Funcionalidades:**
- Conectar a API gratuita (OpenAI, Anthropic, Google Gemini)
- Configurar contexto de análisis
- Sugerencias automáticas de mejora
- Detección de patrones complejos

**Implementación:**
- Módulo `src/ai_integration/ai_analyzer.py`
- Configuración de API key en `config.json`
- Prompt engineering para análisis de XAML

**APIs gratuitas a evaluar:**
- Google Gemini API (gratis hasta cierto límite)
- Anthropic Claude (tier gratuito)
- OpenAI GPT-3.5 (limitado)

**Estimación:** 15-20 horas

---

#### 11. **Dar de Alta Más BBPP**
**Tareas:**
- Recopilar nuevas buenas prácticas
- Implementar validadores en `analyzer.py`
- Agregar reglas a `BBPP_Master.json`
- Actualizar documentación

**Ejemplos de nuevas BBPP:**
- Uso correcto de Delay vs WaitForReady
- Validación de input de usuario
- Gestión de recursos (conexiones, archivos)
- Documentación inline en workflows
- Uso de annotations

**Estimación:** Variable según cantidad de reglas

---

#### 12. **Revisión y Mejora de Reportes**
**Tareas:**
- Actualizar templates HTML con nuevos datos
- Agregar sección de "Penalizaciones Detalladas"
- Mejorar gráficos en reporte detallado
- Agregar exportación a PDF
- Mejorar formato de Excel con gráficos

**Archivos afectados:**
- `src/report_generator.py`
- `src/excel_generator.py`

**Estimación:** 6-8 horas

---

## INSTALACIÓN Y CONFIGURACIÓN

### Requisitos del Sistema
- Windows 10/11
- Python 3.13 o superior
- 500 MB de espacio en disco
- 4 GB de RAM recomendado

### Instalación Actual (Manual)

```bash
# 1. Clonar repositorio (cuando esté en Git)
git clone https://github.com/tu-usuario/AnalizadorBBPP_UiPath.git
cd AnalizadorBBPP_UiPath

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar aplicación
python main.py
```

### Dependencias Python (requirements.txt)
```
openpyxl==3.1.2
Pillow==10.0.0
```

### Configuración Inicial

1. **Branding:**
   - Ir a Configuración > Branding
   - Subir logo de empresa
   - Configurar nombre y colores

2. **Conjuntos de BBPP:**
   - Ir a Gestión de BBPP > Gestión de Conjuntos
   - Activar conjuntos deseados (UiPath, NTT Data)
   - Configurar dependencias

3. **Personalizar Reglas:**
   - Ir a Gestión de BBPP
   - Hacer doble clic en regla
   - Configurar penalización, excepciones, etc.

---

## NOTAS TÉCNICAS

### Sistema de Scoring

**Fórmula:**
```
base_score = 100
total_penalty = sum(penalty por cada regla)
total_activities = número de actividades en el proyecto

penalty_per_activity = total_penalty / total_activities
adjusted_penalty = penalty_per_activity × SCALING_FACTOR

if total_activities < 10:
    final_score = max(0, base_score - (total_penalty × 0.5))
else:
    final_score = max(0, base_score - adjusted_penalty)
```

**Calificaciones:**
- A (90-100%): Excelente
- B (80-89%): Muy Bien
- C (70-79%): Bien
- D (60-69%): Aceptable
- F (0-59%): Necesita Mejoras

---

## CONTACTO Y SOPORTE

**Desarrollador:** Carlos Vidal Castillejo
**Email:** [tu email]
**GitHub:** [tu repositorio]

---

**Última actualización:** 30 de Noviembre de 2025
