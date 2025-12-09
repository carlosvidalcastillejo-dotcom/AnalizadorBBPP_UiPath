# 🚫 Implementación: Sistema de Excepciones para Reglas BBPP

## 📋 Índice
1. [Análisis del Problema](#análisis-del-problema)
2. [Diseño de la Solución](#diseño-de-la-solución)
3. [Estructura de Datos](#estructura-de-datos)
4. [Implementación Backend](#implementación-backend)
5. [Implementación Frontend (UI)](#implementación-frontend-ui)
6. [Código Completo](#código-completo)
7. [Pruebas y Validación](#pruebas-y-validación)
8. [Excepciones Predefinidas REFramework](#excepciones-predefinidas-reframework)

---

## 🎯 Análisis del Problema

### Problema Identificado

El **REFramework oficial de UiPath** utiliza variables y argumentos con nombres que técnicamente violan las BBPP, pero son parte del estándar del framework:

**Ejemplos de Falsos Positivos**:
- `in_Config` → Falla NOMENCLATURA_002 (nombre genérico "Config")
- `io_TransactionItem` → Falla NOMENCLATURA_002 (nombre genérico "Item")
- `in_TransactionData` → Falla NOMENCLATURA_002 (nombre genérico "Data")
- `Config` (variable) → Falla NOMENCLATURA_001/005 (nombre genérico)
- `TransactionItem` → Falla NOMENCLATURA_002 (nombre genérico)
- `SystemException` → Falla NOMENCLATURA_002 (nombre genérico)

### Por Qué Ocurre

Las reglas de nomenclatura están diseñadas para **proyectos personalizados**, pero el REFramework es un **template oficial** creado por UiPath con nombres estándar que se reutilizan en todos los proyectos.

**Problema**: No se puede cambiar el REFramework (es oficial), pero tampoco se puede desactivar la regla (necesaria para proyectos custom).

### Solución Propuesta

**Sistema de Excepciones por Regla**: Permitir definir una lista de nombres que deben **ignorarse** durante la validación de cada regla específica.

---

## 🎨 Diseño de la Solución

### Características del Sistema

1. ✅ **Configurable por regla**: Cada regla tiene su propia lista de excepciones
2. ✅ **Persistente**: Se guarda en `BBPP_Master.json`
3. ✅ **Editable desde UI**: Agregar/eliminar excepciones sin tocar código
4. ✅ **Sin hardcodeo**: Todo dinámico desde configuración
5. ✅ **Retrocompatible**: Reglas sin excepciones siguen funcionando igual

### Reglas que Soportarán Excepciones

| Regla | Razón | Ejemplos de Excepciones |
|-------|-------|-------------------------|
| **NOMENCLATURA_001** | Variables estándar del framework | `Config`, `TransactionItem`, `TransactionData` |
| **NOMENCLATURA_002** | Nombres genéricos oficiales | `Config`, `Data`, `Item`, `Exception` |
| **NOMENCLATURA_003** | Argumentos estándar | `in_Config`, `io_TransactionItem`, `in_TransactionData` |
| **NOMENCLATURA_005** | Variables PascalCase estándar | `Config`, `TransactionItem`, `SystemException` |
| **NOMENCLATURA_006** | Argumentos sin descripción (autogenerados) | `in_Config`, `out_Config` |

### Flujo de Validación con Excepciones

```
┌─────────────────────────────────────┐
│  Validar Variable/Argumento         │
└────────────┬────────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ ¿Está en      │  SI → ✅ SALTAR VALIDACIÓN
     │ excepciones?  │──────────────────────────►
     └───────┬───────┘
             │ NO
             ▼
     ┌───────────────┐
     │ Aplicar regla │
     │ normalmente   │
     └───────────────┘
```

---

## 📊 Estructura de Datos

### Modificación en BBPP_Master.json

#### **Antes** (sin excepciones):
```json
{
  "id": "NOMENCLATURA_002",
  "name": "Evitar nombres genéricos",
  "parameters": {
    "forbidden_names": ["var", "variable", "temp", ...],
    "generic_patterns": ["^var[_]?\\d+$", ...]
  }
}
```

#### **Después** (con excepciones):
```json
{
  "id": "NOMENCLATURA_002",
  "name": "Evitar nombres genéricos",
  "parameters": {
    "forbidden_names": ["var", "variable", "temp", ...],
    "generic_patterns": ["^var[_]?\\d+$", ...],
    "exceptions": [
      "Config",
      "TransactionItem",
      "TransactionData",
      "SystemException",
      "BusinessException",
      "in_Config",
      "io_TransactionItem",
      "in_TransactionData",
      "out_TransactionData"
    ]
  }
}
```

### Estructura del Campo `exceptions`

```python
"exceptions": [
  "NombreExacto1",    # Comparación case-sensitive
  "NombreExacto2",    # Debe coincidir exactamente
  "in_Config",        # Incluye prefijos de dirección
  "dt_Config"         # Incluye prefijos de tipo
]
```

**Importante**: La comparación es **exacta** (case-sensitive):
- ✅ `Config` coincide con excepción `Config`
- ❌ `config` NO coincide con excepción `Config`
- ❌ `MyConfig` NO coincide con excepción `Config`

---

## 🛠️ Implementación Backend

### Paso 1: Actualizar BBPP_Master.json

**Archivo**: `config/bbpp/BBPP_Master.json`

Agregar campo `exceptions` a las siguientes reglas:

#### **NOMENCLATURA_001** (Variables camelCase)
```json
{
  "id": "NOMENCLATURA_001",
  "parameters": {
    "allow_type_prefixes": true,
    "type_prefixes": [...],
    "exceptions": [
      "Config",
      "TransactionItem",
      "TransactionData",
      "TransactionNumber",
      "RetryNumber",
      "SystemException",
      "BusinessException"
    ]
  }
}
```

#### **NOMENCLATURA_002** (Evitar nombres genéricos)
```json
{
  "id": "NOMENCLATURA_002",
  "parameters": {
    "forbidden_names": [...],
    "generic_patterns": [...],
    "exceptions": [
      "Config",
      "TransactionItem",
      "TransactionData",
      "TransactionNumber",
      "RetryNumber",
      "SystemException",
      "BusinessException",
      "QueueRetry",
      "ConsecutiveSystemExceptions",
      "in_Config",
      "io_TransactionItem",
      "in_TransactionData",
      "out_TransactionData",
      "io_dt_TransactionData"
    ]
  }
}
```

#### **NOMENCLATURA_003** (Argumentos con prefijos)
```json
{
  "id": "NOMENCLATURA_003",
  "parameters": {
    "allow_type_prefixes": true,
    "type_prefixes": [...],
    "exceptions": [
      "in_Config",
      "io_TransactionItem",
      "in_TransactionData",
      "out_TransactionData",
      "io_dt_TransactionData",
      "in_TransactionNumber",
      "in_OrchestratorQueueName",
      "in_OrchestratorQueueFolder"
    ]
  }
}
```

#### **NOMENCLATURA_005** (Variables PascalCase)
```json
{
  "id": "NOMENCLATURA_005",
  "parameters": {
    "allow_type_prefixes": true,
    "type_prefixes": [...],
    "exceptions": [
      "Config",
      "TransactionItem",
      "TransactionData",
      "TransactionNumber",
      "RetryNumber",
      "SystemException",
      "BusinessException"
    ]
  }
}
```

#### **NOMENCLATURA_006** (Argumentos con descripción)
```json
{
  "id": "NOMENCLATURA_006",
  "parameters": {
    "min_length": 10,
    "exceptions": [
      "in_Config",
      "io_TransactionItem",
      "in_TransactionData",
      "out_TransactionData"
    ]
  }
}
```

---

### Paso 2: Modificar analyzer.py

**Archivo**: `src/analyzer.py`

#### 2.1 Modificar `_check_variable_naming()` (NOMENCLATURA_001)

**Ubicación**: Línea ~220

**ANTES**:
```python
def _check_variable_naming(self, data: Dict, rules: List[Dict]):
    """Validar nomenclatura de variables (camelCase)"""
    for rule in rules:
        if rule.get('id') != 'NOMENCLATURA_001':
            continue
        if not rule.get('enabled', True):
            continue

        params = rule.get('parameters', {})
        allow_type_prefixes = params.get('allow_type_prefixes', False)
        type_prefixes = params.get('type_prefixes', [])

        for var in data.get('variables', []):
            var_name = var.get('name', '')

            # ... resto del código
```

**DESPUÉS**:
```python
def _check_variable_naming(self, data: Dict, rules: List[Dict]):
    """Validar nomenclatura de variables (camelCase)"""
    for rule in rules:
        if rule.get('id') != 'NOMENCLATURA_001':
            continue
        if not rule.get('enabled', True):
            continue

        params = rule.get('parameters', {})
        allow_type_prefixes = params.get('allow_type_prefixes', False)
        type_prefixes = params.get('type_prefixes', [])

        # NUEVO: Obtener excepciones
        exceptions = params.get('exceptions', [])

        for var in data.get('variables', []):
            var_name = var.get('name', '')

            # NUEVO: Verificar si es una excepción
            if var_name in exceptions:
                continue  # Saltar validación

            # ... resto del código (sin cambios)
```

#### 2.2 Modificar `_check_generic_names()` (NOMENCLATURA_002)

**Ubicación**: Línea ~381

**ANTES**:
```python
def _check_generic_names(self, data: Dict, rules: List[Dict]):
    """Validar que las variables no tengan nombres genéricos"""
    for rule in rules:
        if rule.get('id') != 'NOMENCLATURA_002':
            continue
        if not rule.get('enabled', True):
            continue

        params = rule.get('parameters', {})
        forbidden_names = params.get('forbidden_names', [])
        generic_patterns = params.get('generic_patterns', [])

        for var in data.get('variables', []):
            var_name = var.get('name', '')

            # ... resto del código
```

**DESPUÉS**:
```python
def _check_generic_names(self, data: Dict, rules: List[Dict]):
    """Validar que las variables no tengan nombres genéricos"""
    for rule in rules:
        if rule.get('id') != 'NOMENCLATURA_002':
            continue
        if not rule.get('enabled', True):
            continue

        params = rule.get('parameters', {})
        forbidden_names = params.get('forbidden_names', [])
        generic_patterns = params.get('generic_patterns', [])

        # NUEVO: Obtener excepciones
        exceptions = params.get('exceptions', [])

        for var in data.get('variables', []):
            var_name = var.get('name', '')

            # NUEVO: Verificar si es una excepción
            if var_name in exceptions:
                continue  # Saltar validación

            # ... resto del código (sin cambios)

        # TAMBIÉN agregar para argumentos
        for arg in data.get('arguments', []):
            arg_name = arg.get('name', '')

            # NUEVO: Verificar si es una excepción
            if arg_name in exceptions:
                continue  # Saltar validación

            # ... resto del código (sin cambios)
```

#### 2.3 Modificar `_check_argument_prefixes()` (NOMENCLATURA_003)

**Ubicación**: Línea ~484

**ANTES**:
```python
def _check_argument_prefixes(self, data: Dict, rules: List[Dict]):
    """Validar que los argumentos tengan prefijos correctos"""
    for rule in rules:
        if rule.get('id') != 'NOMENCLATURA_003':
            continue
        if not rule.get('enabled', True):
            continue

        params = rule.get('parameters', {})
        allow_type_prefixes = params.get('allow_type_prefixes', False)
        type_prefixes = params.get('type_prefixes', [])

        for arg in data.get('arguments', []):
            arg_name = arg.get('name', '')
            direction = arg.get('direction', 'In')

            # ... resto del código
```

**DESPUÉS**:
```python
def _check_argument_prefixes(self, data: Dict, rules: List[Dict]):
    """Validar que los argumentos tengan prefijos correctos"""
    for rule in rules:
        if rule.get('id') != 'NOMENCLATURA_003':
            continue
        if not rule.get('enabled', True):
            continue

        params = rule.get('parameters', {})
        allow_type_prefixes = params.get('allow_type_prefixes', False)
        type_prefixes = params.get('type_prefixes', [])

        # NUEVO: Obtener excepciones
        exceptions = params.get('exceptions', [])

        for arg in data.get('arguments', []):
            arg_name = arg.get('name', '')
            direction = arg.get('direction', 'In')

            # NUEVO: Verificar si es una excepción
            if arg_name in exceptions:
                continue  # Saltar validación

            # ... resto del código (sin cambios)
```

#### 2.4 Modificar `_check_variable_naming_pascal()` (NOMENCLATURA_005)

**Ubicación**: Línea ~325

**ANTES**:
```python
def _check_variable_naming_pascal(self, data: Dict, rules: List[Dict]):
    """Validar nomenclatura de variables (PascalCase)"""
    for rule in rules:
        if rule.get('id') != 'NOMENCLATURA_005':
            continue
        if not rule.get('enabled', True):
            continue

        params = rule.get('parameters', {})
        allow_type_prefixes = params.get('allow_type_prefixes', False)
        type_prefixes = params.get('type_prefixes', [])

        for var in data.get('variables', []):
            var_name = var.get('name', '')

            # ... resto del código
```

**DESPUÉS**:
```python
def _check_variable_naming_pascal(self, data: Dict, rules: List[Dict]):
    """Validar nomenclatura de variables (PascalCase)"""
    for rule in rules:
        if rule.get('id') != 'NOMENCLATURA_005':
            continue
        if not rule.get('enabled', True):
            continue

        params = rule.get('parameters', {})
        allow_type_prefixes = params.get('allow_type_prefixes', False)
        type_prefixes = params.get('type_prefixes', [])

        # NUEVO: Obtener excepciones
        exceptions = params.get('exceptions', [])

        for var in data.get('variables', []):
            var_name = var.get('name', '')

            # NUEVO: Verificar si es una excepción
            if var_name in exceptions:
                continue  # Saltar validación

            # ... resto del código (sin cambios)
```

#### 2.5 Modificar `_check_argument_descriptions()` (NOMENCLATURA_006)

**Ubicación**: Línea ~593

**BUSCAR**:
```python
def _check_argument_descriptions(self, data: Dict, rules: List[Dict]):
    """Validar que los argumentos tengan descripciones claras"""
    for rule in rules:
        if rule.get('id') != 'NOMENCLATURA_006':
            continue
        if not rule.get('enabled', True):
            continue

        params = rule.get('parameters', {})
        min_length = params.get('min_length', {}).get('value', 10)
```

**AGREGAR después de obtener `min_length`**:
```python
        # NUEVO: Obtener excepciones
        exceptions = params.get('exceptions', [])

        for arg in data.get('arguments', []):
            arg_name = arg.get('name', '')

            # NUEVO: Verificar si es una excepción
            if arg_name in exceptions:
                continue  # Saltar validación

            # ... resto del código (sin cambios)
```

---

## 🎨 Implementación Frontend (UI)

### Paso 3: Modificar Diálogo de Edición de Regla

**Archivo**: `src/ui/rules_management_screen.py`

**Ubicación**: Función `_show_edit_dialog()` (línea ~310)

#### 3.1 Determinar si la Regla Soporta Excepciones

**AGREGAR después de línea ~483** (después de verificar `supports_type_prefixes`):

```python
# Verificar si esta regla soporta excepciones
supports_exceptions = rule_id in [
    'NOMENCLATURA_001',
    'NOMENCLATURA_002',
    'NOMENCLATURA_003',
    'NOMENCLATURA_005',
    'NOMENCLATURA_006'
]
```

#### 3.2 Agregar Sección de Excepciones en el Diálogo

**AGREGAR después de la sección de prefijos de tipo** (línea ~707):

```python
# NUEVA SECCIÓN: Excepciones
if supports_exceptions:
    # Separador
    ttk.Separator(params_frame, orient='horizontal').pack(fill=tk.X, pady=15)

    # Título de la sección
    tk.Label(
        params_frame,
        text="Excepciones de la Regla",
        font=("Arial", 11, "bold"),
        bg="white",
        fg=PRIMARY_COLOR
    ).pack(anchor="w", pady=(10, 5))

    # Descripción
    tk.Label(
        params_frame,
        text="Variables o argumentos que deben ignorarse durante la validación de esta regla.",
        font=("Arial", 9),
        bg="white",
        fg="gray",
        wraplength=520,
        justify=tk.LEFT
    ).pack(anchor="w", pady=(0, 10))

    # Frame para la lista de excepciones
    exceptions_frame = tk.Frame(params_frame, bg="white")
    exceptions_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    # Listbox con scrollbar
    exceptions_list_frame = tk.Frame(exceptions_frame, bg="white")
    exceptions_list_frame.pack(fill=tk.BOTH, expand=True)

    exceptions_scrollbar = tk.Scrollbar(exceptions_list_frame)
    exceptions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    exceptions_listbox = tk.Listbox(
        exceptions_list_frame,
        font=("Arial", 10),
        yscrollcommand=exceptions_scrollbar.set,
        selectmode=tk.SINGLE,
        height=8,
        bg="#F9F9F9"
    )
    exceptions_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    exceptions_scrollbar.config(command=exceptions_listbox.yview)

    # Cargar excepciones actuales
    current_exceptions = parameters.get('exceptions', [])
    exceptions_list = list(current_exceptions)  # Copia mutable

    for exc in exceptions_list:
        exceptions_listbox.insert(tk.END, exc)

    # Frame para botones de gestión
    exceptions_buttons_frame = tk.Frame(params_frame, bg="white")
    exceptions_buttons_frame.pack(fill=tk.X, pady=10)

    # Entry para nueva excepción
    new_exception_var = tk.StringVar()
    new_exception_entry = tk.Entry(
        exceptions_buttons_frame,
        textvariable=new_exception_var,
        font=("Arial", 10),
        width=30
    )
    new_exception_entry.pack(side=tk.LEFT, padx=(0, 10))

    def add_exception():
        """Agregar nueva excepción a la lista"""
        exception_name = new_exception_var.get().strip()

        if not exception_name:
            messagebox.showwarning(
                "Campo Vacío",
                "Por favor ingrese un nombre de excepción",
                parent=dialog
            )
            return

        if exception_name in exceptions_list:
            messagebox.showwarning(
                "Duplicado",
                f"La excepción '{exception_name}' ya existe en la lista",
                parent=dialog
            )
            return

        # Agregar a lista y listbox
        exceptions_list.append(exception_name)
        exceptions_listbox.insert(tk.END, exception_name)
        new_exception_var.set('')  # Limpiar campo

    def remove_exception():
        """Eliminar excepción seleccionada"""
        selection = exceptions_listbox.curselection()
        if not selection:
            messagebox.showwarning(
                "Sin Selección",
                "Por favor seleccione una excepción para eliminar",
                parent=dialog
            )
            return

        index = selection[0]
        exception_name = exceptions_listbox.get(index)

        # Confirmar eliminación
        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Eliminar la excepción '{exception_name}'?",
            parent=dialog
        ):
            exceptions_list.remove(exception_name)
            exceptions_listbox.delete(index)

    # Botón Agregar
    add_exception_btn = tk.Button(
        exceptions_buttons_frame,
        text="➕ Agregar",
        command=add_exception,
        bg=PRIMARY_COLOR,
        fg="white",
        font=("Arial", 9, "bold"),
        padx=15,
        pady=5
    )
    add_exception_btn.pack(side=tk.LEFT, padx=5)

    # Botón Eliminar
    remove_exception_btn = tk.Button(
        exceptions_buttons_frame,
        text="➖ Eliminar Seleccionado",
        command=remove_exception,
        bg="#DC3545",
        fg="white",
        font=("Arial", 9, "bold"),
        padx=15,
        pady=5
    )
    remove_exception_btn.pack(side=tk.LEFT, padx=5)

    # Permitir agregar con Enter
    new_exception_entry.bind('<Return>', lambda e: add_exception())
else:
    exceptions_list = None  # No soporta excepciones
```

#### 3.3 Guardar Excepciones al Aceptar

**MODIFICAR la función `on_accept()`** (línea ~771):

**AGREGAR después de guardar prefijos de tipo** (línea ~801):

```python
# Actualizar excepciones (si aplica)
if supports_exceptions and exceptions_list is not None:
    rule_obj = self.rules_manager.get_rule_by_id(rule_id)
    if rule_obj and 'parameters' in rule_obj:
        rule_obj['parameters']['exceptions'] = exceptions_list.copy()
        # Guardar cambios
        self.rules_manager.save_rules()
```

---

## 💻 Código Completo

### Código Completo para analyzer.py

#### Función Auxiliar (Agregar al inicio de la clase, después de `__init__`)

```python
def _is_exception(self, name: str, rule_id: str, rules: List[Dict]) -> bool:
    """
    Verificar si un nombre está en la lista de excepciones de una regla

    Args:
        name: Nombre a verificar
        rule_id: ID de la regla
        rules: Lista de reglas activas

    Returns:
        True si es una excepción, False en caso contrario
    """
    for rule in rules:
        if rule.get('id') == rule_id:
            exceptions = rule.get('parameters', {}).get('exceptions', [])
            return name in exceptions
    return False
```

#### Modificaciones Específicas

**NOMENCLATURA_001** (Variables camelCase):
```python
# Línea ~235 (dentro del loop de variables)
# AGREGAR después de obtener var_name:
if var_name in exceptions:
    continue
```

**NOMENCLATURA_002** (Nombres genéricos):
```python
# Línea ~395 (variables) y ~410 (argumentos)
# AGREGAR después de obtener var_name/arg_name:
if var_name in exceptions:  # o arg_name
    continue
```

**NOMENCLATURA_003** (Prefijos de argumentos):
```python
# Línea ~520 (dentro del loop de argumentos)
# AGREGAR después de obtener arg_name:
if arg_name in exceptions:
    continue
```

**NOMENCLATURA_005** (Variables PascalCase):
```python
# Línea ~340 (dentro del loop de variables)
# AGREGAR después de obtener var_name:
if var_name in exceptions:
    continue
```

**NOMENCLATURA_006** (Descripciones de argumentos):
```python
# Línea ~605 (dentro del loop de argumentos)
# AGREGAR después de obtener arg_name:
if arg_name in exceptions:
    continue
```

---

## 🧪 Pruebas y Validación

### Checklist de Pruebas

#### ✅ Prueba 1: Agregar Excepciones desde UI
1. Abrir "Gestión de Reglas BBPP"
2. Doble clic en NOMENCLATURA_002
3. Scroll hasta sección "Excepciones"
4. Escribir "Config" en el campo
5. Hacer clic "➕ Agregar"
6. Verificar que aparece en la lista
7. Hacer clic "✅ Aceptar"
8. Verificar mensaje de éxito

#### ✅ Prueba 2: Verificar Guardado en JSON
1. Abrir `config/bbpp/BBPP_Master.json`
2. Buscar NOMENCLATURA_002
3. Verificar que `parameters.exceptions` contiene `"Config"`

#### ✅ Prueba 3: Eliminar Excepción
1. Abrir diálogo de NOMENCLATURA_002
2. Seleccionar "Config" en la lista
3. Hacer clic "➖ Eliminar Seleccionado"
4. Confirmar eliminación
5. Guardar
6. Verificar en JSON que ya no está

#### ✅ Prueba 4: Excepciones Funcionan en Análisis
1. Asegurar que NOMENCLATURA_002 tiene excepciones:
   ```json
   "exceptions": ["Config", "TransactionItem"]
   ```
2. Ejecutar análisis del REFramework:
   ```bash
   python test_reframework.py
   ```
3. Verificar que variables `Config` y `TransactionItem` NO generan hallazgos
4. Verificar que otras variables genéricas SÍ generan hallazgos

#### ✅ Prueba 5: Enter Agrega Excepción
1. En diálogo de excepciones
2. Escribir nombre en campo
3. Presionar Enter (no clic en botón)
4. Verificar que se agrega a la lista

#### ✅ Prueba 6: Duplicados No Permitidos
1. Agregar "Config"
2. Intentar agregar "Config" de nuevo
3. Verificar mensaje de advertencia

#### ✅ Prueba 7: Campo Vacío No Permitido
1. Dejar campo vacío
2. Hacer clic "➕ Agregar"
3. Verificar mensaje de advertencia

#### ✅ Prueba 8: Excepciones Case-Sensitive
1. Agregar excepción "Config"
2. Ejecutar análisis con variable "config" (minúscula)
3. Verificar que "config" SÍ genera hallazgo (no es excepción)
4. Variable "Config" NO debe generar hallazgo

#### ✅ Prueba 9: Múltiples Reglas con Excepciones
1. Agregar "Config" a NOMENCLATURA_001
2. Agregar "Config" a NOMENCLATURA_002
3. Agregar "Config" a NOMENCLATURA_005
4. Ejecutar análisis
5. Verificar que "Config" no falla en ninguna de las 3 reglas

#### ✅ Prueba 10: Reglas Sin Excepciones Siguen Funcionando
1. ESTRUCTURA_001 no tiene sección de excepciones
2. Verificar que el diálogo se abre sin errores
3. Verificar que la regla sigue funcionando normalmente

---

## 📦 Excepciones Predefinidas REFramework

### Lista Completa para BBPP_Master.json

#### **NOMENCLATURA_001** (Variables camelCase)
```json
"exceptions": [
  "Config",
  "TransactionItem",
  "TransactionData",
  "TransactionNumber",
  "RetryNumber",
  "SystemException",
  "BusinessException",
  "QueueRetry",
  "ConsecutiveSystemExceptions"
]
```

#### **NOMENCLATURA_002** (Evitar nombres genéricos)
```json
"exceptions": [
  "Config",
  "TransactionItem",
  "TransactionData",
  "TransactionNumber",
  "RetryNumber",
  "SystemException",
  "BusinessException",
  "QueueRetry",
  "ConsecutiveSystemExceptions",
  "in_Config",
  "io_TransactionItem",
  "in_TransactionData",
  "out_TransactionData",
  "io_dt_TransactionData",
  "in_TransactionNumber",
  "in_OrchestratorQueueName",
  "in_OrchestratorQueueFolder",
  "io_TransactionNumber",
  "io_RetryNumber",
  "io_SystemException",
  "io_BusinessException",
  "io_QueueRetry",
  "io_ConsecutiveSystemExceptions"
]
```

#### **NOMENCLATURA_003** (Argumentos con prefijos)
```json
"exceptions": [
  "in_Config",
  "io_TransactionItem",
  "in_TransactionData",
  "out_TransactionData",
  "io_dt_TransactionData",
  "in_TransactionNumber",
  "in_OrchestratorQueueName",
  "in_OrchestratorQueueFolder",
  "io_TransactionNumber",
  "io_RetryNumber",
  "io_SystemException",
  "io_BusinessException",
  "io_QueueRetry",
  "io_ConsecutiveSystemExceptions"
]
```

#### **NOMENCLATURA_005** (Variables PascalCase)
```json
"exceptions": [
  "Config",
  "TransactionItem",
  "TransactionData",
  "TransactionNumber",
  "RetryNumber",
  "SystemException",
  "BusinessException",
  "QueueRetry",
  "ConsecutiveSystemExceptions"
]
```

#### **NOMENCLATURA_006** (Argumentos con descripción)
```json
"exceptions": [
  "in_Config",
  "io_TransactionItem",
  "in_TransactionData",
  "out_TransactionData",
  "in_OrchestratorQueueName",
  "in_OrchestratorQueueFolder"
]
```

---

## 📝 Notas Importantes

### Comparación Case-Sensitive

Las excepciones son **case-sensitive** (distinguen mayúsculas/minúsculas):
- `Config` ≠ `config`
- `TransactionItem` ≠ `transactionitem`

**Razón**: En UiPath, las variables son case-sensitive, por lo que las excepciones deben serlo también.

### Excepciones con Prefijos

Las excepciones pueden incluir prefijos de dirección y tipo:
- ✅ `in_Config` (excepción válida)
- ✅ `io_dt_TransactionData` (excepción válida)
- ✅ `dt_Config` (excepción válida)

**No es necesario agregar todas las combinaciones**. Solo agrega las que realmente existen en el REFramework.

### Excepciones Globales vs Por Conjunto

Las excepciones se guardan **por regla**, no por conjunto. Esto significa:
- Si agregas "Config" a NOMENCLATURA_002, aplica para **todos los conjuntos** (UiPath, NTTData, etc.)
- No se pueden tener excepciones diferentes para UiPath vs NTTData

**Razón**: Las excepciones son inherentes al REFramework oficial, que es el mismo para todos.

### Retrocompatibilidad

Si una regla **no tiene** el campo `exceptions` en BBPP_Master.json:
- `params.get('exceptions', [])` devuelve lista vacía `[]`
- El loop `if var_name in exceptions:` nunca se ejecuta
- La regla funciona exactamente igual que antes

**No rompe nada**.

---

## 🚀 Orden de Implementación Recomendado

1. **Backup de archivos**
   ```bash
   cp config/bbpp/BBPP_Master.json config/bbpp/BBPP_Master.json.backup
   cp src/analyzer.py src/analyzer.py.backup
   cp src/ui/rules_management_screen.py src/ui/rules_management_screen.py.backup
   ```

2. **Actualizar BBPP_Master.json**
   - Agregar campo `exceptions` a las 5 reglas
   - Poblar con excepciones del REFramework

3. **Modificar analyzer.py**
   - Agregar verificación de excepciones en 5 funciones
   - (Opcional) Agregar función auxiliar `_is_exception()`

4. **Modificar rules_management_screen.py**
   - Agregar sección de excepciones en diálogo
   - Agregar lógica de guardado

5. **Pruebas**
   - Ejecutar análisis del REFramework
   - Verificar reducción de hallazgos
   - Validar UI funcionando

6. **Commit**
   ```bash
   git add .
   git commit -m "feat: Sistema de excepciones para reglas BBPP"
   ```

---

## ✅ Checklist de Implementación

- [ ] Backup de archivos realizado
- [ ] BBPP_Master.json actualizado con excepciones
- [ ] analyzer.py modificado (5 funciones)
- [ ] rules_management_screen.py modificado (UI)
- [ ] Prueba 1: Agregar excepción desde UI ✓
- [ ] Prueba 2: Verificar guardado en JSON ✓
- [ ] Prueba 3: Eliminar excepción ✓
- [ ] Prueba 4: Análisis del REFramework sin falsos positivos ✓
- [ ] Prueba 5: Enter agrega excepción ✓
- [ ] Prueba 6: Duplicados rechazados ✓
- [ ] Prueba 7: Campo vacío rechazado ✓
- [ ] Prueba 8: Case-sensitive funciona ✓
- [ ] Commit realizado

---

**Documento creado**: 2025-11-29
**Versión**: 1.0
**Autor**: Claude Code
**Proyecto**: AnalizadorBBPP_UiPath

---

## 🎯 Resumen Ejecutivo

**Objetivo**: Eliminar falsos positivos del REFramework oficial de UiPath

**Solución**: Sistema de excepciones configurable por regla

**Impacto**:
- ✅ Score del REFramework mejorará significativamente
- ✅ No más hallazgos en variables/argumentos estándar del framework
- ✅ Reglas siguen funcionando para código custom

**Esfuerzo**:
- Backend: 5 funciones modificadas (~15 líneas cada una)
- Frontend: 1 sección nueva en UI (~150 líneas)
- JSON: Agregar campo `exceptions` a 5 reglas

**Estimación**: 1-2 horas de implementación + testing

¡Éxito con la implementación! 🚀
