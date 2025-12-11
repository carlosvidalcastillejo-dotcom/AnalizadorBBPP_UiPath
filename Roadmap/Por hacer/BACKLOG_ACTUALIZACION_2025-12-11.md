# 📋 BACKLOG - Nuevas Funcionalidades Solicitadas
## Fecha: 2025-12-11
## Versión Actual: 1.2.0
## Autor: Carlos Vidal Castillejo

---

## 🆕 NUEVAS SOLICITUDES (11 Diciembre 2025)

### **PRIORIDAD ALTA**

---

### 1. ✅ **Validación de Compatibilidad de Versiones UiPath**

**Descripción:** Verificar que el proyecto funciona correctamente en diferentes versiones de UiPath Studio.

#### 1.1 Detección de Versión de Studio
- [ ] **Leer versión completa de Studio desde project.json**
  - Campo: `studioVersion` (ej: "23.10.5", "24.10.1", "25.10.0")
  - Extraer versión major, minor, patch
  - Almacenar en metadatos del proyecto

#### 1.2 Validación de Compatibilidad
- [ ] **Comparar con versiones soportadas**
  - Definir matriz de compatibilidad (config/version_compatibility.json)
  - Versiones soportadas: 2023.10.x, 2024.10.x, 2025.10.x
  - Warning si versión es muy antigua (< 2023.10)
  - Error si versión no soportada

- [ ] **Detectar actividades deprecadas por versión**
  - Lista de actividades deprecadas por versión
  - Sugerir alternativas modernas
  - Ejemplo: "Click" → "UI Automation: Click" en versiones modernas

- [ ] **Validar paquetes y dependencias**
  - Comprobar versiones de paquetes instalados
  - Avisar si paquetes son incompatibles con la versión de Studio
  - Sugerir actualización de paquetes

#### 1.3 Reporte de Compatibilidad
- [ ] **Sección nueva en reportes**
  - "Compatibilidad de Versión"
  - Versión detectada
  - Estado de compatibilidad (Compatible / Warning / Incompatible)
  - Lista de problemas específicos de versión
  - Recomendaciones de actualización

**Archivos a modificar:**
- `src/project_scanner.py` - Extraer studioVersion completa
- `src/analyzer.py` - Añadir validaciones de versión
- `config/version_compatibility.json` (NUEVO) - Matriz de compatibilidad
- `src/version_compatibility_checker.py` (NUEVO) - Lógica de validación

**Criterios de aceptación:**
- ✅ Detecta versión exacta de Studio (23.10.5, 24.10.1, etc.)
- ✅ Valida compatibilidad contra matriz configurable
- ✅ Genera warnings para versiones antiguas
- ✅ Sugiere actividades alternativas para deprecadas
- ✅ Incluye sección en reportes HTML/Excel

---

### 2. 🏗️ **Detección de Tipo de Proyecto (Legacy vs Windows)**

