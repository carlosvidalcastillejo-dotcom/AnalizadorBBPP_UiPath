# Análisis de Nuevas Buenas Prácticas (BBPP)

**Fecha:** 2025-12-08
**Versión Actual:** 1.2.0 Stable
**Reglas Actuales:** 17 implementadas
**Reglas Totales en Excel:** 44
**Nuevas a Implementar:** 27

---

## 📊 RESUMEN EJECUTIVO

Del listado Excel proporcionado (44 reglas):
- ✅ **17 reglas YA IMPLEMENTADAS** (39%)
- ❌ **27 reglas NUEVAS** (61%)
- 🟢 **Auto-detectables completas:** ~18 reglas
- 🟡 **Auto-detectables parciales:** ~7 reglas
- 🔴 **No auto-detectables (manuales):** ~2 reglas

---

## ✅ REGLAS YA IMPLEMENTADAS (17)

| ID Excel | Nombre en Excel | ID Actual | Nombre Actual | Estado |
|----------|-----------------|-----------|---------------|--------|
| N.7 | Variables en camelCase | NOMENCLATURA_001 | Variables en camelCase | ✅ |
| - | Nombres genéricos | NOMENCLATURA_002 | Evitar nombres genéricos | ✅ |
| N.8-N.10 | Prefijos in_/out_/io_ | NOMENCLATURA_003 | Argumentos con prefijos | ✅ |
| - | Argumentos con descripción | NOMENCLATURA_004 | Argumentos con descripción | ✅ |
| - | Variables PascalCase | NOMENCLATURA_005 | Variables en PascalCase | ✅ |
| CG.4 | Anidación prohibida | ESTRUCTURA_001 | IFs anidados excesivos | ✅ |
| F.2 | Try-Catch vacíos | ESTRUCTURA_002 | Try-Catch vacíos | ✅ |
| - | Actividades críticas | ESTRUCTURA_003 | Actividades críticas en Try-Catch | ✅ |
| - | Sequences largos | MODULARIZACION_001 | Sequences muy largos | ✅ |
| - | Uso de Invoke | MODULARIZACION_002 | Uso de Invoke Workflow | ✅ |
| F.1 | REFramework | MODULARIZACION_003 | Patrón Init/End en State Machines | ✅ |
| G.4 | Código comentado | CODIGO_001 | Código comentado excesivo | ✅ |
| - | Logging insuficiente | LOGGING_001 | Logging insuficiente | ✅ |
| - | Logging inicio/fin | LOGGING_002 | Logging en inicio y fin | ✅ |
| CG.2 | Uso de Assets | CONFIGURACION_001 | Uso de Orchestrator Assets | ✅ |
| RT.2 | Timeout en actividades | RENDIMIENTO_001 | Timeouts explícitos | ✅ |
| CG.7 | Selectores limpios | SELECTORES_001 | Selectores estables | ✅ |

---

## ❌ REGLAS NUEVAS A IMPLEMENTAR (27)

### 🔴 PRIORIDAD CRÍTICA (7 reglas - Severidad: Error)

#### 1. **G.1** - Confidencialidad y Seguridad de la información
- **Categoría:** Seguridad
- **Severidad:** Error
- **Auto-detectable:** Parcial
- **Descripción:** No loggear datos sensibles (passwords, DNI, tarjetas). Encriptar datos en BBDD.
- **Implementación:**
  - Buscar LogMessage/WriteLine con keywords sensibles
  - Detectar Assign de strings con passwords/credentials
  - Buscar Send Outlook Mail sin encriptación
- **Complejidad:** Alta (requiere parsing contextual)
- **Estimación:** 6-8 horas
- **Parámetros:**
  ```json
  {
    "keywords_sensibles": ["password", "credential", "nif", "dni", "tarjeta", "cuenta", "iban"],
    "check_log_activities": true,
    "check_email_encryption": true
  }
  ```

#### 2. **DB.1** - Prohibido incluir consultas SQL en código
- **Categoría:** Bases de Datos
- **Severidad:** Error
- **Auto-detectable:** Sí
- **Descripción:** Solo ejecutar procedures. Prohibido SQL directo (SELECT, INSERT, UPDATE, DELETE).
- **Implementación:**
  - Buscar ExecuteQuery/ExecuteNonQuery
  - Validar CommandText no contenga keywords SQL
  - Debe ser solo nombre de procedure
- **Complejidad:** Media
- **Estimación:** 3-4 horas
- **Parámetros:**
  ```json
  {
    "allow_inline_sql": false,
    "check_procedures_only": true,
    "sql_keywords": ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP"]
  }
  ```

