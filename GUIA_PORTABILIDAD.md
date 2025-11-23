# 📦 GUÍA DE PORTABILIDAD - Analizador BBPP UiPath

**Versión Actual:** 0.3.0  
**Fecha:** 21/11/2025  
**Autor:** Carlos Vidal Castillejo

---

## 🎯 CÓMO MOVER EL PROYECTO A OTRO EQUIPO

### Opción 1: Copiar Carpeta Completa (Recomendado) ⭐

**Pasos:**

1. **Copiar la carpeta completa:**
   ```
   📁 analizador_bbpp_v0.2.6_COMPLETO/
   ```
   A tu disco externo o USB

2. **En el nuevo equipo:**
   - Pegar la carpeta donde quieras
   - Abrir terminal en esa carpeta
   - Instalar dependencias:
     ```bash
     pip install -r requirements.txt
     ```

3. **Listo!** Ya puedes:
   ```bash
   python run.py          # Ejecutar aplicación
   python build.py        # Compilar nueva versión
   ```

---

### Opción 2: Usar Git (Más Profesional)

**Si usas GitHub/GitLab:**

1. **En equipo actual:**
   ```bash
   git init
   git add .
   git commit -m "Versión 0.3.0 - Sistema de métricas completo"
   git remote add origin <tu-repo>
   git push -u origin main
   ```

2. **En nuevo equipo:**
   ```bash
   git clone <tu-repo>
   cd analizador_bbpp_v0.2.6_COMPLETO
   pip install -r requirements.txt
   ```

---

## 📋 ARCHIVOS IMPORTANTES A CONSERVAR

### ✅ Archivos Esenciales (SIEMPRE copiar)

```
📁 analizador_bbpp_v0.2.6_COMPLETO/
├── 📁 src/                    ← TODO el código fuente
├── 📁 config/                 ← Configuraciones
│   ├── user_config.json       ← TU configuración personalizada
│   └── bbpp_rules/            ← Reglas de análisis
├── 📁 data/                   ← Base de datos de métricas
│   └── metrics.db             ← Historial de análisis
├── 📁 assets/                 ← Recursos (iconos, logos)
├── 📁 tests/                  ← Tests unitarios
├── requirements.txt           ← Dependencias Python
├── run.py                     ← Ejecutar aplicación
├── build.py                   ← Compilar .exe
├── CHANGELOG.md               ← Historial de versiones
└── README.md                  ← Documentación
```

### ⚠️ Archivos Opcionales (puedes omitir)

```
📁 dist/                       ← Ejecutables compilados (se regeneran)
📁 build/                      ← Archivos temporales de build
📁 __pycache__/                ← Cache de Python
📁 .git/                       ← Historial Git (si usas Git)
📁 output/                     ← Reportes generados (se regeneran)
```

---

## 🔧 REQUISITOS EN EL NUEVO EQUIPO

### Software Necesario:

1. **Python 3.10 o superior**
   - Descargar: https://www.python.org/downloads/
   - ✅ Marcar "Add Python to PATH" durante instalación

2. **Dependencias Python:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Opcional (para compilar):**
   - PyInstaller (ya incluido en requirements.txt)

---

## 📝 VERIFICACIÓN POST-PORTABILIDAD

Después de copiar al nuevo equipo, verifica:

### 1. Verificar Python
```bash
python --version
# Debe mostrar: Python 3.10.x o superior
```

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Probar Aplicación
```bash
python run.py
```

### 4. Verificar Configuración
- Abre la app
- Ve a "⚙️ Configuración"
- Verifica que tus settings estén ahí

### 5. Verificar Métricas
- Click en "📈 Métricas"
- Debe mostrar tu historial (si copiaste `data/metrics.db`)

---

## 🗂️ ESTRUCTURA DE CARPETAS EXPLICADA

