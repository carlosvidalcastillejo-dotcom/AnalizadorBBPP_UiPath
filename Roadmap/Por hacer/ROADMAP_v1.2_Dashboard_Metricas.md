# 📊 ROADMAP v1.2 - Mejoras Dashboard de Métricas

**Proyecto:** Analizador de Buenas Prácticas UiPath
**Versión Objetivo:** 1.2.0
**Fecha Estimada:** Diciembre 2024
**Estimación:** 1-2 días
**Prioridad:** Alta

---

## 🎯 Objetivo

Mejorar la usabilidad, rendimiento y control del Dashboard de Métricas mediante:
1. Indicador visual de resultados mostrados
2. Control de límite configurable para búsquedas

---

## 📋 Tareas Detalladas

### 1. Indicador de Resultados Mostrados

**Descripción:** Agregar un mensaje informativo que muestre cuántos resultados se están visualizando del total disponible.

**Ubicación:** Debajo de la tabla de historial de análisis en el Dashboard de Métricas

**Especificaciones:**

#### 1.1 Diseño Visual
- **Texto:** `"Mostrando X de Y resultados"` o `"Mostrando X resultados"` (si no hay filtro)
- **Ejemplos:**
  - Sin filtro: `"Mostrando 82 resultados"`
  - Con filtro proyecto: `"Mostrando 82 de 105 resultados (filtrado por: RoboticEnterpriseFramework)"`
  - Con búsqueda: `"Mostrando 11 de 105 resultados (búsqueda: 'blank')"`
  - Con ambos: `"Mostrando 5 de 105 resultados (filtrado por: dummy_project, búsqueda: 'test')"`