#### 3. **DB.2** - Cerrar conexiones en Finally
- **Categoría:** Bases de Datos
- **Severidad:** Error
- **Auto-detectable:** Sí
- **Descripción:** Asegurar cierre de conexiones BBDD en bloque Finally de TryCatch.
- **Implementación:**
  - Detectar DatabaseConnection/Connect
  - Verificar que esté dentro de TryCatch
  - Validar que Finally contenga Close/Disconnect
- **Complejidad:** Alta (análisis de flujo)
- **Estimación:** 5-6 horas
- **Parámetros:**
  ```json
  {
    "enforce_finally_close": true,
    "connection_activities": ["DatabaseConnection", "Connect"]
  }
  ```

#### 4. **F.1** - Uso de REFramework (MEJORADO)
- **Categoría:** Framework
- **Severidad:** Error
- **Auto-detectable:** Sí
- **Descripción:** Verificar estructura completa de REFramework con estados requeridos.
- **Implementación:**
  - Buscar StateMachine en Main.xaml
  - Validar existencia de estados: Initialization, GetTransactionData, Process, EndProcess
  - Verificar transiciones correctas
- **Complejidad:** Media (ya tenemos parcialmente en MODULARIZACION_003)
- **Estimación:** 4-5 horas (mejora de regla existente)
- **Parámetros:**
  ```json
  {
    "require_reframework": true,
    "required_states": ["Initialization", "GetTransactionData", "Process", "EndProcess"]
  }
  ```

#### 5. **F.2** - Un Try-Catch por estado (MEJORADO)
- **Categoría:** Framework
- **Severidad:** Error
- **Auto-detectable:** Sí
- **Descripción:** Cada estado debe tener UN SOLO Try-Catch. Prohibido anidar.
- **Implementación:**
  - Contar TryCatch dentro de cada State
  - Detectar TryCatch anidados
- **Complejidad:** Media (relacionado con ESTRUCTURA_002)
- **Estimación:** 3-4 horas
- **Parámetros:**
  ```json
  {
    "max_trycatch_per_state": 1,
    "allow_nested_trycatch": false
  }
  ```

#### 6. **CG.4** - Anidación prohibida (MEJORADO)
- **Categoría:** Código Limpio
- **Severidad:** Error (actualmente Warning)
- **Auto-detectable:** Sí
- **Descripción:** Máximo 1 nivel de anidación, solo ForEach/If permitidos.
- **Implementación:**
  - Ya implementado en ESTRUCTURA_001
  - Elevar severidad a Error
  - Limitar tipos permitidos
- **Complejidad:** Baja (solo ajustar existente)
- **Estimación:** 1-2 horas

#### 7. **CG.8** - Propiedades WaitForReady y DelayAfter
- **Categoría:** Navegación
- **Severidad:** Error
- **Auto-detectable:** Sí
- **Descripción:** WaitForReady=COMPLETE, DelayAfter>0 en actividades críticas.
- **Implementación:**
  - Buscar actividades UI (Click, Type, etc.)
  - Extraer WaitForReady y DelayAfter
  - Validar valores correctos
- **Complejidad:** Media
- **Estimación:** 4-5 horas
- **Parámetros:**
  ```json
  {
    "wait_for_ready": "COMPLETE",
    "min_delay_after_ms": 500,
    "critical_activities": ["Click", "TypeInto", "SelectItem"]
  }
  ```

---

### 🟠 PRIORIDAD ALTA (10 reglas - Severidad: Warning)

#### 8. **N.1** - Nombre del Proceso
- **Categoría:** Nomenclatura
- **Severidad:** Warning
- **Auto-detectable:** Sí
- **Patrón:** `^[A-Z]{3}_[A-Z0-9]{3}_[A-Za-z0-9_]+$`
- **Ejemplo:** ACC_014_NombreProceso
- **Complejidad:** Baja (leer project.json + regex)
- **Estimación:** 2 horas

#### 9. **N.2** - Nombre del Step
- **Categoría:** Nomenclatura
- **Severidad:** Warning
- **Auto-detectable:** Sí
- **Patrón:** `^[A-Z]{3}_[A-Z0-9]{3}_\d{2}\d[0-9A-Z]_[A-Za-z0-9]+_[A-Za-z0-9_]+$`
- **Ejemplo:** ACC_001_0100_App1_ConsultarOrden
- **Complejidad:** Baja (project.json + regex)
- **Estimación:** 2 horas

