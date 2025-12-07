# 📋 TAREAS PENDIENTES - Analizador BBPP UiPath

## Fecha: 2025-12-06
## Versión Actual: 0.1.1-beta
## Autor: Carlos Vidal Castillejo

---

## 🎯 TAREAS PRIORITARIAS (Próximas Sesiones)

### 1. 🔄 **Sistema de Actualización Automática** (ALTA PRIORIDAD)

#### 1.1 Optimización del Instalador
- [ ] **Instalador siempre descarga desde rama `main/master`**
  - Actualmente puede descargar de develop
  - Modificar script de instalador para apuntar a main
  - Validar que main esté actualizado antes de release
  
- [ ] **Optimizar tamaño del instalador**
  - Reducir dependencias innecesarias
  - Comprimir assets
  - Usar PyInstaller con opciones optimizadas
  
- [ ] **Mejorar UX del instalador**
  - Barra de progreso más detallada
  - Mensajes de estado claros
  - Opción de instalación personalizada vs rápida

#### 1.2 Botón de Actualización en la Aplicación
- [ ] **Detección de nuevas versiones**
  - Conectar con GitHub Releases API
  - Comparar versión local vs versión en GitHub
  - Notificación visual cuando hay actualización disponible
  
- [ ] **Actualización in-place (sin reinstalar)**
  - Descargar nueva versión en background
  - Reemplazar archivos sin perder configuración
  - Usar registro de Windows para tracking de versión
  - Backup automático antes de actualizar
  
- [ ] **Changelog visual**
  - Mostrar novedades de la nueva versión
  - Diálogo atractivo con lista de cambios
  - Opción de "Actualizar ahora" o "Recordar después"

**Archivos a modificar:**
- `installer/installer_script.iss` (InnoSetup)
- `src/updater.py` (NUEVO)
- `src/ui/main_window.py` (añadir botón/menú)
- `build.py` (optimizaciones)

---

### 2. 🤖 **Integración con IA** (ALTA PRIORIDAD)

#### 2.1 Configuración de API
- [ ] **Pantalla de configuración de IA**
  - Selector de proveedor (OpenAI, Gemini, Claude, Local)
  - Campo para API Key (encriptado)
  - Test de conexión
  - Configuración de modelo a usar
  
- [ ] **Soporte para múltiples proveedores**
  - OpenAI (GPT-4, GPT-3.5)
  - Google Gemini (Gemini Pro, Gemini Flash)
  - Anthropic Claude
  - Modelos locales (Ollama, LM Studio)
  
- [ ] **Gestión segura de credenciales**
  - Encriptación de API Keys
  - Almacenamiento en keyring del sistema
  - No guardar en texto plano

#### 2.2 Funcionalidades con IA
- [ ] **Análisis contextual de hallazgos**
  - IA revisa cada hallazgo y determina si es falso positivo
  - Explicación detallada del problema
  - Sugerencias de corrección
  
- [ ] **Generación de código corregido**
  - IA genera snippet de código arreglado
  - Explicación didáctica de la buena práctica
  - Comparación antes/después
  
- [ ] **Asistente de refactorización**
  - Sugerencias de mejora más allá de las reglas
  - Detección de patrones anti-pattern
  - Recomendaciones de arquitectura
  
- [ ] **Generación de documentación**
  - IA genera documentación del proyecto
  - Descripción de workflows
  - Diagramas de flujo automáticos

**Archivos a crear/modificar:**
- `src/ai/ai_manager.py` (NUEVO)
- `src/ai/providers/` (NUEVO - carpeta con proveedores)
- `src/ui/ai_config_screen.py` (NUEVO)
- `src/analyzer.py` (integrar IA en análisis)

---

### 3. 📊 **Más Reglas BBPP** (MEDIA PRIORIDAD)

#### 3.1 Nuevas Categorías de Reglas
- [ ] **Seguridad**
  - Detección de credenciales hardcodeadas
  - Uso de SecureString
  - Validación de inputs
  - Sanitización de datos
  
- [ ] **Performance**
  - Uso excesivo de Delays
  - Bucles ineficientes
  - Lectura repetida de archivos
  - Queries SQL no optimizadas
  
- [ ] **Mantenibilidad**
  - Complejidad ciclomática alta
  - Duplicación de código
  - Workflows muy largos
  - Falta de modularización
  
- [ ] **Accesibilidad**
  - Uso de selectores dinámicos
  - Manejo de diferentes resoluciones
  - Soporte multi-idioma

#### 3.2 Reglas Específicas de UiPath
- [ ] **REFramework**
  - Validar estructura correcta
  - Verificar estados obligatorios
  - Comprobar manejo de excepciones
  
