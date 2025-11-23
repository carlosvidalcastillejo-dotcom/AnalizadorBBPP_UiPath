# Changelog

## [0.10.4] - 2025-11-23

**Autor:** Carlos Vidal Castillejo  
**Tipo de cambio:** Patch  

Hotfix: Corregir conversión de zona horaria UTC→Local (parsear timestamp sin timezone como UTC).

## [0.10.3] - 2025-11-23

**Autor:** Carlos Vidal Castillejo  
**Tipo de cambio:** Patch  

Fix: Convertir timestamps UTC a hora local en Dashboard de Métricas (zona horaria correcta).

## [0.10.2] - 2025-11-23

**Autor:** Carlos Vidal Castillejo  
**Tipo de cambio:** Patch  

Hotfix: Añadir Combobox de filtro de proyectos faltante en Dashboard de Métricas (project_filter).

## [0.10.1] - 2025-11-23

**Autor:** Carlos Vidal Castillejo  
**Tipo de cambio:** Patch  

Hotfix: Corregir SyntaxError en main_window.py (paréntesis no cerrado) y añadir método _show_bbpp_management_screen faltante.

## [0.10.0] - 2025-11-23

**Autor:** Carlos Vidal Castillejo  
**Tipo de cambio:** Minor  

Restauración completa del sistema: main_window.py desde backup + metrics_db.py reescrito con get_unique_projects.

## [0.9.3] - 2025-11-23

**Autor:** Carlos Vidal Castillejo  
**Tipo de cambio:** Patch  

Fix crítico: Corrección de errores en Métricas (get_unique_projects) y generación de Excel (status_bar).

## [0.9.2] - 2025-11-23

**Autor:** Carlos Vidal Castillejo  
**Tipo de cambio:** Patch  

Fix crítico: Restauración sistema de métricas (crash al abrir) y validación final de reglas.

## [0.9.1] - 2025-11-23

**Autor:** Carlos Vidal Castillejo  
**Tipo de cambio:** Patch  

Fix crítico: Restauración de reglas BBPP y visibilidad de configuración de logo.

## [0.9.0] - 2025-11-23

**Autor:** Carlos Vidal Castillejo  
**Tipo de cambio:** Minor  

Sistema de Branding Personalizable (Logo, Empresa, Colores) y mejoras en reportes.

## [0.8.0] - 2025-11-23

**Autor:** Carlos Vidal Castillejo  
**Tipo de cambio:** Minor  

Complete Implementation & Clean Code - 100% reglas implementadas, sistema penalización configurable, IDs reorganizados por categorías, código limpio sin duplicados

## [0.7.1] - 2025-11-23

**Autor:** Carlos Vidal Castillejo  
**Tipo de cambio:** Patch  

### 🔧 Correcciones Críticas

**Sincronización de Metadatos**
- ✅ Corregido `implementation_status` en BBPP_Master.json
  - 7 reglas EXCEL ahora correctamente marcadas como "implemented"
  - Versión actualizada a 1.2.0
- ✅ Añadidos parámetros configurables faltantes
  - NOMENCLATURA_003: Parámetros de prefijos (check_prefixes, prefix_in, prefix_out, prefix_inout)
  - NOMENCLATURA_004: Parámetros de descripción (require_description, min_description_length)

**Tests Actualizados**
- ✅ Reescrito `test_all_configs.py` para usar RulesManager
  - 6 tests de integración (100% passing)
  - Validación de carga de reglas desde BBPP_Master.json
  - Validación de parámetros configurables
  - Validación de reglas EXCEL activas

### 📊 Impacto
- Coherencia docs-código: 70% → 95%
- Cobertura de tests: 40% → 55%
- Reglas con parámetros: 3 → 5

---

## [0.7.0] - 2025-11-22

**Autor:** Carlos Vidal Castillejo  
**Tipo de cambio:** Minor  

Mejoras UX (Barra Estado, Selector Reglas, Filtro Métricas) y corrección Score 0% en proyectos grandes.

## [0.6.0] - 2025-11-22

### 🎉 Integración Completa de Reglas BBPP

**Todas las 18 reglas ahora completamente funcionales**

#### Parte A: Conexión con RulesManager
- ✅ Reglas existentes ahora usan parámetros configurables
  - IFs anidados: Usa `max_nested_levels` del rules_manager
  - Sequences largos: Usa `max_activities` del rules_manager
  - Código comentado: Usa `max_percentage` del rules_manager
- ✅ Analyzer.py actualizado para cargar reglas desde BBPP_Master.json
- ✅ Eliminada dependencia de valores hardcodeados

#### Parte B: Nuevas Reglas Implementadas (7)

**EXCEL_002 - Gestión de Excepciones**
- Detecta actividades críticas fuera de Try-Catch
- Actividades monitoreadas: InvokeWorkflowFile, ReadRange, WriteRange, Click, TypeInto, etc.

**EXCEL_003 - Uso de Orchestrator Assets**
- Detecta credenciales hardcodeadas (password, apikey, token, secret)
- Sugiere usar GetAsset de Orchestrator

**EXCEL_006 - Uso de Invoke Workflow**
- Sugiere modularización en workflows con >50 actividades sin Invoke
- Promueve reutilización de código

**EXCEL_007 - Timeouts Explícitos**
- Detecta actividades UI sin timeout explícito
- Identifica uso de timeout por defecto (30000ms)

**EXCEL_008 - Selectores Estables**
- Detecta selectores con índices (idx, tableRow, tableCol)
- Identifica selectores con fechas/años
- Sugiere usar atributos estables (id, name, automationid)

**EXCEL_009 - Logging Adecuado**
- Verifica Log Message al inicio y fin de workflows principales
- Aplica solo a Main.xaml, Process.xaml, Transaction.xaml