#### 10. **N.6** - Nombre de Assets
- **Categoría:** Nomenclatura
- **Severidad:** Warning
- **Auto-detectable:** Parcial
- **Descripción:** Assets deben iniciar con código de proceso. Credenciales incluyen aplicativo.
- **Complejidad:** Media (buscar GetAsset/GetCredential)
- **Estimación:** 3 horas

#### 11. **G.2** - Principio de simplicidad
- **Categoría:** Modularización
- **Severidad:** Warning
- **Auto-detectable:** Sí
- **Descripción:** Workflows con >200 actividades deben modularizarse.
- **Complejidad:** Baja (ya tenemos lógica similar en MODULARIZACION_001)
- **Estimación:** 2-3 horas

#### 12. **G.3** - Fallar de manera segura
- **Categoría:** Manejo de Errores
- **Severidad:** Warning
- **Auto-detectable:** Parcial
- **Descripción:** Mensajes de error sin datos sensibles. Screenshots en ruta segura.
- **Complejidad:** Alta (similar a G.1)
- **Estimación:** 5-6 horas

#### 13. **M.6** - Módulos sin lógica de negocio
- **Categoría:** Modularización
- **Severidad:** Warning
- **Auto-detectable:** Sí
- **Descripción:** Módulos no deben invocar otros workflows (máx 2 niveles).
- **Complejidad:** Media (análisis de profundidad)
- **Estimación:** 4 horas

#### 14. **M.7** - No capturar excepciones en módulos
- **Categoría:** Manejo de Errores
- **Severidad:** Warning
- **Auto-detectable:** Sí
- **Descripción:** Workflows invocados no deben tener Try-Catch.
- **Complejidad:** Media (identificar módulos + buscar TryCatch)
- **Estimación:** 3-4 horas

#### 15. **CG.3** - Uso de Actividades Modernas
- **Categoría:** Desarrollo
- **Severidad:** Warning
- **Auto-detectable:** Sí
- **Descripción:** project.json > projectProfile == "Simplified"
- **Complejidad:** Muy Baja (leer JSON)
- **Estimación:** 1 hora

#### 16. **CG.5** - Verificación de cambios de estado
- **Categoría:** Robustez
- **Severidad:** Warning
- **Auto-detectable:** Parcial
- **Descripción:** Usar CheckAppState/ElementExists antes de acciones críticas.
- **Complejidad:** Alta (análisis de secuencias)
- **Estimación:** 5-6 horas

#### 17. **CG.7** - Selectores limpios (MEJORADO)
- **Categoría:** Selectores
- **Severidad:** Warning
- **Auto-detectable:** Sí
- **Descripción:** Evitar idx, rutas completas. Usar comodines.
- **Complejidad:** Media (ya implementado SELECTORES_001, expandir)
- **Estimación:** 3-4 horas

---

### 🟡 PRIORIDAD MEDIA (7 reglas - Severidad: Info)

#### 18. **N.3** - Nombre de colas
- **Auto-detectable:** Parcial
- **Estimación:** 3 horas

#### 19. **N.4** - Formato de elemento en cola
- **Auto-detectable:** Sí
- **Estimación:** 4 horas

#### 20. **N.5** - Nombre de procedures
- **Auto-detectable:** Sí
- **Estimación:** 2-3 horas

#### 21. **G.5** - Descripciones (DisplayName)
- **Auto-detectable:** Sí
- **Estimación:** 2-3 horas

#### 22. **M.1** - Nombre de librería
- **Auto-detectable:** Sí
- **Estimación:** 2 horas

#### 23. **M.2** - Nombre del XAML en librería
- **Auto-detectable:** Sí
- **Estimación:** 2 horas

#### 24. **M.3** - Nota descriptiva en módulos
- **Auto-detectable:** Sí
- **Estimación:** 2-3 horas

#### 25. **M.4** - Validaciones en módulos
- **Auto-detectable:** Parcial
- **Estimación:** 4-5 horas

#### 26. **M.5** - Estructura de carpetas para módulos
- **Auto-detectable:** Sí
- **Estimación:** 2-3 horas

#### 27. **RT.1** - Uso de Retry Scope
- **Auto-detectable:** Sí
- **Estimación:** 4-5 horas

#### 28. **DB.3** - Esquema de tablas
- **Auto-detectable:** Parcial
- **Estimación:** 3-4 horas

#### 29. **CG.1** - Fichero de configuración en red
- **Auto-detectable:** Parcial
- **Estimación:** 3-4 horas

