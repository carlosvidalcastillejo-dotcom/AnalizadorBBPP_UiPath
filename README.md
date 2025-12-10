# 🚀 Analizador de Buenas Prácticas para UiPath

**Versión:** 1.0.0
**Autor:** Carlos Vidal Castillejo

---

## 📋 Descripción

Aplicación de escritorio profesional desarrollada en Python con Tkinter que permite analizar proyectos UiPath y verificar el cumplimiento de Buenas Prácticas (BBPP) tanto oficiales de UiPath como personalizadas de la empresa.

### ✨ Características Principales

- ✅ **17 Reglas BBPP implementadas** (Nomenclatura, Estructura, Modularización, Código Limpio, Rendimiento)
- ✅ **Sistema de penalización personalizable** con 3 modos (severity_default, individual, global)
- ✅ **Sistema de excepciones** para REFramework (50 variables/argumentos predefinidos)
- ✅ **Gestión de conjuntos de BBPP** (UiPath, Custom)
- ✅ **Reportes profesionales** (HTML Normal, HTML Detallado con gráficos Chart.js, Excel)
- ✅ **Dashboard de métricas** con histórico de análisis y filtros
- ✅ **Sistema de branding personalizable** (logo, empresa, colores)
- ✅ **Base de datos SQLite** para métricas históricas
- ✅ **Validación de dependencias** de paquetes NuGet configurables por conjunto
- ✅ **Ejecutable .exe** compilado con PyInstaller

---

## 🗂️ Estructura del Proyecto

```
AnalizadorBBPP_UiPath/
├── src/
│   ├── main.py                          # Punto de entrada
│   ├── config.py                        # Configuración global
│   ├── xaml_parser.py                   # Parser de XAML
│   ├── analyzer.py                      # Analizador de BBPP (17 reglas)
│   ├── project_scanner.py               # Escáner de proyectos
│   ├── rules_manager.py                 # Gestor de reglas BBPP
│   ├── report_generator.py              # Generador de reportes HTML
│   ├── excel_report_generator.py        # Generador de reportes Excel
│   ├── branding_manager.py              # Gestor de branding
│   ├── version_manager.py               # Gestor de versiones
│   ├── ui/
│   │   ├── main_window.py               # Ventana principal
│   │   ├── rules_management_screen.py   # Pantalla de gestión de reglas
│   │   ├── metrics_dashboard.py         # Dashboard de métricas
│   │   └── release_notes_screen.py      # Pantalla de notas de versión
│   ├── database/
│   │   └── metrics_db.py                # Base de datos de métricas
│   └── metrics/
│       ├── metrics_calculator.py        # Calculador de métricas
│       └── chart_generator.py           # Generador de gráficos
├── config/
│   ├── bbpp/
│   │   └── BBPP_Master.json            # Reglas BBPP maestras
│   ├── config.json                      # Configuración de scoring
│   ├── branding.json                    # Configuración de branding
│   └── user_config.json                 # Configuración de usuario
├── assets/                              # Logos, imágenes
├── output/                              # Reportes generados
│   ├── HTML/                            # Reportes HTML
│   └── Excel/                           # Reportes Excel
├── dist/
│   └── AnalizadorBBPP_UiPath.exe       # Ejecutable compilado
├── AnalizadorBBPP_UiPath.spec          # Configuración PyInstaller
├── CHANGELOG.md                         # Registro de cambios
├── ROADMAP.md                           # Hoja de ruta
└── README.md                            # Este archivo
```

---

## 🚀 Instalación y Uso

### Opción 1: Ejecutar el .exe (Recomendado)

1. Descargar el proyecto desde el repositorio
2. Navegar a la carpeta `dist/`
3. Ejecutar `AnalizadorBBPP_UiPath.exe`

### Opción 2: Ejecutar con Python

**Requisitos:**
- Python 3.8 o superior
- Tkinter (incluido en Python por defecto)

**Instalación de dependencias:**
```bash
pip install -r requirements.txt
```

**Ejecutar:**
```bash
python src/main.py
```

---

## 📊 Reglas BBPP Implementadas

### 📝 Nomenclatura (6 reglas)

| ID | Nombre | Descripción |
|---|---|---|
| **NOMENCLATURA_001** | Variables en camelCase | Variables deben usar camelCase (ej: `miVariable`) |
| **NOMENCLATURA_002** | Evitar nombres genéricos | Detecta nombres como `var1`, `temp`, `test` |
| **NOMENCLATURA_003** | Argumentos con prefijos | Argumentos deben tener `in_`, `out_`, `io_` |
| **NOMENCLATURA_004** | Comentarios en workflows | Workflows deben tener comentarios descriptivos |
| **NOMENCLATURA_005** | Variables en PascalCase | Variables de tipo especial en PascalCase |
| **NOMENCLATURA_006** | Argumentos con descripción | Argumentos deben tener descripción clara |

### 🏗️ Estructura (3 reglas)

| ID | Nombre | Descripción |
|---|---|---|
| **ESTRUCTURA_001** | IFs anidados excesivos | Máximo 3 niveles de IFs (configurable) |
| **ESTRUCTURA_002** | Try-Catch vacíos | Detecta bloques Catch sin manejo de errores |
| **ESTRUCTURA_003** | Actividades críticas protegidas | Actividades críticas deben estar en Try-Catch |

### 🔧 Modularización (3 reglas)

| ID | Nombre | Descripción |
|---|---|---|
| **MODULARIZACION_001** | Sequences largos | Sequences con >20 actividades (configurable) |
| **MODULARIZACION_002** | Uso de Invoke Workflow | Promover reutilización con Invoke Workflow |
| **MODULARIZACION_003** | Patrón Init/End | State Machines deben tener patrón Init/End |

