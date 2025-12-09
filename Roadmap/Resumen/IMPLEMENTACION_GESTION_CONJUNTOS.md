# 🔧 Implementación: Gestión de Conjuntos BBPP

## 📋 Índice
1. [Análisis de Viabilidad](#análisis-de-viabilidad)
2. [Diseño de la Solución](#diseño-de-la-solución)
3. [Implementación Paso a Paso](#implementación-paso-a-paso)
4. [Código Completo](#código-completo)
5. [Pruebas y Validación](#pruebas-y-validación)
6. [Troubleshooting](#troubleshooting)

---

## 📊 Análisis de Viabilidad

### ✅ VIABILIDAD: 100% FACTIBLE

**Objetivo**: Redesñar la interfaz de "Gestión de Reglas BBPP" para separar la gestión de conjuntos/entornos de la tabla principal, reduciendo el desorden visual.

### Estado Actual

**Archivo**: `src/ui/rules_management_screen.py`

**Tabla Principal** (líneas 192-220):
```python
columns = ("id", "name", "category", "severity", "penalty", "enabled", "uipath", "nttdata", "status")
```

**Problema**:
- Columnas `uipath` y `nttdata` hardcodeadas
- No escalable (si se agregan más conjuntos, habría que modificar código)
- Ocupa espacio horizontal innecesario
- Cluttered (desordenado)

**Solución**:
- Eliminar columnas `uipath` y `nttdata`
- Crear botón "🔧 Gestión de Conjuntos"
- Abrir diálogo modal con dropdown para seleccionar conjunto
- Mostrar todas las reglas con checkboxes de inclusión/exclusión
- Todo dinámico desde `BBPP_Master.json`

### Verificación de No-Hardcodeo

✅ Conjuntos leídos dinámicamente: `self.rules_manager.sets.keys()`
✅ Reglas leídas dinámicamente: `self.rules_manager.get_all_rules()`
✅ Dependencias leídas/guardadas en JSON: `get_set_dependencies()`, `set_set_dependencies()`
✅ Sin nombres hardcodeados en código

### Compatibilidad Retroactiva

✅ **No afecta** a `analyzer.py` (sigue leyendo `active_sets`)
✅ **No afecta** a `project_scanner.py`
✅ **Formato JSON idéntico** (sin cambios en estructura)
✅ **Scripts existentes funcionan** (`test_reframework.py`, etc.)

---

## 🎨 Diseño de la Solución

### Mockup de la Interfaz

```
┌────────────────────────────────────────────────────────────┐
│  🔧 Gestión de Conjuntos de Buenas Prácticas              │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Seleccionar Conjunto:  [▼ UiPath         ]  [Cargar]     │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  ☑ Conjunto Activo                                   │ │
│  │                                                       │ │
│  │  📦 Dependencias Configuradas: 5 paquetes            │ │
│  │  [📝 Editar Dependencias]                            │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌─── Reglas en este Conjunto ──────────────────────────┐ │
│  │  ☑ NOMENCLATURA_001 - Variables en camelCase        │ │
│  │  ☑ NOMENCLATURA_002 - Evitar nombres genéricos      │ │
│  │  ☑ NOMENCLATURA_003 - Argumentos con prefijos       │ │
│  │  ☐ NOMENCLATURA_004 - Comentarios en workflows      │ │
│  │  ☑ NOMENCLATURA_005 - Variables en PascalCase       │ │
│  │  ☑ ESTRUCTURA_001 - Workflows modulares             │ │
│  │  ...                                                 │ │
│  │  (scroll para ver más)                               │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│                       [💾 Guardar] [❌ Cerrar]            │
└────────────────────────────────────────────────────────────┘
```

### Flujo de Usuario

1. Usuario hace clic en "🔧 Gestión de Conjuntos"
2. Se abre diálogo modal
3. Usuario selecciona conjunto del dropdown (UiPath, NTTData, etc.)
4. Se cargan:
   - Estado activo/inactivo del conjunto
   - Número de dependencias
   - Lista de TODAS las reglas con checkboxes
5. Usuario marca/desmarca reglas para incluir/excluir del conjunto
6. Usuario hace clic en "💾 Guardar"
7. Se actualiza `BBPP_Master.json`
8. Se recarga tabla principal (sin mostrar columnas de conjuntos)

---

## 🛠️ Implementación Paso a Paso

### PASO 1: Simplificar la Tabla Principal

**Archivo**: `src/ui/rules_management_screen.py`

#### 1.1 Modificar definición de columnas (línea ~192)

**ANTES**:
```python
columns = ("id", "name", "category", "severity", "penalty", "enabled", "uipath", "nttdata", "status")
```

**DESPUÉS**:
```python
columns = ("id", "name", "category", "severity", "penalty", "enabled", "status")
```

#### 1.2 Eliminar headings y configuración de columnas (líneas ~201-209)

**ELIMINAR estas líneas**:
```python
self.tree.heading("uipath", text="UiPath")
self.tree.heading("nttdata", text="NTTData")
self.tree.column("uipath", width=80, anchor="center")
self.tree.column("nttdata", width=80, anchor="center")
```

#### 1.3 Modificar `_load_rules()` (líneas ~233-283)

**ELIMINAR estas líneas** (~254-255):
```python
# Checkmarks para conjuntos
uipath = "✅" if "UiPath" in rule.get('sets', []) else "❌"
nttdata = "✅" if "NTTData" in rule.get('sets', []) else "❌"
```

**MODIFICAR la inserción** (~269-273):

**ANTES**:
```python
self.tree.insert(
    "",
    tk.END,
    values=(rule_id, name, category, severity, penalty, enabled, uipath, nttdata, status_text),
    tags=(tag,)
)
```

**DESPUÉS**:
```python
self.tree.insert(
    "",
    tk.END,
    values=(rule_id, name, category, severity, penalty, enabled, status_text),
    tags=(tag,)
)
```

---

### PASO 2: Agregar Botón "Gestión de Conjuntos"

**Ubicación**: Después del botón "Desactivar Todas" (~línea 141)

**AGREGAR**:
```python
# Botón Gestión de Conjuntos
sets_mgmt_btn = tk.Button(
    buttons_frame,
    text="🔧 Gestión de Conjuntos",
    font=("Arial", 10),
    bg=ACCENT_COLOR,
    fg="white",
    relief=tk.FLAT,
    cursor="hand2",
    command=self._show_sets_management_dialog
)
sets_mgmt_btn.pack(side=tk.LEFT, padx=5)
```

---

### PASO 3: Crear Función del Diálogo

**Ubicación**: Al final de la clase `RulesManagementScreen`, antes de la sección de dependencias (~línea 969)

**AGREGAR FUNCIÓN COMPLETA** (ver sección [Código Completo](#código-completo))

---

### PASO 4: (OPCIONAL) Eliminar Sección Redundante

**Ubicación**: Líneas 143-182

La sección "Gestión de Conjuntos y Dependencias" que muestra los conjuntos con botones de dependencias se vuelve redundante.

**Decisión**:
- **Opción A**: Eliminarla completamente (recomendado para UI más limpia)
- **Opción B**: Mantenerla como vista rápida

**Si decides eliminar** (Opción A):
```python
# COMENTAR O ELIMINAR desde línea ~143 hasta ~182
# Frame de Gestión de Conjuntos
# sets_mgmt_frame = tk.LabelFrame(...)
# ...
# sets_mgmt_frame.pack(...)
```

---

## 💻 Código Completo

### Función `_show_sets_management_dialog()` Completa

```python
def _show_sets_management_dialog(self):
    """
    Mostrar diálogo para gestionar conjuntos de BBPP
    Permite seleccionar un conjunto y gestionar qué reglas pertenecen a él
    """
    # Crear ventana modal
    dialog = tk.Toplevel(self.parent)
    dialog.title("🔧 Gestión de Conjuntos de Buenas Prácticas")
    dialog.geometry("800x700")
    dialog.transient(self.parent)
    dialog.grab_set()

    # Centrar ventana
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - 400
    y = (dialog.winfo_screenheight() // 2) - 350
    dialog.geometry(f"800x700+{x}+{y}")

    # Frame principal
    main_frame = tk.Frame(dialog, bg="white", padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Título
    tk.Label(
        main_frame,
        text="Gestión de Conjuntos de Buenas Prácticas",
        font=("Arial", 14, "bold"),
        bg="white",
        fg=PRIMARY_COLOR
    ).pack(pady=(0, 20))

    # Descripción
    tk.Label(
        main_frame,
        text="Seleccione un conjunto y marque las reglas que desea incluir en él.",
        font=("Arial", 9),
        bg="white",
        fg="gray",
        wraplength=750
    ).pack(pady=(0, 10))

    # Frame de selección de conjunto
    select_frame = tk.Frame(main_frame, bg="white")
    select_frame.pack(fill=tk.X, pady=10)

    tk.Label(
        select_frame,
        text="Seleccionar Conjunto:",
        font=("Arial", 10, "bold"),
        bg="white"
    ).pack(side=tk.LEFT, padx=(0, 10))

    # Obtener conjuntos dinámicamente desde rules_manager
    available_sets = list(self.rules_manager.sets.keys())
    if not available_sets:
        messagebox.showwarning(
            "Sin Conjuntos",
            "No hay conjuntos configurados en BBPP_Master.json",
            parent=dialog
        )
        dialog.destroy()
        return

    selected_set = tk.StringVar(value=available_sets[0])

    set_combo = ttk.Combobox(
        select_frame,
        textvariable=selected_set,
        values=available_sets,
        state="readonly",
        width=30,
        font=("Arial", 10)
    )
    set_combo.pack(side=tk.LEFT, padx=10)

    # Variables para UI
    set_enabled_var = tk.BooleanVar()
    rules_checkboxes = {}  # {rule_id: BooleanVar}

    # Frame de información del conjunto
    info_frame = tk.LabelFrame(
        main_frame,
        text="Información del Conjunto",
        font=("Arial", 10, "bold"),
        bg="white",
        padx=10,
        pady=10
    )
    info_frame.pack(fill=tk.X, pady=10)

    # Checkbox conjunto activo
    enabled_check = tk.Checkbutton(
        info_frame,
        text="☑ Conjunto Activo",
        variable=set_enabled_var,
        font=("Arial", 10, "bold"),
        bg="white",
        fg=COLOR_SUCCESS
    )
    enabled_check.pack(anchor="w", pady=5)

    # Label de info de dependencias
    deps_label = tk.Label(
        info_frame,
        text="",
        font=("Arial", 9),
        bg="white",
        fg="gray"
    )
    deps_label.pack(anchor="w", pady=5)

    # Botón para editar dependencias (reutiliza función existente)
    def edit_dependencies():
        """Abrir diálogo de dependencias para el conjunto seleccionado"""
        self._show_dependency_dialog(selected_set.get())
        # Recargar info después de editar
        load_set_info()

    deps_btn = tk.Button(
        info_frame,
        text="📝 Editar Dependencias",
        command=edit_dependencies,
        bg=SECONDARY_COLOR,
        fg="white",
        font=("Arial", 9),
        padx=10,
        pady=5
    )
    deps_btn.pack(anchor="w", pady=5)

    # Frame de reglas con scroll
    rules_frame = tk.LabelFrame(
        main_frame,
        text="Reglas en este Conjunto",
        font=("Arial", 10, "bold"),
        bg="white",
        padx=10,
        pady=10
    )
    rules_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    # Canvas para scroll
    rules_canvas = tk.Canvas(rules_frame, bg="white", highlightthickness=0)
    rules_scrollbar = ttk.Scrollbar(rules_frame, orient=tk.VERTICAL, command=rules_canvas.yview)
    rules_content = tk.Frame(rules_canvas, bg="white")

    rules_content.bind(
        "<Configure>",
        lambda e: rules_canvas.configure(scrollregion=rules_canvas.bbox("all"))
    )

    rules_canvas.create_window((0, 0), window=rules_content, anchor="nw", width=730)
    rules_canvas.configure(yscrollcommand=rules_scrollbar.set)

    # Habilitar scroll con rueda del mouse
    def _on_mousewheel(event):
        rules_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    rules_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    rules_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    rules_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_set_info():
        """
        Cargar información del conjunto seleccionado:
        - Estado activo/inactivo
        - Número de dependencias
        - Checkboxes de reglas
        """
        set_name = selected_set.get()
        if not set_name:
            return

        # Obtener datos del conjunto
        set_data = self.rules_manager.sets.get(set_name, {})

        # Actualizar checkbox de activo
        set_enabled_var.set(set_data.get('enabled', True))

        # Actualizar label de dependencias
        deps = set_data.get('dependencies', {})
        deps_count = len(deps)
        deps_label.config(text=f"📦 {deps_count} dependencia{'s' if deps_count != 1 else ''} configurada{'s' if deps_count != 1 else ''}")

        # Limpiar checkboxes anteriores
        for widget in rules_content.winfo_children():
            widget.destroy()
        rules_checkboxes.clear()

        # Crear checkboxes para TODAS las reglas
        all_rules = self.rules_manager.get_all_rules()

        for rule in all_rules:
            rule_id = rule.get('id', '')
            rule_name = rule.get('name', '')

            # Verificar si la regla pertenece a este conjunto
            is_in_set = set_name in rule.get('sets', [])

            # Crear variable y checkbox
            var = tk.BooleanVar(value=is_in_set)
            rules_checkboxes[rule_id] = var

            check = tk.Checkbutton(
                rules_content,
                text=f"{rule_id} - {rule_name}",
                variable=var,
                font=("Arial", 9),
                bg="white",
                anchor="w"
            )
            check.pack(fill=tk.X, pady=2, padx=5)

    def on_set_changed(*args):
        """Evento cuando se cambia el conjunto seleccionado en el dropdown"""
        load_set_info()

    # Vincular evento de cambio de conjunto
    selected_set.trace('w', on_set_changed)

    # Cargar información inicial
    load_set_info()

    # Botones de acción
    buttons_frame = tk.Frame(main_frame, bg="white")
    buttons_frame.pack(fill=tk.X, pady=10)

    def save_changes():
        """
        Guardar cambios del conjunto:
        1. Actualizar estado activo/inactivo del conjunto
        2. Actualizar qué reglas pertenecen al conjunto
        3. Guardar a BBPP_Master.json
        """
        set_name = selected_set.get()
        if not set_name:
            return

        # 1. Actualizar enabled del conjunto
        self.rules_manager.sets[set_name]['enabled'] = set_enabled_var.get()

        # 2. Actualizar reglas: añadir/quitar del conjunto según checkboxes
        for rule_id, var in rules_checkboxes.items():
            rule = self.rules_manager.get_rule_by_id(rule_id)
            if not rule:
                continue

            current_sets = rule.get('sets', []).copy()  # Copiar para no mutar
            is_checked = var.get()

            # Añadir al conjunto si está marcado y no está
            if is_checked and set_name not in current_sets:
                current_sets.append(set_name)
            # Quitar del conjunto si no está marcado pero está
            elif not is_checked and set_name in current_sets:
                current_sets.remove(set_name)

            # Actualizar regla
            self.rules_manager.update_rule(rule_id, {'sets': current_sets})

        # 3. Guardar a archivo
        if self.rules_manager.save_rules():
            messagebox.showinfo(
                "Éxito",
                f"✅ Conjunto '{set_name}' actualizado correctamente",
                parent=dialog
            )
            # Recargar tabla principal para reflejar cambios
            self._load_rules()
        else:
            messagebox.showerror(
                "Error",
                "❌ Error al guardar cambios",
                parent=dialog
            )

    # Botón Guardar
    tk.Button(
        buttons_frame,
        text="💾 Guardar Cambios",
        command=save_changes,
        bg=COLOR_SUCCESS,
        fg="white",
        font=("Arial", 10, "bold"),
        padx=20,
        pady=8
    ).pack(side=tk.LEFT, padx=5)

    # Botón Cerrar
    tk.Button(
        buttons_frame,
        text="❌ Cerrar",
        command=dialog.destroy,
        bg="#DC3545",
        fg="white",
        font=("Arial", 10),
        padx=20,
        pady=8
    ).pack(side=tk.RIGHT, padx=5)
```

---

## 🧪 Pruebas y Validación

### Checklist de Pruebas

Después de implementar, verificar:

#### ✅ Prueba 1: Tabla Simplificada
1. Abrir "Gestión de Reglas BBPP"
2. Verificar que la tabla NO muestra columnas "UiPath" y "NTTData"
3. Verificar que muestra: ID, Nombre, Categoría, Severidad, Penalización, Activa, Estado

#### ✅ Prueba 2: Botón de Gestión de Conjuntos
1. Verificar que existe botón "🔧 Gestión de Conjuntos"
2. Hacer clic → debe abrir diálogo modal
3. Verificar que el diálogo se centra en pantalla

#### ✅ Prueba 3: Carga de Conjuntos Dinámica
1. En el diálogo, verificar que el dropdown muestra "UiPath" y "NTTData"
2. Si agregas un nuevo conjunto en `BBPP_Master.json`, debe aparecer automáticamente

#### ✅ Prueba 4: Información del Conjunto
1. Seleccionar "UiPath" del dropdown
2. Verificar que muestra:
   - Checkbox "Conjunto Activo" (marcado si `"enabled": true`)
   - Número correcto de dependencias
   - Botón "Editar Dependencias" funcional

#### ✅ Prueba 5: Checkboxes de Reglas
1. Verificar que muestra TODAS las reglas (17 en total)
2. Reglas con ✅ = pertenecen al conjunto UiPath
3. Reglas con ☐ = NO pertenecen
4. Verificar scroll funciona si hay muchas reglas

#### ✅ Prueba 6: Cambiar de Conjunto
1. Cambiar dropdown de "UiPath" a "NTTData"
2. Verificar que los checkboxes se actualizan automáticamente
3. Reglas diferentes pueden estar marcadas

#### ✅ Prueba 7: Guardar Cambios
1. Desmarcar una regla que estaba incluida (ej: NOMENCLATURA_001)
2. Hacer clic en "💾 Guardar Cambios"
3. Verificar mensaje de éxito
4. Abrir `BBPP_Master.json` → verificar que la regla ya no tiene "UiPath" en `sets`
5. Volver a abrir el diálogo → verificar que el checkbox permanece desmarcado

#### ✅ Prueba 8: Activar/Desactivar Conjunto
1. Desmarcar "☑ Conjunto Activo"
2. Guardar
3. Verificar en JSON: `"UiPath": { "enabled": false }`

#### ✅ Prueba 9: Editar Dependencias
1. Hacer clic en "📝 Editar Dependencias"
2. Debe abrir el diálogo existente de dependencias
3. Agregar una dependencia nueva
4. Guardar
5. Volver al diálogo de conjuntos → verificar que el contador aumentó

#### ✅ Prueba 10: Compatibilidad con Análisis
1. Cerrar la aplicación
2. Ejecutar un análisis con `test_reframework.py`
3. Verificar que funciona igual que antes (sin errores)
4. El análisis debe respetar los conjuntos activos

---

## 🐛 Troubleshooting

### Problema 1: "No se puede importar tk"

**Síntoma**: Error al abrir el diálogo
```
NameError: name 'tk' is not defined
```

**Solución**: Verificar imports al inicio del archivo:
```python
import tkinter as tk
from tkinter import ttk, messagebox
```

---

### Problema 2: Diálogo no se centra

**Síntoma**: El diálogo aparece en esquina superior izquierda

**Solución**: Verificar que estas líneas están presentes:
```python
dialog.update_idletasks()
x = (dialog.winfo_screenwidth() // 2) - 400
y = (dialog.winfo_screenheight() // 2) - 350
dialog.geometry(f"800x700+{x}+{y}")
```

---

### Problema 3: Checkboxes no se actualizan al cambiar conjunto

**Síntoma**: Al cambiar de "UiPath" a "NTTData", los checkboxes quedan igual

**Solución**: Verificar que el trace está configurado:
```python
selected_set.trace('w', on_set_changed)
```

Y que `on_set_changed` llama a `load_set_info()`

---

### Problema 4: Scroll no funciona con rueda del mouse

**Síntoma**: No se puede hacer scroll con la rueda

**Solución**: Agregar binding:
```python
def _on_mousewheel(event):
    rules_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
rules_canvas.bind_all("<MouseWheel>", _on_mousewheel)
```

**IMPORTANTE**: Esto puede causar problemas si hay múltiples diálogos abiertos. Considera usar:
```python
rules_canvas.bind("<MouseWheel>", _on_mousewheel)  # Solo cuando mouse sobre canvas
```

---

### Problema 5: Cambios no se guardan en JSON

**Síntoma**: Al hacer cambios y guardar, el JSON no se actualiza

**Debugging**:
1. Verificar que `self.rules_manager.save_rules()` retorna `True`
2. Revisar permisos del archivo `BBPP_Master.json`
3. Verificar que no hay errores en consola
4. Comprobar que el archivo no está abierto en otro programa

**Solución**: Agregar logging:
```python
print(f"DEBUG: Guardando conjunto {set_name}")
print(f"DEBUG: Enabled = {set_enabled_var.get()}")
for rule_id, var in rules_checkboxes.items():
    if var.get():
        print(f"  - {rule_id}: incluida")
```

---

### Problema 6: Error "list index out of range" al abrir diálogo

**Síntoma**:
```
IndexError: list index out of range
available_sets[0]
```

**Causa**: No hay conjuntos en `BBPP_Master.json`

**Solución**: Ya está manejado en el código:
```python
if not available_sets:
    messagebox.showwarning(...)
    dialog.destroy()
    return
```

---

## 📝 Notas Adicionales

### Extensibilidad Futura

Esta implementación permite:

1. **Agregar nuevos conjuntos** fácilmente:
   ```json
   "sets": {
     "UiPath": {...},
     "NTTData": {...},
     "MiEmpresa": {
       "name": "Buenas Prácticas Mi Empresa",
       "description": "Estándares personalizados",
       "enabled": true,
       "dependencies": {}
     }
   }
   ```

2. **Crear conjuntos personalizados** desde la UI (feature futura):
   - Botón "➕ Nuevo Conjunto" en el diálogo
   - Formulario para nombre, descripción
   - Automáticamente aparece en dropdown

3. **Importar/Exportar conjuntos** (feature futura):
   - Exportar conjunto como JSON independiente
   - Compartir entre proyectos/equipos

### Mejoras Opcionales

#### Mejora 1: Búsqueda de Reglas

Agregar campo de búsqueda en el diálogo:
```python
search_var = tk.StringVar()
search_entry = tk.Entry(rules_frame, textvariable=search_var, ...)
search_var.trace('w', lambda *args: filter_rules(search_var.get()))
```

#### Mejora 2: Contador de Reglas Seleccionadas

Mostrar "15 de 17 reglas seleccionadas":
```python
def update_counter():
    selected = sum(1 for var in rules_checkboxes.values() if var.get())
    total = len(rules_checkboxes)
    counter_label.config(text=f"{selected} de {total} reglas seleccionadas")
```

#### Mejora 3: Botones "Seleccionar Todas" / "Deseleccionar Todas"

```python
def select_all():
    for var in rules_checkboxes.values():
        var.set(True)

def deselect_all():
    for var in rules_checkboxes.values():
        var.set(False)
```

#### Mejora 4: Confirmación antes de Cerrar con Cambios

Detectar si hay cambios sin guardar:
```python
def on_closing():
    if has_unsaved_changes():
        if messagebox.askyesno("Cambios sin Guardar",
                               "¿Descartar cambios?",
                               parent=dialog):
            dialog.destroy()
    else:
        dialog.destroy()

dialog.protocol("WM_DELETE_WINDOW", on_closing)
```

---

## ✅ Checklist de Implementación

Usa esta lista para verificar que completaste todos los pasos:

- [ ] **PASO 1.1**: Modificar definición de columnas (línea ~192)
- [ ] **PASO 1.2**: Eliminar headings de `uipath` y `nttdata` (líneas ~201-209)
- [ ] **PASO 1.3**: Eliminar variables `uipath` y `nttdata` en `_load_rules()` (~254-255)
- [ ] **PASO 1.4**: Actualizar `tree.insert()` para usar 7 columnas en vez de 9 (~269-273)
- [ ] **PASO 2**: Agregar botón "🔧 Gestión de Conjuntos" (~línea 141)
- [ ] **PASO 3**: Agregar función completa `_show_sets_management_dialog()` (~línea 969)
- [ ] **PASO 4** (opcional): Eliminar sección redundante de conjuntos (líneas 143-182)
- [ ] **PRUEBAS**: Ejecutar todas las pruebas del checklist
- [ ] **VALIDACIÓN**: Verificar que análisis sigue funcionando correctamente

---

## 📞 Contacto y Soporte

Si encuentras problemas durante la implementación:

1. Revisa la sección [Troubleshooting](#troubleshooting)
2. Verifica que seguiste todos los pasos del checklist
3. Comprueba logs en consola (buscar errores de Python)
4. Valida sintaxis del código (indentación, paréntesis, comillas)

---

**Documento creado**: 2025-11-29
**Versión**: 1.0
**Autor**: Claude Code
**Proyecto**: AnalizadorBBPP_UiPath

---

## 🎯 Resumen Ejecutivo

**Lo que vas a lograr**:
- ✅ Tabla principal más limpia (eliminar 2 columnas hardcodeadas)
- ✅ Sistema escalable (funciona con N conjuntos, no solo 2)
- ✅ Gestión centralizada de conjuntos en un solo lugar
- ✅ Mejor UX (menos clicks, más intuitivo)
- ✅ Sin hardcodeo (todo dinámico desde JSON)
- ✅ Compatible con código existente (sin romper nada)

**Esfuerzo estimado**: 30-45 minutos
**Archivos a modificar**: 1 (`src/ui/rules_management_screen.py`)
**Líneas de código**: ~350 nuevas, ~15 eliminadas, ~5 modificadas

¡Éxito con la implementación! 🚀