- [ ] **Orchestrator**
  - Uso correcto de Queues
  - Assets vs Config
  - Logging a Orchestrator
  
- [ ] **Document Understanding**
  - Validación de pipelines
  - Uso de ML Skills
  - Manejo de confianza

**Archivos a modificar:**
- `config/bbpp/BBPP_UiPath.json`
- `config/bbpp/BBPP_NTTData.json`
- `src/analyzer.py` (nuevas validaciones)

---

### 4. ✅ **Comprobación de Versión de UiPath** (MEDIA PRIORIDAD)

- [ ] **Validar versión mínima requerida**
  - Leer versión de Studio desde project.json
  - Comparar con versión mínima configurada
  - Warning si versión es muy antigua
  
- [ ] **Compatibilidad de actividades**
  - Detectar actividades deprecadas
  - Sugerir alternativas modernas
  - Avisar de breaking changes
  
- [ ] **Recomendaciones de actualización**
  - Sugerir actualizar a versión LTS
  - Listar beneficios de actualizar
  - Detectar incompatibilidades

**Archivos a modificar:**
- `src/project_scanner.py` (ya extrae versión)
- `src/analyzer.py` (añadir validaciones)
- `config/version_requirements.json` (NUEVO)

---

### 5. 🎨 **Personalización de Pantalla y Reportes** (MEDIA PRIORIDAD)

#### 5.1 Temas de Color
- [ ] **Selector de tema**
  - Tema claro / oscuro
  - Temas predefinidos (UiPath, NTT Data, Personalizado)
  - Preview en tiempo real
  
- [ ] **Colores personalizables**
  - Color primario
  - Color secundario
  - Color de acentos
  - Colores de severidad

#### 5.2 Personalización de Reportes
- [ ] **Plantillas de reportes**
  - Múltiples plantillas HTML
  - Selector de estilo
  - Logo en reportes
  
- [ ] **Secciones configurables**
  - Elegir qué secciones incluir
  - Orden de secciones
  - Nivel de detalle
  
- [ ] **Exportación personalizada**
  - Formato de fecha configurable
  - Idioma de reportes
  - Unidades de medida

**Archivos a crear/modificar:**
- `src/ui/theme_manager.py` (NUEVO)
- `src/report_generator.py` (plantillas)
- `config/themes/` (NUEVO - carpeta con temas)

---

### 6. 🔧 **Creación de Nuevos Conjuntos BBPP** (ALTA PRIORIDAD)

- [ ] **Botón "Nuevo Conjunto"**
  - Diálogo para crear conjunto
  - Nombre del conjunto
  - Descripción
  - Autor
  
- [ ] **Copiar reglas de conjunto existente**
  - Selector de conjunto origen
  - Checkboxes para elegir reglas a copiar
  - Opción "Copiar todas"
  
- [ ] **Editor de conjunto**
  - Añadir/quitar reglas
  - Modificar parámetros
  - Activar/desactivar reglas
  
- [ ] **Exportar/Importar conjuntos**
  - Exportar a JSON
  - Importar desde JSON
  - Compartir con otros usuarios

**Archivos a crear/modificar:**
- `src/ui/bbpp_set_creator.py` (NUEVO)
- `src/rules_manager.py` (métodos de copia)
- `src/ui/rules_management_screen.py` (botón nuevo)

---

## 📋 TAREAS DEL ROADMAP EXISTENTE

### 7. 📚 **Documentación Completa** (PENDIENTE)

- [ ] **Manual de usuario (PDF)**
  - Introducción y características
  - Guía de instalación
  - Tutorial de primer uso
  - Configuración avanzada
  - Creación de reglas personalizadas
  - FAQ y troubleshooting
  
- [ ] **Documentación técnica**
  - Arquitectura del proyecto
  - Estructura JSON de BBPP
  - Guía para desarrolladores
  - Diagramas de flujo
  - API documentation

---

### 8. 🐛 **Testing y Calidad** (PENDIENTE)

- [ ] **Testing exhaustivo**
  - Proyectos reales de diferentes tamaños
  - Validar performance con proyectos >50 XAML
  - Edge cases y errores
  
- [ ] **Gestión de errores robusta**
  - Try-catch en todas las operaciones críticas
  - Logs de error detallados
  - Mensajes de error user-friendly
  
- [ ] **Validación de edge cases**
  - Proyectos sin project.json
  - XAML malformados
  - Rutas con caracteres especiales
  - Proyectos muy grandes

---

### 9. 📦 **Instalador Final** (PARCIAL)

- [x] Compilar con PyInstaller ✅
- [ ] Reducir tamaño del ejecutable
- [ ] Incluir todos los assets
- [ ] Firmar ejecutable digitalmente
- [x] Crear instalador con InnoSetup ✅
- [ ] Testing Windows 10/11

