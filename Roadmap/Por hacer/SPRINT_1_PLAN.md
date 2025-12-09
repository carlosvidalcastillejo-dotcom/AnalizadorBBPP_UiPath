# 🚀 SPRINT 1 - Plan de Implementación

## Fecha Inicio: 2025-12-07
## Duración Estimada: 1 sesión
## Objetivo: Mejorar sistema de distribución y actualización

---

## 📋 TAREAS DEL SPRINT

### 1. 🔄 Optimizar Instalador (Descarga desde main)
**Prioridad:** CRÍTICA  
**Tiempo estimado:** 30 minutos  
**Estado:** 🔴 PENDIENTE

#### Objetivo:
Asegurar que el instalador siempre descargue el código desde la rama `main` en lugar de `develop`.

#### Archivos a modificar:
- `installer/installer_script.iss`
- `installer/download_and_install.ps1` (si existe)

#### Pasos:
1. Revisar script actual del instalador
2. Identificar URL de descarga de GitHub
3. Cambiar referencia de `develop` a `main`
4. Añadir validación de rama
5. Probar instalación

#### Criterios de aceptación:
- ✅ Instalador descarga desde `main`
- ✅ No hay referencias a `develop` en scripts de instalación
- ✅ Instalación funciona correctamente

---

### 2. 🤖 Configuración Básica de IA
**Prioridad:** ALTA  
**Tiempo estimado:** 2 horas  
**Estado:** 🔴 PENDIENTE

#### Objetivo:
Crear pantalla de configuración para conectar con APIs de IA (OpenAI, Gemini, Claude).

#### Archivos a crear:
- `src/ai/__init__.py`
- `src/ai/ai_manager.py`
- `src/ai/config.py`
- `src/ui/ai_config_screen.py`

#### Archivos a modificar:
- `src/ui/main_window.py` (añadir opción en menú)
- `config/user_config.json` (añadir sección AI)

#### Funcionalidades:
1. **Pantalla de Configuración:**
   - Selector de proveedor (OpenAI, Gemini, Claude, Desactivado)
   - Campo para API Key (con botón mostrar/ocultar)
   - Selector de modelo
   - Botón "Probar Conexión"
   - Guardar/Cancelar

2. **Backend:**
   - Clase `AIManager` para gestionar proveedores
   - Encriptación de API Keys
   - Validación de conexión
   - Manejo de errores

#### Criterios de aceptación:
- ✅ Pantalla de configuración funcional
- ✅ API Keys se guardan encriptadas
- ✅ Test de conexión funciona
- ✅ Soporte para al menos 2 proveedores (OpenAI, Gemini)

---

### 3. 🔄 Botón de Actualización Automática
**Prioridad:** ALTA  
**Tiempo estimado:** 2 horas  
**Estado:** 🔴 PENDIENTE

#### Objetivo:
Implementar sistema de actualización automática que detecte nuevas versiones en GitHub.

#### Archivos a crear:
- `src/updater.py`
- `src/ui/update_dialog.py`

#### Archivos a modificar:
- `src/ui/main_window.py` (añadir botón/menú)
- `src/config.py` (añadir configuración de updates)

#### Funcionalidades:
1. **Detección de Versiones:**
   - Conectar con GitHub Releases API
   - Comparar versión local vs remota
   - Parsear changelog de la nueva versión

2. **UI de Actualización:**
   - Notificación cuando hay actualización disponible
   - Diálogo con changelog
   - Botones: "Actualizar ahora", "Recordar después", "Omitir versión"
   - Barra de progreso durante descarga

3. **Proceso de Actualización:**
   - Descargar nueva versión
   - Backup de configuración actual
   - Reemplazar archivos
   - Reiniciar aplicación

4. **Registro en Windows:**
   - Guardar versión instalada en registro
   - Tracking de última comprobación
   - Configuración de auto-check

#### Criterios de aceptación:
- ✅ Detecta nuevas versiones en GitHub
- ✅ Muestra changelog de forma atractiva
- ✅ Actualización funciona sin perder configuración
- ✅ Manejo de errores robusto

---

### 4. 🔧 Creación de Nuevos Conjuntos BBPP
**Prioridad:** ALTA  
**Tiempo estimado:** 1.5 horas  
**Estado:** 🔴 PENDIENTE