```
📁 analizador_bbpp_v0.2.6_COMPLETO/
│
├── 📁 src/                              # CÓDIGO FUENTE
│   ├── 📁 database/                     # Sistema de métricas (BD)
│   │   ├── __init__.py
│   │   └── metrics_db.py                # SQLite para historial
│   │
│   ├── 📁 metrics/                      # Análisis de métricas
│   │   ├── __init__.py
│   │   ├── metrics_calculator.py       # Cálculos avanzados
│   │   └── chart_generator.py          # Generador de gráficos
│   │
│   ├── 📁 ui/                           # Interfaz gráfica
│   │   ├── main_window.py              # Ventana principal
│   │   ├── metrics_dashboard.py        # Dashboard de métricas
│   │   └── release_notes_screen.py     # Notas de versión
│   │
│   ├── analyzer.py                      # Motor de análisis BBPP
│   ├── xaml_parser.py                   # Parser de XAML
│   ├── project_scanner.py               # Escáner de proyectos
│   ├── config.py                        # Configuración global
│   ├── version_manager.py               # Versionado semántico
│   ├── release_notes_generator.py      # Generador de changelog
│   ├── change_detector.py               # Detector de cambios
│   ├── report_generator.py              # Reportes HTML
│   └── excel_report_generator.py        # Reportes Excel
│
├── 📁 config/                           # CONFIGURACIONES
│   ├── user_config.json                 # TU configuración
│   └── 📁 bbpp_rules/                   # Reglas de análisis
│       ├── nomenclatura.json
│       ├── hardcodeo.json
│       ├── anidamiento.json
│       ├── try_catch.json
│       ├── modularizacion.json
│       └── logs.json
│
├── 📁 data/                             # DATOS PERSISTENTES
│   └── metrics.db                       # Base de datos SQLite
│
├── 📁 assets/                           # RECURSOS
│   └── icon.ico                         # Icono de la app
│
├── 📁 tests/                            # TESTS UNITARIOS
│   ├── test_metrics_db.py
│   └── test_change_detector.py
│
├── 📁 output/                           # SALIDAS (se regenera)
│   ├── 📁 reports/                      # Reportes HTML/Excel
│   └── 📁 charts/                       # Gráficos generados
│
├── 📁 dist/                             # EJECUTABLES (se regenera)
│   └── Analizador_BBPP_UiPath_v0.3.0.exe
│
├── 📁 build/                            # TEMPORAL (se regenera)
│
├── run.py                               # EJECUTAR APP
├── build.py                             # COMPILAR EXE
├── requirements.txt                     # DEPENDENCIAS
├── CHANGELOG.md                         # HISTORIAL
└── README.md                            # DOCUMENTACIÓN
```

---

## 💾 BACKUP RECOMENDADO

### Carpetas Críticas a Respaldar:

1. **`src/`** - Todo el código
2. **`config/`** - Tu configuración personalizada
3. **`data/`** - Historial de análisis
4. **`CHANGELOG.md`** - Historial de versiones
5. **`requirements.txt`** - Dependencias

### Carpetas que NO necesitas respaldar:

- `dist/` - Se regenera al compilar
- `build/` - Temporal
- `__pycache__/` - Cache
- `output/` - Reportes (se regeneran)

---

## 🚀 INICIO RÁPIDO EN NUEVO EQUIPO

```bash
# 1. Copiar carpeta al nuevo equipo

# 2. Abrir terminal en la carpeta
cd ruta/a/analizador_bbpp_v0.2.6_COMPLETO

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
python run.py

# 5. (Opcional) Compilar
python build.py
```

---

## 📞 SOLUCIÓN DE PROBLEMAS

### Error: "No module named 'tkinter'"
**Solución:** Reinstalar Python con soporte Tkinter

### Error: "No module named 'openpyxl'"
**Solución:** 
```bash
pip install -r requirements.txt
```

### Error: "Permission denied" al compilar
**Solución:** Ejecutar terminal como Administrador

### No aparece historial de métricas
**Solución:** Asegúrate de copiar la carpeta `data/` con `metrics.db`

---

## ✅ CHECKLIST DE PORTABILIDAD

- [ ] Copiar carpeta completa `analizador_bbpp_v0.2.6_COMPLETO/`
- [ ] Verificar que `config/user_config.json` está incluido
- [ ] Verificar que `data/metrics.db` está incluido (si quieres historial)
- [ ] En nuevo equipo: Instalar Python 3.10+
- [ ] Ejecutar `pip install -r requirements.txt`
- [ ] Probar con `python run.py`
- [ ] Verificar configuración en la app
- [ ] Verificar métricas (si copiaste la BD)

---

**¡Listo para mover a cualquier equipo!** 🎉