---

### 10. 🚀 **Release en GitHub** (PARCIAL)

- [x] Repositorio creado ✅
- [ ] README.md profesional
- [ ] Screenshots de la aplicación
- [ ] Características destacadas
- [ ] Instrucciones de instalación
- [ ] Licencia apropiada
- [ ] Release v1.0.0 con assets

---

### 11. 💬 **Sistema de Feedback** (PENDIENTE)

- [ ] Botón "Reportar problema"
- [ ] Formulario que genere issue en GitHub
- [ ] Logs de errores guardados
- [ ] Telemetría básica (opcional)

---

### 12. 📊 **Comparador de Versiones** (FUTURO)

- [ ] Comparar análisis actual vs anterior
- [ ] Visualizar mejora/empeoramiento del score
- [ ] Gráfico de tendencia temporal
- [ ] Delta de hallazgos

---

### 13. 📄 **Exportación a PDF** (FUTURO)

- [ ] Reporte ejecutivo en PDF
- [ ] Resumen de score y gráficos principales
- [ ] Formato profesional para managers

---

### 14. 🎨 **Editor Visual de Reglas** (FUTURO)

- [ ] Crear nuevas reglas sin programar
- [ ] Interfaz drag-and-drop
- [ ] Guardado automático en JSON

---

### 15. 🔗 **Integración Orchestrator** (FUTURO)

- [ ] Robot UiPath que ejecuta análisis
- [ ] Publicación de resultados en Orchestrator
- [ ] Alertas automáticas

---

## 🎯 PRIORIZACIÓN SUGERIDA

### Sprint 1 (Próxima Sesión) - CRÍTICO
1. ✅ **Actualización de colores de severidad** (COMPLETADO)
2. ✅ **Dashboard de Métricas mejorado** (COMPLETADO)
3. 🔄 **Optimizar instalador** (descarga desde main)
4. 🤖 **Configuración básica de IA** (pantalla + API)

### Sprint 2 - ALTA PRIORIDAD
1. 🔄 **Botón de actualización automática**
2. 🔧 **Creación de nuevos conjuntos BBPP**
3. ✅ **Validación de versión de UiPath**
4. 📊 **Añadir 5-10 reglas BBPP nuevas**

### Sprint 3 - MEDIA PRIORIDAD
1. 🤖 **Funcionalidades de IA** (análisis contextual)
2. 🎨 **Personalización de temas**
3. 📚 **Documentación de usuario**
4. 🐛 **Testing exhaustivo**

### Sprint 4 - BAJA PRIORIDAD
1. 📊 **Comparador de versiones**
2. 📄 **Exportación a PDF**
3. 💬 **Sistema de feedback**
4. 🚀 **Release v1.0 en GitHub**

---

## 📝 NOTAS ADICIONALES

### Tareas Identificadas del Historial

1. **Sistema de Excepciones** ✅ (COMPLETADO)
   - Ya implementado para variables REFramework
   - Funcional y probado

2. **Gráficos en Reportes HTML** ✅ (COMPLETADO)
   - Chart.js integrado
   - Gráficos interactivos funcionando

3. **Gestión de Conjuntos BBPP** ✅ (COMPLETADO)
   - UI para activar/desactivar conjuntos
   - Persistencia de configuración

4. **Branding Personalizable** ✅ (COMPLETADO)
   - Logo, nombre empresa, colores
   - Totalmente funcional

5. **Sidebar Estable** ✅ (COMPLETADO)
   - Ya no desaparece
   - Funciona correctamente

### Posibles Mejoras Adicionales

- [ ] **Análisis incremental**
  - Solo analizar archivos modificados
  - Cache de resultados anteriores
  
- [ ] **Análisis paralelo**
  - Usar multiprocessing
  - Acelerar análisis de proyectos grandes
  
- [ ] **Integración con Git**
  - Detectar cambios en commits
  - Análisis automático en pre-commit
  
- [ ] **Dashboard web**
  - Versión web del dashboard
  - Compartir resultados online
  
- [ ] **API REST**
  - Exponer funcionalidad vía API
  - Integración con CI/CD

---

## 🎯 CONCLUSIÓN

**Total de tareas pendientes:** ~60+

**Prioridad ALTA:** 8 tareas  
**Prioridad MEDIA:** 12 tareas  
**Prioridad BAJA:** 15 tareas  
**Futuro (v2.0+):** 25+ tareas

**Próxima sesión recomendada:**
1. Optimizar instalador (descarga desde main)
2. Configuración básica de IA
3. Botón de actualización automática
4. Creación de nuevos conjuntos BBPP

---

**Última actualización:** 2025-12-06  
**Versión del documento:** 1.0  
**Estado:** 📋 Documento de planificación activo