- **Estilo:**
  - Fuente: Arial 9-10pt
  - Color: Gris oscuro (#666666)
  - Ubicación: Centrado o alineado a la izquierda debajo de la tabla
  - Padding: 5-10px vertical
  - Background: Opcional, fondo gris claro (#F5F5F5) con bordes redondeados

#### 1.2 Lógica de Actualización
- **Trigger 1:** Al cargar datos (`_load_data()`)
- **Trigger 2:** Al cambiar filtro de proyecto (`_on_filter_change()`)
- **Trigger 3:** Al escribir en búsqueda (`_on_search_change()`)

- **Cálculo:**
  ```python
  total_results = len(self.all_tree_items)  # Total cargado de DB
  visible_results = len(self.tree.get_children())  # Visible actualmente
  ```

#### 1.3 Implementación
- **Archivo:** `src/ui/metrics_dashboard.py`
- **Método nuevo:** `_update_results_indicator(visible, total, filter_info="")`
- **Widget:** `tk.Label` con textvariable `self.results_indicator_var`
- **Grid/Pack:** Debajo de `self.tree` con `sticky='w'` o centrado

**Checklist:**
- [ ] Crear widget Label para indicador
- [ ] Implementar método `_update_results_indicator()`
- [ ] Llamar al método en `_load_data()`
- [ ] Llamar al método en `_on_filter_change()`
- [ ] Llamar al método en `_on_search_change()`
- [ ] Testing con diferentes filtros y búsquedas
- [ ] Verificar actualización dinámica en tiempo real

---

### 2. Control de Límite de Búsqueda

**Descripción:** Permitir al usuario configurar un límite máximo de resultados a cargar para mejorar el rendimiento con grandes volúmenes de datos.

**Ubicación:** En la sección "Filtrar por Proyecto" del Dashboard de Métricas

**Especificaciones:**

#### 2.1 Diseño de Controles

**Layout propuesto:**
```
┌─────────────────────────────────────────────────────┐
│ 🔍 Filtrar por Proyecto                            │
├─────────────────────────────────────────────────────┤
│ Proyecto: [Dropdown: Todos ▼]                      │
│                                                     │
│ [ ✓ ] Limitar resultados: [100  ↑↓]               │
│       (desmarcar para cargar todos)                 │
└─────────────────────────────────────────────────────┘
```

**Componentes:**
1. **Checkbox:** `self.limit_checkbox`
   - Texto: "Limitar resultados:"
   - Estado inicial: Activado (checked)
   - Comando: `_on_limit_toggle()`

2. **Spinbox:** `self.limit_spinbox`
   - Rango: 10 - 10000
   - Valor por defecto: 100
   - Incremento: 10
   - Ancho: 8 caracteres
   - Estado: Habilitado/deshabilitado según checkbox
   - Comando: `_on_limit_change()`

3. **Label informativo:**
   - Texto pequeño: "(desmarcar para cargar todos)"
   - Color gris (#888888)
   - Fuente: Arial 8pt

#### 2.2 Lógica de Funcionamiento

**Comportamiento:**
- **Checkbox marcado:** Cargar solo los últimos N resultados (según spinbox)
  - `history = self.db.get_analysis_history(selected_project, limit=limit_value)`

- **Checkbox desmarcado:** Cargar TODOS los resultados (sin límite)
  - `history = self.db.get_analysis_history(selected_project, limit=None)`

**Interacción con búsqueda:**
- La búsqueda filtra **sobre los resultados cargados**
- Si límite = 100 y búsqueda no encuentra coincidencias, el usuario puede:
  - Aumentar el límite (ej: 500)
  - Desmarcar checkbox para cargar todos
  - Usar el dropdown de proyecto para filtrar primero

**Rendimiento:**
- Con límite activo: Carga rápida (100-500 análisis)
- Sin límite: Puede ser lento si hay 1000+ análisis
- Se debe mostrar loading indicator durante carga

#### 2.3 Persistencia de Configuración

**Archivo:** `config/user_config.json`

**Nuevos campos:**
```json
{
  "last_selected_bbpp_set": "UiPath",
  "metrics_dashboard": {
    "limit_enabled": true,
    "limit_value": 100
  }
}
```

**Funciones:**
- `load_user_config()` - Leer configuración al iniciar
- `save_user_config()` - Guardar al cambiar límite o checkbox

#### 2.4 Implementación

**Archivo:** `src/ui/metrics_dashboard.py`

**Métodos nuevos:**
```python
def _on_limit_toggle(self):
    """Manejar activación/desactivación del límite"""
    is_enabled = self.limit_enabled.get()

    # Habilitar/deshabilitar spinbox
    if is_enabled:
        self.limit_spinbox.config(state='normal')
    else:
        self.limit_spinbox.config(state='disabled')

    # Guardar en config
    user_config = load_user_config()
    if 'metrics_dashboard' not in user_config:
        user_config['metrics_dashboard'] = {}
    user_config['metrics_dashboard']['limit_enabled'] = is_enabled
    save_user_config(user_config)

    # Recargar datos
    self._load_data()

def _on_limit_change(self):
    """Manejar cambio en el valor del límite"""
    limit_value = self.limit_value.get()

    # Guardar en config
    user_config = load_user_config()
    if 'metrics_dashboard' not in user_config:
        user_config['metrics_dashboard'] = {}
    user_config['metrics_dashboard']['limit_value'] = limit_value
    save_user_config(user_config)

    # Recargar datos solo si checkbox está marcado
    if self.limit_enabled.get():
        self._load_data()

def _get_limit(self):
    """Obtener límite actual según configuración"""
    if hasattr(self, 'limit_enabled') and self.limit_enabled.get():
        return self.limit_value.get()
    else:
        return None
```

**Modificación en `_load_data()`:**
```python
def _load_data(self):
    # ... código existente ...

    # Obtener historial con límite configurable
    limit = self._get_limit()
    history = self.db.get_analysis_history(selected_project, limit=limit)

    # ... resto del código ...
```

**Checklist:**
- [ ] Agregar campos a `user_config.json` en `src/config.py`
- [ ] Crear Checkbox y Spinbox en Dashboard
- [ ] Implementar `_on_limit_toggle()`
- [ ] Implementar `_on_limit_change()`
- [ ] Implementar `_get_limit()`
- [ ] Modificar `_load_data()` para usar límite configurable
- [ ] Cargar valores de config al iniciar Dashboard
- [ ] Testing con límite activado/desactivado
- [ ] Testing con diferentes valores (10, 100, 500, 1000)
- [ ] Verificar persistencia al cerrar/abrir app
- [ ] Verificar interacción con búsqueda y filtro
- [ ] Optimizar rendimiento con 1000+ análisis

---

## 📊 Criterios de Aceptación

### Indicador de Resultados
- [x] ✅ El mensaje se muestra debajo de la tabla
- [ ] El mensaje se actualiza al cambiar filtro de proyecto
- [ ] El mensaje se actualiza al buscar en tiempo real
- [ ] El formato es claro y profesional
- [ ] Incluye información de filtros activos

### Control de Límite
- [ ] Checkbox y Spinbox funcionan correctamente
- [ ] Límite por defecto es 100
- [ ] Al desmarcar checkbox, carga TODOS los resultados
- [ ] Cambios se persisten en `user_config.json`
- [ ] Performance es buena con 100-500 resultados
- [ ] Sin límite funciona correctamente (aunque lento con 1000+)
- [ ] Búsqueda funciona sobre resultados cargados
- [ ] UI es intuitiva y clara

---

## 🧪 Plan de Testing

### Test 1: Indicador de Resultados
1. Abrir Dashboard de Métricas con 105 análisis en DB
2. Verificar mensaje: "Mostrando 100 de 105 resultados"
3. Seleccionar proyecto "RoboticEnterpriseFramework" (82 análisis)
4. Verificar mensaje: "Mostrando 82 de 105 resultados (filtrado por: RoboticEnterpriseFramework)"
5. Buscar "blank" (11 resultados esperados)
6. Verificar mensaje: "Mostrando 11 de 105 resultados (búsqueda: 'blank')"

### Test 2: Límite Activado
1. Marcar checkbox "Limitar resultados"
2. Establecer límite en 50
3. Verificar que solo carga 50 análisis (rápido)
4. Verificar mensaje: "Mostrando 50 de 105 resultados"
5. Buscar proyecto que está en posición 51-105
6. Verificar que NO aparece (no está cargado)

### Test 3: Límite Desactivado
1. Desmarcar checkbox "Limitar resultados"
2. Verificar que carga TODOS los análisis (puede ser lento)
3. Verificar mensaje: "Mostrando 105 resultados"
4. Buscar cualquier proyecto
5. Verificar que SÍ aparece (todos están cargados)

### Test 4: Persistencia
1. Establecer límite en 200 y marcar checkbox
2. Cerrar aplicación
3. Abrir aplicación
4. Ir a Dashboard de Métricas
5. Verificar que límite sigue en 200 y checkbox marcado

### Test 5: Performance
1. Crear 1000 análisis de prueba en DB
2. Con límite 100: Verificar carga rápida (<1 seg)
3. Con límite 1000: Verificar carga moderada (1-3 seg)
4. Sin límite: Verificar carga lenta pero funcional (3-10 seg)

---

## 📁 Archivos a Modificar

### Archivos Principales
1. **src/ui/metrics_dashboard.py**
   - Agregar indicador de resultados
   - Agregar checkbox y spinbox de límite
   - Implementar métodos `_update_results_indicator()`, `_on_limit_toggle()`, `_on_limit_change()`, `_get_limit()`
   - Modificar `_load_data()` para usar límite configurable

2. **src/config.py**
   - Agregar estructura de `metrics_dashboard` en `user_config.json`
   - Asegurar persistencia de `limit_enabled` y `limit_value`

3. **config/user_config.json**
   - Agregar campos nuevos (se crea automáticamente)

### Archivos de Documentación
4. **CHANGELOG.md**
   - Agregar entrada v1.2.0 con nuevas funcionalidades

5. **README.md**
   - Actualizar sección de Dashboard de Métricas
   - Mencionar indicador de resultados y control de límite

---

## 🎨 Mockup Visual

```
╔═══════════════════════════════════════════════════════════════════╗
║ 📊 Dashboard de Métricas                                          ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  📊 Estadísticas Generales                                        ║
║  ┌─────────────────────────────────────────────────────────────┐ ║
║  │ Total: 105  │  Score: 69.8  │  Último: 100.0  │  📈 Mejor  │ ║
║  └─────────────────────────────────────────────────────────────┘ ║
║                                                                   ║
║  🔍 Búsqueda en Tiempo Real                                       ║
║  ┌─────────────────────────────────────────────────────────────┐ ║
║  │ Buscar: [                                    ] [×]           │ ║
║  └─────────────────────────────────────────────────────────────┘ ║
║                                                                   ║
║  🔧 Filtrar por Proyecto                                          ║
║  ┌─────────────────────────────────────────────────────────────┐ ║
║  │ Proyecto: [Todos                            ▼]              │ ║
║  │                                                              │ ║
║  │ [✓] Limitar resultados: [100  ↑↓]                           │ ║
║  │     (desmarcar para cargar todos)                            │ ║
║  └─────────────────────────────────────────────────────────────┘ ║
║                                                                   ║
║  ┌─────────────────────────────────────────────────────────────┐ ║
║  │ Fecha        │ Proyecto      │ Ver. │ Score │ E │ W │ I │▲ │ ║
║  ├─────────────────────────────────────────────────────────────┤ ║
║  │ 2025-11-30   │ Robotic...    │ 1.0  │ 100.0 │99 │133│192│  │ ║
║  │ 2025-11-30   │ Robotic...    │ 1.0  │ 100.0 │99 │133│192│  │ ║
║  │ ...          │ ...           │ ...  │ ...   │.. │...│...│  │ ║
║  │              │               │      │       │   │   │   │▼ │ ║
║  └─────────────────────────────────────────────────────────────┘ ║
║                                                                   ║
║  Mostrando 100 de 105 resultados                                 ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## 📝 Notas Importantes

### Consideraciones de Rendimiento
- Base de datos SQLite es rápida hasta ~10,000 registros
- Con más de 1000 análisis, el límite por defecto (100) es recomendado
- La búsqueda en tiempo real debe ser instantánea (<100ms)
- Si el usuario nota lentitud, se le debe sugerir activar el límite

### Experiencia de Usuario
- El indicador de resultados debe ser **discreto pero visible**
- El control de límite debe tener un **label explicativo claro**
- Los valores deben ser **razonables** (10-10000)
- La persistencia debe ser **transparente** (sin confirmación)

### Mantenibilidad
- Código debe estar **bien comentado**
- Métodos deben ser **pequeños y específicos**
- Lógica de límite debe estar **centralizada** en `_get_limit()`
- Testing debe cubrir **todos los casos de uso**

---

**Documento creado:** 30 Noviembre 2024
**Autor:** Carlos Vidal Castillejo
**Versión del documento:** 1.0