#### 30. **CG.6** - Maximizar ventanas
- **Auto-detectable:** Parcial
- **Estimación:** 3 horas

---

### 🟢 PRIORIDAD BAJA (3 reglas - Logs)

#### 31-33. **L.1, L.2, L.3** - Sistema de Logs
- **Estimación total:** 6-8 horas

---

## 📊 RESUMEN DE COMPLEJIDAD

| Complejidad | Cantidad | Horas Estimadas |
|-------------|----------|-----------------|
| Muy Baja | 1 | 1h |
| Baja | 5 | 10-12h |
| Media | 12 | 36-48h |
| Alta | 9 | 45-60h |
| **TOTAL** | **27** | **92-121h** |

---

## 🎯 PLAN DE IMPLEMENTACIÓN RECOMENDADO

### Sprint 1: Seguridad y BBDD (Críticas) - 20-25h
1. ✅ G.1 - Seguridad de datos sensibles
2. ✅ DB.1 - Prohibir SQL directo
3. ✅ DB.2 - Cerrar conexiones en Finally
4. ✅ CG.8 - WaitForReady/DelayAfter

### Sprint 2: Nomenclatura y Framework - 15-20h
5. ✅ N.1 - Nombre del Proceso
6. ✅ N.2 - Nombre del Step
7. ✅ N.6 - Nombre de Assets
8. ✅ F.1 - REFramework mejorado
9. ✅ F.2 - Un Try-Catch por estado

### Sprint 3: Modularización y Robustez - 20-25h
10. ✅ G.2 - Principio de simplicidad
11. ✅ G.3 - Fallar de manera segura
12. ✅ M.6 - Módulos sin lógica de negocio
13. ✅ M.7 - No capturar excepciones en módulos
14. ✅ CG.5 - Verificación de cambios de estado

### Sprint 4: Nomenclatura Avanzada - 10-15h
15. ✅ N.3 - Nombre de colas
16. ✅ N.4 - Formato de elemento en cola
17. ✅ N.5 - Nombre de procedures
18. ✅ G.5 - Descripciones

### Sprint 5: Librerías y Configuración - 12-18h
19. ✅ M.1 - Nombre de librería
20. ✅ M.2 - Nombre XAML en librería
21. ✅ M.3 - Nota descriptiva en módulos
22. ✅ M.4 - Validaciones en módulos
23. ✅ M.5 - Estructura de carpetas
24. ✅ CG.1 - Configuración en red
25. ✅ CG.3 - Actividades modernas

### Sprint 6: Retry, Navegación, Logs - 15-20h
26. ✅ RT.1 - Uso de Retry Scope
27. ✅ DB.3 - Esquema de tablas
28. ✅ CG.6 - Maximizar ventanas
29. ✅ CG.7 - Selectores mejorado
30. ✅ L.1, L.2, L.3 - Sistema de Logs

---

## 🔑 OBSERVACIONES IMPORTANTES

### Reglas que requieren mejora de existentes:
- **F.1** - Mejorar MODULARIZACION_003 para validar REFramework completo
- **F.2** - Relacionado con ESTRUCTURA_002 (Try-Catch)
- **CG.4** - Mejorar ESTRUCTURA_001 (elevar severidad)
- **CG.7** - Expandir SELECTORES_001

### Reglas complejas (requieren análisis contextual):
- **G.1** - Seguridad (parsing de variables sensibles)
- **G.3** - Mensajes de error seguros
- **DB.2** - Cierre de conexiones en Finally (análisis de flujo)
- **CG.5** - Verificación de estado (análisis de secuencias)
- **M.6** - Profundidad de invocaciones

### Reglas simples (alta prioridad para quick wins):
- **N.1, N.2** - Validación por regex
- **N.6** - Prefijos de Assets
- **CG.3** - Project profile
- **G.5** - DisplayName modificado

---

## 📈 IMPACTO ESTIMADO

Al completar las **27 nuevas reglas**, el proyecto tendrá:
- ✅ **44 reglas BBPP** en total
- ✅ **Cobertura completa** del estándar UiPath oficial
- ✅ **Seguridad reforzada** (reglas G.1, G.3, DB.*)
- ✅ **Framework validation** completa (REFramework)
- ✅ **Nomenclatura exhaustiva** (N.1-N.6)
- ✅ **Robustez y performance** (RT.1, CG.5, CG.8)

**Versión objetivo:** v1.3.0 (con las 44 reglas completas)

---

**Documento generado:** 2025-12-08
**Autor:** Claude Code
**Versión:** 1.0