### 🧹 Código Limpio (2 reglas)

| ID | Nombre | Descripción |
|---|---|---|
| **CODIGO_001** | Código comentado excesivo | Máximo 5% de código comentado (configurable) |
| **LOGGING_001** | Logging insuficiente | Workflows deben tener logs adecuados |

### ⚡ Rendimiento y Configuración (3 reglas)

| ID | Nombre | Descripción |
|---|---|---|
| **RENDIMIENTO_001** | Timeouts explícitos | Actividades UI deben tener timeout explícito |
| **SELECTORES_001** | Selectores dinámicos | Evitar selectores con índices o fechas |
| **CONFIGURACION_001** | Orchestrator Assets | Evitar credenciales hardcodeadas |

---

## ⚙️ Sistema de Penalización Personalizable

Cada regla puede configurarse con uno de estos **3 modos**:

### 1. **Severity Default** (Predeterminado)
Usa pesos globales según severidad:
- ERROR: 10 puntos por hallazgo
- WARNING: 3 puntos por hallazgo
- INFO: 0.5 puntos por hallazgo

### 2. **Individual**
Cada hallazgo penaliza por el porcentaje configurado.
- Ejemplo: Si `penalty_value = 2%` y hay 20 hallazgos → Penalización = 40%

### 3. **Global**
Penalización fija total, sin importar la cantidad de hallazgos.
- Ejemplo: Si `penalty_value = 5%` y hay 1 o 100 hallazgos → Penalización = 5%

### Límite Máximo
Opcionalmente se puede activar un **límite máximo** (cap) para limitar la penalización máxima de una regla.
- Solo aplica a modos **Severity Default** e **Individual**

---

## 🔧 Sistema de Excepciones

Las reglas de nomenclatura soportan **excepciones** para variables/argumentos estándar del REFramework:

### Excepciones Predefinidas (50 total):
```
Config, TransactionItem, SystemException, BusinessException,
in_Config, out_Config, io_Config, in_TransactionItem,
out_TransactionItem, io_TransactionItem, TransactionNumber,
TransactionField1, TransactionField2, TransactionID,
RetryNumber, QueueRetry, TransactionData, dt_TransactionData,
dt_Config, str_TransactionID, Exception, BusinessRuleException,
...
```

### Gestión desde UI:
- ➕ Agregar nuevas excepciones
- ➖ Eliminar excepciones
- ✅ Persistencia en BBPP_Master.json

---

## 📦 Gestión de Conjuntos de BBPP

Permite organizar reglas en **conjuntos** como:
- **UiPath**: Reglas oficiales de UiPath
- **Custom**: Conjuntos personalizados

### Funcionalidades:
- ✅ Activar/desactivar conjuntos completos
- ✅ Asignar reglas a conjuntos
- ✅ Gestionar dependencias de paquetes NuGet por conjunto
- ✅ Validar que el proyecto tenga las dependencias necesarias

---

## 📈 Reportes Generados

### 1. **Reporte HTML Normal**
- Resumen ejecutivo con score visual
- Estadísticas del proyecto
- Listado de hallazgos agrupados por categoría

### 2. **Reporte HTML Detallado**
- Todo lo del reporte normal +
- **Gráficos interactivos** con Chart.js:
  - Distribución por severidad (Pie)
  - Hallazgos por categoría (Bar)
  - Top 5 reglas con más hallazgos (Bar)
- **Hallazgos colapsables** para mejor navegación
- **Filtros interactivos** por severidad y categoría

### 3. **Reporte Excel**
- Hoja "Resumen" con estadísticas
- Hoja "Hallazgos" con tabla detallada
- Formato profesional con colores por severidad

---

## 📊 Dashboard de Métricas

Visualiza el **histórico de análisis** con:
- ✅ Tabla con todos los análisis realizados
- ✅ Filtro por proyecto
- ✅ Ordenamiento por fecha
- ✅ Botones para abrir reportes HTML/Excel directamente
- ✅ Ventana de detalles con todos los hallazgos

---

## 🎨 Sistema de Branding

Personaliza la aplicación con:
- 🖼️ **Logo personalizado** (PNG, JPG)
- 🏢 **Nombre de empresa**
- 🎨 **Colores corporativos** (Primary, Secondary, Accent)
- ✅ Cambios se reflejan en reportes HTML

---

## 🔧 Configuración

### Archivo: `config/config.json`
```json
{
  "scoring": {
    "error_weight": -10,
    "warning_weight": -3,
    "info_weight": -0.5,
    "scaling_factor": 5
  }
}
```

### Archivo: `config/bbpp/BBPP_Master.json`
Contiene todas las reglas con sus parámetros configurables.

---

## 🛠️ Compilación a .exe

El proyecto incluye configuración de PyInstaller:

```bash
pyinstaller AnalizadorBBPP_UiPath.spec
```

El ejecutable se generará en `dist/AnalizadorBBPP_UiPath.exe`.

---

## 📜 Changelog

Ver [CHANGELOG.md](CHANGELOG.md) para historial completo de cambios.

---

## 🗺️ Roadmap

Ver [ROADMAP.md](ROADMAP.md) para próximas funcionalidades planificadas.

---

## 📝 Licencia

Proyecto de código abierto.

---

## 👥 Autor

**Desarrollador:** Carlos Vidal Castillejo

---

<<<<<<< HEAD
## 📞 Contacto

Para consultas o contribuciones, abrir un issue en el repositorio de GitHub.

---

=======
>>>>>>> bfff680d14e127510897c16c93ca905fb95f3a04
**Última actualización:** 30 de Noviembre de 2024
**Versión:** 1.0.0