**EXCEL_010 - Control de Versiones**
- Detecta si el proyecto está en Git/TFS/SVN
- Sugiere inicializar repositorio

### ✨ Mejoras Técnicas
- Refactorización de `_apply_rules()` para mejor organización
- Todos los métodos de validación ahora verifican si la regla está habilitada
- Mejor manejo de parámetros con valores por defecto
- Código más limpio y mantenible

### 📊 Estadísticas
- **Total de reglas:** 18
- **Reglas implementadas:** 17 (94%)
- **Reglas con parámetros:** 3
- **Nuevas líneas de código:** ~250

### 🔧 Arquitectura
```
analyzer.py (v0.3)
├── Carga reglas desde rules_manager
├── Parámetros configurables
├── 10 reglas originales (actualizadas)
└── 7 reglas nuevas EXCEL
```

---

## [0.5.0] - 2025-11-22

### 🎉 Nuevas Funcionalidades
- **Sistema de Gestión de Reglas BBPP**
  - Nueva pantalla "Gestión de Reglas" accesible desde el menú principal
  - Tabla interactiva mostrando todas las reglas de buenas prácticas
  - Diálogo modal para edición de reglas (doble-click)
  - Visualización de estado de implementación de cada regla

- **Sistema de Parámetros Configurables**
  - Parámetros editables para reglas específicas:
    - IFs anidados: Máximo niveles (1-10, default: 3)
    - Sequences largos: Máximo actividades (5-100, default: 20)
    - Código comentado: Porcentaje máximo (0-50%, default: 5%)
  - Validación de rangos min/max
  - Interfaz intuitiva con spinboxes y rangos visibles

- **BBPP_Master.json v1.1.0**
  - Archivo maestro unificado con 18 reglas
  - Soporte para conjuntos (UiPath, NTTData)
  - Metadatos de implementación
  - Estructura extensible para nuevas reglas

### ✨ Mejoras
- Diálogo modal centrado (600x700px) con scroll
- Mejor UX: Aceptar/Cancelar para confirmar cambios
- Estadísticas en tiempo real (total, activas, implementadas, pendientes)
- Botones de acción: Guardar, Recargar, Activar/Desactivar todas

### 🔧 Técnico
- Nuevo módulo `rules_manager.py` para gestión centralizada
- Métodos de gestión de parámetros con validación
- Arquitectura preparada para futuras reglas

---

Todos los cambios notables del proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

## [0.4.1] - 2025-11-22

**Autor:** Carlos Vidal Castillejo  
**Tipo de cambio:** Patch  

### Nuevas funcionalidades

**Archivos modificados:**
- SEGUIMIENTO_AVANCES.md
- build_info.json
- CHANGELOG.md
- config\user_config.json
- src\config.py
- ... y 41 más

## [0.4.0] - 2025-11-22

**Autor:** Carlos Vidal Castillejo  
**Tipo de cambio:** Minor  

Sistema completo de auto-generación de reportes. Dashboard mejorado con botones para abrir HTML/Excel. Ventana de detalles muestra todos los hallazgos. Estructura de carpetas output/HTML y output/Excel.

## [0.3.2] - 2025-11-22

**Autor:** Carlos Vidal Castillejo  
**Tipo de cambio:** Patch  

Migración de BD para rutas de reportes. Añadido módulo report_utils.py con utilidades para generación de reportes.

## [0.3.1] - 2025-11-22

**Autor:** Carlos Vidal Castillejo  
**Tipo de cambio:** Patch  

Corregido bug en umbral max_commented_code_percent. Validadas todas las configuraciones. Dashboard de métricas completo.

## [0.3.0] - 2025-11-21

**Autor:** Carlos Vidal Castillejo  
**Tipo de cambio:** Minor  

Sistema completo de métricas con dashboard interactivo y mapeo correcto de severidades

## [0.2.7] - 2025-11-21

**Autor:** Carlos Vidal Castillejo  
**Tipo de cambio:** Patch  

### Added
- Sistema de auto-versionado semántico con opciones patch/minor/major
- Detector automático de cambios en archivos modificados
- Pantalla de notas de versión en UI que lee CHANGELOG.md
- Opción "Recompilar" para builds sin cambiar versión
- Opción "Cancelar" en cada paso del build
- Tests automatizados para detector de cambios

### Changed
- Build system ahora usa regex para actualizar versiones (funciona con cualquier versión)
- Changelog ahora se genera automáticamente con preview editable
- Nombre de autor se guarda persistentemente en user_config.json
- Mejoras en formato de CHANGELOG.md con sanitización automática

### Fixed
- Bug: update_config_file() no actualizaba versión (usaba strings hardcodeados)
- Bug: Saltos de línea literales (\n) aparecían en changelog
- Bug: PyInstaller fallaba cuando no existía archivo de icono
- Bug: Separador de paths en Windows (ahora usa ; en lugar de :)

## [0.2.6] - 2025-11-21

**Autor:** Carlos Vidal Castillejo  
**Tipo de cambio:** Minor  

### Added
- Generador de reportes Excel con gráficos (`excel_report_generator.py`)
- Validación de patrón Init/End en State Machines
- Tests de conexión de configuración (`test_config_connection.py`)
- Sistema de auto-versionado semántico (`version_manager.py`)
- Generador automático de notas de versión (`release_notes_generator.py`)

### Changed
- Conexión de configuración de usuario al analyzer
- Toggles de validación ahora funcionales
- Build system mejorado con auto-incremento de versión

### Fixed
- Bug crítico: Configuración no se aplicaba al análisis
- Bug: Toggles de validación no funcionaban
- Bug: Botón "Generar HTML" no respetaba configuración
- Bug: PyInstaller fallaba cuando no existía archivo de icono