**Descripción:** Identificar si el proyecto usa Legacy (VB) o Windows (C#) y adaptar validaciones según el tipo.

#### 2.1 Detección de Tipo de Proyecto
- [ ] **Leer configuración del proyecto**
  - Campo: `designOptions.projectProfile` en project.json
  - Valores: "Legacy", "Windows", "Web", "Cross-Platform"
  - Campo alternativo: `expressionLanguage` ("VisualBasic", "CSharp")
  - Almacenar en metadatos

- [ ] **Detectar lenguaje de expresiones**
  - VisualBasic (VB.NET) en proyectos Legacy
  - CSharp (C#) en proyectos Windows
  - Extraer de `designOptions.expressionLanguage`

- [ ] **Identificar sintaxis en XAML**
  - Expresiones VB: `variable1 + variable2`
  - Expresiones C#: `variable1 + variable2` (similar pero diferentes métodos)
  - Buscar patrones específicos de cada lenguaje

#### 2.2 Validaciones Específicas por Tipo
- [ ] **Reglas específicas de Legacy (VB.NET)**
  - Validar sintaxis VB en expresiones
  - Comprobar uso correcto de métodos VB (Left, Right, Mid, etc.)
  - Detectar conversiones de tipo VB (CStr, CInt, etc.)

- [ ] **Reglas específicas de Windows (C#)**
  - Validar sintaxis C# en expresiones
  - Comprobar uso de métodos .NET modernos
  - Detectar LINQ queries
  - Validar async/await patterns

- [ ] **Advertencias de incompatibilidad**
  - Warning si usa sintaxis de otro lenguaje
  - Sugerencias de conversión VB ↔ C#
  - Detectar mixed expressions (error)

#### 2.3 Reporte de Tipo de Proyecto
- [ ] **Metadatos en reportes**
  - Tipo de proyecto (Legacy/Windows/Web/Cross-Platform)
  - Lenguaje de expresiones (VB.NET/C#)
  - Versión de .NET Framework
  - Lista de características específicas detectadas

**Archivos a modificar:**
- `src/project_scanner.py` - Extraer projectProfile y expressionLanguage
- `src/analyzer.py` - Añadir validaciones específicas por tipo
- `config/bbpp/BBPP_UiPath.json` - Nuevas reglas por tipo de proyecto
- `src/expression_parser.py` (NUEVO) - Parser de expresiones VB/C#

**Criterios de aceptación:**
- ✅ Detecta tipo de proyecto (Legacy/Windows/Web/Cross-Platform)
- ✅ Identifica lenguaje de expresiones (VB.NET/C#)
- ✅ Aplica reglas específicas según tipo
- ✅ Detecta sintaxis incorrecta para el tipo de proyecto
- ✅ Genera warnings de incompatibilidad
- ✅ Incluye información en reportes

---

### 3. 💻 **Detección de Lenguaje de Programación (VB.NET vs C#)**

**Descripción:** Identificar si el proyecto usa VB.NET o C# y validar sintaxis correcta.

#### 3.1 Análisis de Expresiones
- [ ] **Parser de expresiones**
  - Extraer todas las expresiones de XAML
  - Identificar lenguaje por sintaxis
  - Detectar errores de sintaxis

- [ ] **Validación de sintaxis VB.NET**
  - Operadores: `And`, `Or`, `Not`, `&` (concatenación)
  - Funciones: `CStr()`, `CInt()`, `Left()`, `Right()`, `Mid()`
  - Conversiones: `CBool()`, `CDate()`, etc.
  - Keywords: `Nothing`, `Is`, `IsNot`

- [ ] **Validación de sintaxis C#**
  - Operadores: `&&`, `||`, `!`, `+` (concatenación)
  - Funciones: `.ToString()`, `.Substring()`, `int.Parse()`
  - Conversiones: `(int)`, `(string)`, `Convert.To*()`
  - Keywords: `null`, `is`, `as`

#### 3.2 Detección de Errores Comunes
- [ ] **Errores de mezcla de sintaxis**
  - Usar `And` en proyecto C# → Error
  - Usar `&&` en proyecto VB.NET → Error
  - Usar `Nothing` en C# → Error (debe ser `null`)

- [ ] **Sugerencias de corrección**
  - Convertir automáticamente expresión al lenguaje correcto
  - Mostrar equivalencia VB ↔ C#
  - Ejemplo: `variable1 & variable2` (VB) → `variable1 + variable2` (C#)

#### 3.3 Regla BBPP Nueva: "EXPRESIONES_001"
- [ ] **Crear nueva regla**
  - ID: EXPRESIONES_001
  - Nombre: "Sintaxis de expresión correcta para el lenguaje"
  - Severidad: Error
  - Descripción: "Las expresiones deben usar la sintaxis correcta según el lenguaje del proyecto (VB.NET o C#)"
  - Validación: Detectar sintaxis incorrecta
  - Sugerencia: Mostrar expresión corregida

**Archivos a crear/modificar:**
- `src/expression_parser.py` (NUEVO) - Parser de expresiones VB/C#
- `src/expression_validator.py` (NUEVO) - Validador de sintaxis
- `src/analyzer.py` - Integrar validación de expresiones
- `config/bbpp/BBPP_UiPath.json` - Añadir EXPRESIONES_001
- `config/syntax_mappings.json` (NUEVO) - Mapeos VB ↔ C#

**Criterios de aceptación:**
- ✅ Detecta lenguaje del proyecto correctamente
- ✅ Extrae todas las expresiones de XAML
- ✅ Valida sintaxis VB.NET correctamente
- ✅ Valida sintaxis C# correctamente
- ✅ Detecta errores de mezcla de sintaxis
- ✅ Sugiere correcciones automáticas
- ✅ Genera findings con regla EXPRESIONES_001

---

### 4. 🔄 **Detección de Variables Duplicadas en Mismo Scope**

**Descripción:** Verificar que no existan variables con el mismo nombre dentro del mismo alcance (scope).

#### 4.1 Análisis de Scopes
- [ ] **Mapeo de scopes en XAML**
  - Identificar todos los scopes (Sequence, Flowchart, StateMachine, etc.)
  - Crear árbol jerárquico de scopes
  - Cada scope tiene: parent_scope, child_scopes, variables

- [ ] **Detección de variables por scope**
  - Extraer variables declaradas en cada scope
  - Almacenar: nombre, tipo, scope_id, posición en XAML
  - Crear diccionario: {scope_id: [lista_variables]}

- [ ] **Algoritmo de detección de duplicados**
  - Para cada scope, verificar si hay nombres duplicados
  - Comparar solo variables en el MISMO scope (no parent ni child)
  - Ignorar scopes diferentes (variables pueden tener mismo nombre si están en scopes distintos)

#### 4.2 Validación de Visibilidad
- [ ] **Reglas de visibilidad**
  - Variables en scope hijo NO pueden duplicar variables de scope padre (shadowing)
  - Variables en scope padre NO afectan a scope hijo (OK)
  - Variables en scopes hermanos pueden tener mismo nombre (OK)

- [ ] **Casos especiales**
  - Variables de Invoke Workflow (in_/out_/io_) → scope separado
  - Variables en Try-Catch → considerar scope del Try
  - Variables en If-Then-Else → considerar scope del If

#### 4.3 Regla BBPP Nueva: "VARIABLES_005"
- [ ] **Crear nueva regla**
  - ID: VARIABLES_005
  - Nombre: "Variables duplicadas en el mismo scope"
  - Severidad: Error
  - Categoría: "Nomenclatura"
  - Descripción: "No debe haber variables con el mismo nombre dentro del mismo alcance (scope)"
  - Validación:
    - Detectar duplicados en mismo scope
    - Detectar shadowing (duplicado en scope hijo)
  - Sugerencia: "Renombrar una de las variables para evitar conflictos"

#### 4.4 Reporte de Duplicados
- [ ] **Detalles del finding**
  - Nombre de la variable duplicada
  - Lista de ubicaciones donde aparece
  - Scope donde ocurre el duplicado
  - Archivo XAML y línea aproximada
  - Sugerencia: "variable1" → "variable1_2", "variable1_backup", etc.

**Archivos a crear/modificar:**
- `src/scope_analyzer.py` (NUEVO) - Análisis de scopes en XAML
- `src/variable_tracker.py` (NUEVO) - Tracking de variables por scope
- `src/analyzer.py` - Integrar validación de duplicados
- `config/bbpp/BBPP_UiPath.json` - Añadir VARIABLES_005
- `src/xaml_parser.py` - Mejorar extracción de variables con scope

**Ejemplos:**

**CASO 1: Duplicado en mismo scope (ERROR)**
```xml
<Sequence>
  <Variable Name="myVar" />
  <Variable Name="myVar" />  <!-- ❌ ERROR: Duplicado -->
</Sequence>
```

**CASO 2: Variable en scope padre e hijo (WARNING - Shadowing)**
```xml
<Sequence>
  <Variable Name="myVar" />
  <Sequence>
    <Variable Name="myVar" />  <!-- ⚠️ WARNING: Shadowing -->
  </Sequence>
</Sequence>
```

**CASO 3: Variables en scopes hermanos (OK)**
```xml
<Sequence>
  <Sequence>
    <Variable Name="myVar" />  <!-- ✅ OK -->
  </Sequence>
  <Sequence>
    <Variable Name="myVar" />  <!-- ✅ OK (scope diferente) -->
  </Sequence>
</Sequence>
```

**Criterios de aceptación:**
- ✅ Mapea correctamente todos los scopes del proyecto
- ✅ Detecta variables duplicadas en el mismo scope
- ✅ Detecta shadowing (duplicado en scope hijo)
- ✅ Ignora duplicados en scopes hermanos/independientes
- ✅ Genera finding con ubicaciones exactas
- ✅ Sugiere nombres alternativos
- ✅ Incluye en reportes HTML/Excel

---

## 📊 ESTADO ACTUAL DEL CÓDIGO

### ✅ Lo que YA tenemos implementado:

1. **Detección básica de versión de Studio**
   - Archivo: `src/project_scanner.py` línea 203-235
   - Lee `studioVersion` de project.json
   - Extrae versión de Studio y UiPath.System.Activities
   - Detecta `projectProfile` (Legacy/Windows)

2. **Nomenclatura de variables**
   - Archivos: `src/analyzer.py`
   - Reglas: NOMENCLATURA_001, NOMENCLATURA_002, NOMENCLATURA_003
   - Valida camelCase, PascalCase, prefijos

3. **Sistema de reglas configurable**
   - Archivo: `config/bbpp/BBPP_UiPath.json`
   - 17 reglas implementadas
   - Sistema de severidad y categorías

### ⚠️ Lo que FALTA implementar:

1. **Validación profunda de versiones**
   - Matriz de compatibilidad
   - Detección de actividades deprecadas
   - Recomendaciones de actualización

2. **Parser de expresiones VB/C#**
   - Análisis de sintaxis
   - Validación de lenguaje
   - Conversiones automáticas

3. **Análisis de scopes para variables**
   - Mapeo de jerarquía de scopes
   - Detección de duplicados
   - Detección de shadowing

4. **Nuevas reglas BBPP**
   - EXPRESIONES_001: Sintaxis de expresión correcta
   - VARIABLES_005: Variables duplicadas en mismo scope

---

## 🗂️ ESTRUCTURA DE ARCHIVOS PROPUESTA

```
src/
├── analyzers/              (NUEVO - Carpeta para analizadores específicos)
│   ├── version_checker.py  (Validación de versiones UiPath)
│   ├── expression_parser.py (Parser de expresiones VB/C#)
│   ├── scope_analyzer.py   (Análisis de scopes XAML)
│   └── variable_tracker.py (Tracking de variables)
│
├── validators/             (NUEVO - Validadores específicos)
│   ├── expression_validator.py (Valida sintaxis VB/C#)
│   └── scope_validator.py      (Valida scopes y duplicados)
│
└── analyzer.py             (MODIFICAR - Integrar nuevos analizadores)

config/
├── version_compatibility.json  (NUEVO - Matriz de compatibilidad)
├── syntax_mappings.json        (NUEVO - Mapeos VB ↔ C#)
└── bbpp/
    └── BBPP_UiPath.json        (MODIFICAR - Añadir nuevas reglas)
```

---

## 📅 PLANIFICACIÓN SUGERIDA

### Sprint 1 (1-2 semanas)
**Objetivo:** Validación de versiones y tipos de proyecto

- [ ] Implementar `version_checker.py`
- [ ] Crear `version_compatibility.json`
- [ ] Mejorar extracción en `project_scanner.py`
- [ ] Añadir sección en reportes
- [ ] Testing con proyectos 2023.10, 2024.10, 2025.10

### Sprint 2 (1-2 semanas)
**Objetivo:** Parser de expresiones y validación VB/C#

- [ ] Implementar `expression_parser.py`
- [ ] Implementar `expression_validator.py`
- [ ] Crear `syntax_mappings.json`
- [ ] Añadir regla EXPRESIONES_001
- [ ] Testing con proyectos Legacy y Windows

### Sprint 3 (2 semanas)
**Objetivo:** Detección de variables duplicadas

- [ ] Implementar `scope_analyzer.py`
- [ ] Implementar `variable_tracker.py`
- [ ] Añadir regla VARIABLES_005
- [ ] Testing exhaustivo de scopes
- [ ] Validar casos edge (shadowing, scopes complejos)

### Sprint 4 (1 semana)
**Objetivo:** Integración y testing final

- [ ] Integrar todos los analizadores en `analyzer.py`
- [ ] Actualizar reportes HTML/Excel
- [ ] Testing end-to-end
- [ ] Documentación de nuevas features
- [ ] Release v1.3.0

---

## 🎯 PRIORIDAD DE IMPLEMENTACIÓN

1. **ALTA** - Detección de tipo de proyecto (Legacy/Windows) - **Bloqueante para otras features**
2. **ALTA** - Validación de versiones UiPath - **Requerido por usuario**
3. **ALTA** - Detección de variables duplicadas - **Requerido por usuario**
4. **MEDIA** - Parser y validación de expresiones VB/C# - **Mejora de calidad**

---

## 📝 NOTAS TÉCNICAS

### Consideraciones de Implementación

**1. Performance:**
- Parser de expresiones puede ser costoso → Cachear resultados
- Análisis de scopes debe ser eficiente → Usar algoritmo recursivo optimizado
- Validación de versiones es rápida → No afecta performance

**2. Compatibilidad:**
- Probar con proyectos reales de diferentes versiones
- Validar con proyectos Legacy y Windows
- Testing con diferentes estructuras de scopes

**3. Mantenibilidad:**
- Crear módulos independientes para cada feature
- Documentar formato de project.json por versión
- Mantener actualizada matriz de compatibilidad

---

## ✅ CRITERIOS DE ACEPTACIÓN GLOBALES

Para considerar estas features completadas:

1. ✅ Detecta correctamente versiones 2023.10.x, 2024.10.x, 2025.10.x
2. ✅ Identifica proyectos Legacy (VB) vs Windows (C#)
3. ✅ Valida sintaxis de expresiones VB.NET y C#
4. ✅ Detecta variables duplicadas en mismo scope
5. ✅ Detecta shadowing de variables (scope hijo duplica padre)
6. ✅ Genera findings claros con sugerencias
7. ✅ Incluye información en reportes HTML y Excel
8. ✅ Performance < 5 segundos adicionales para proyectos de 50 XAML
9. ✅ Tests unitarios cubren casos principales
10. ✅ Documentación actualizada

---

**Última actualización:** 2025-12-11
**Versión del documento:** 1.0
**Estado:** 📋 Backlog pendiente de implementación
**Próxima revisión:** Después de Sprint 1
