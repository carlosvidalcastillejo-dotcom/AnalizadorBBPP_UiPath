# 🚀 Analizador de Buenas Prácticas para UiPath (BBPP)
## Documento de Presentación Técnica

---

### 📄 Introducción

El **Analizador de Buenas Prácticas para UiPath** es una solución de software de escritorio diseñada para **automatizar, estandarizar y elevar la calidad** de los desarrollos RPA en UiPath. 

Esta herramienta permite a los desarrolladores y arquitectos de RPA realizar auditorías de código estáticas de manera inmediata y local, asegurando el cumplimiento de los estándares de la industria y las normativas internas de la organización antes de que el código llegue a producción.

---

### 🎯 Objetivos de la Herramienta

*   **Estandarización:** Garantizar que todos los desarrollos sigan las mismas reglas de nomenclatura, estructura y diseño.
*   **Calidad de Código:** Detectar tempranamente deuda técnica, código muerto, y malas prácticas que afectan el mantenimiento.
*   **Eficiencia:** Reducir drásticamente el tiempo dedicado a Code Reviews manuales.
*   **Mejora Continua:** Monitorear la evolución de la calidad de los proyectos mediante métricas históricas.

---

### ✨ Características Principales

#### 1. 🔍 Motor de Análisis Potente
*   **17 Reglas Implementadas:** Cubriendo Nomenclatura, Estructura, Modularización, Código Limpio y Rendimiento.
*   **Análisis Estático:** Parsea archivos `.xaml` y `project.json` sin necesidad de ejecutar el código, garantizando velocidad y seguridad.
*   **Scoring Inteligente:** Sistema de puntuación ponderada (0-100%) que califica la "salud" del proyecto.
*   **Gestión de Excepciones:** Compatible nativamente con **REFramework**, permitiendo excluir variables estándar (ej. `Config`, `TransactionItem`) para evitar falsos positivos.

#### 2. 🛡️ Flexibilidad y Configuración
*   **Multi-Set de Reglas:** Soporte para múltiples conjuntos de normativas (ej. *UiPath Oficial*, *NTT Data*, *Custom Interno*) activables según el cliente o proyecto.
*   **Personalización Total:**
    *   Todas las reglas son parametrizables vía JSON.
    *   Sistema de penalización ajustable (Por severidad, individual porcentual o global).
*   **Validación de Dependencias:** Verificación automática de versiones de paquetes NuGet requeridos por cada estándar.

#### 3. 📊 Visualización y Reportes
*   **Dashboard de Métricas:** Interfaz integrada con historial de análisis, permitiendo ver la evolución de un proyecto en el tiempo.
*   **Reportes HTML Interactivos:**
    *   Gráficos dinámicos (Chart.js) para distribución de severidad y categorías.
    *   Navegación fluida por hallazgos.
    *   Score visual tipo "Gauge".
*   **Exportación Excel:** Reportes detallados para auditoría formal.

#### 4. 🎨 Branding Corporativo
*   Personalización completa de la interfaz y reportes con el logo y colores de la empresa, ideal para consultoras que entregan auditorías a clientes finales.

#### 5. 🤖 Integración con IA (Roadmap)
*   Integración en desarrollo con modelos LLM (Google Gemini) para sugerencias de refactorización automática y explicación contextual de errores.

---

### 🏗️ Arquitectura Técnica

*   **Lenguaje:** Python 3.8+
*   **Interfaz Gráfica:** CustomTkinter (Moderna, modo oscuro/claro).
*   **Persistencia:** SQLite para métricas históricas y JSON para configuraciones.
*   **Distribución:** Ejecutable standalone (`.exe`) compilado, no requiere instalación de Python en la máquina del usuario.
*   **Privacidad:** Todo el análisis se realiza **localmente**. El código nunca sale del entorno del usuario (excepto en funciones opcionales de IA bajo demanda).

---

### 🚀 Flujo de Trabajo Típico

1.  **Selección:** El especialista selecciona la carpeta del proyecto UiPath.
2.  **Configuración:** Elige el conjunto de reglas a aplicar (ej. "Estándar Corporativo").
3.  **Análisis:** La herramienta escanea cientos de archivos en segundos.
4.  **Revisión:**
    *   Visualización inmediata de Score y Semáforo (Verde/Amarillo/Rojo).
    *   Navegación por hallazgos críticos en la UI.
5.  **Reporte:** Generación automática de entregable HTML/Excel para el equipo de desarrollo.

---

### 📞 Información de Contacto y Soporte

**Desarrollador Principal:** Carlos Vidal Castillejo  
**Estado del Proyecto:** Activo / Fase de Integración de IA
**Repositorio / Documentación:** Consultar `README.md` y carpeta `docs/` para guías de instalación y uso detalladas.

---
*Generado automáticamente para presentación técnica interna.*