#### Objetivo:
Permitir crear nuevos conjuntos de BBPP desde la UI, copiando reglas de conjuntos existentes.

#### Archivos a crear:
- `src/ui/bbpp_set_creator.py`

#### Archivos a modificar:
- `src/ui/rules_management_screen.py` (añadir botón)
- `src/rules_manager.py` (métodos de copia)

#### Funcionalidades:
1. **Diálogo de Creación:**
   - Campo: Nombre del conjunto
   - Campo: Descripción
   - Campo: Autor
   - Selector: Copiar desde conjunto existente
   - Checklist: Reglas a copiar
   - Botón: "Seleccionar todas"
   - Botón: "Crear conjunto vacío"

2. **Backend:**
   - Validar nombre único
   - Copiar reglas seleccionadas
   - Crear archivo JSON nuevo
   - Actualizar lista de conjuntos disponibles

3. **Integración:**
   - Botón "Nuevo Conjunto" en pantalla de gestión
   - Refresh automático de la lista
   - Conjunto nuevo aparece inmediatamente

#### Criterios de aceptación:
- ✅ Puede crear conjunto vacío
- ✅ Puede copiar reglas de conjunto existente
- ✅ Validación de nombre único
- ✅ Archivo JSON se crea correctamente
- ✅ Conjunto aparece en la lista inmediatamente

---

## 📊 PLAN DE EJECUCIÓN

### Orden Recomendado:

1. **Optimizar Instalador** (30 min)
   - Tarea rápida y crítica
   - Asegura que futuras releases usen main

2. **Creación de Nuevos Conjuntos** (1.5 h)
   - Funcionalidad muy solicitada
   - Relativamente independiente

3. **Configuración de IA** (2 h)
   - Base para futuras funcionalidades
   - Puede probarse inmediatamente

4. **Botón de Actualización** (2 h)
   - Requiere testing más exhaustivo
   - Depende de tener releases en main

**Tiempo total estimado:** ~6 horas

---

## 🎯 ENTREGABLES

Al finalizar el Sprint 1, tendremos:

1. ✅ Instalador optimizado que descarga desde `main`
2. ✅ Pantalla de configuración de IA funcional
3. ✅ Sistema de actualización automática
4. ✅ Capacidad de crear nuevos conjuntos BBPP

---

## 🧪 TESTING

### Tests a realizar:

1. **Instalador:**
   - Instalar desde cero
   - Verificar que descarga desde main
   - Comprobar que todos los archivos se instalan

2. **Configuración IA:**
   - Probar con API Key válida de OpenAI
   - Probar con API Key válida de Gemini
   - Probar con API Key inválida
   - Verificar encriptación

3. **Actualización:**
   - Simular nueva versión en GitHub
   - Probar actualización completa
   - Verificar que no se pierde configuración
   - Probar "Recordar después"

4. **Nuevos Conjuntos:**
   - Crear conjunto vacío
   - Crear conjunto copiando de UiPath
   - Crear conjunto copiando de NTTData
   - Verificar que se puede editar

---

## 📝 NOTAS

### Dependencias:
- Instalador requiere acceso a GitHub
- IA requiere API Keys (usuario debe proveerlas)
- Actualización requiere releases en GitHub

### Riesgos:
- API de GitHub puede tener rate limits
- Encriptación de API Keys puede ser compleja
- Actualización in-place puede fallar en algunos casos

### Mitigaciones:
- Implementar retry logic para GitHub API
- Usar biblioteca estándar para encriptación (cryptography)
- Siempre hacer backup antes de actualizar

---

## ✅ CHECKLIST DE INICIO

Antes de empezar, verificar:
- [ ] Git está en rama `develop`
- [ ] No hay cambios sin commitear
- [ ] Entorno virtual activado
- [ ] Dependencias instaladas
- [ ] Backup de la base de datos

---

**Creado:** 2025-12-07  
**Sprint:** 1  
**Estado:** 🚀 LISTO PARA COMENZAR

---

## 🎬 ¿POR DÓNDE EMPEZAMOS?

Recomiendo empezar por la **Tarea 1: Optimizar Instalador**, ya que es rápida y crítica.

¿Estás listo para comenzar?
