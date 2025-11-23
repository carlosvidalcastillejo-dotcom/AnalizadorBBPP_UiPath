# Estrategia de Ramas Git - AnalizadorBBPP_UiPath

## Estructura de Ramas

Este proyecto utiliza una estrategia **Git Flow simplificada** con las siguientes ramas:

### Ramas Principales

#### 🟢 `main`
- **Propósito**: Código estable y versiones de producción
- **Protección**: Solo se actualiza mediante Pull Requests desde `develop`
- **Commits**: Solo merges de versiones estables
- **Tags**: Cada merge a `main` debe tener un tag de versión (ej: `v1.0.0`)

#### 🔵 `develop`
- **Propósito**: Rama de desarrollo activo
- **Uso**: Aquí trabajamos día a día
- **Integración**: Se integran todas las features antes de pasar a `main`
- **Estado**: Debe ser siempre funcional, pero puede tener features en progreso

### Ramas Temporales

#### 🟡 `feature/*`
- **Propósito**: Desarrollo de nuevas funcionalidades
- **Nomenclatura**: `feature/nombre-descriptivo`
- **Ejemplos**:
  - `feature/nueva-regla-bbpp`
  - `feature/exportar-pdf`
  - `feature/metricas-dashboard`
- **Ciclo de vida**:
  1. Crear desde `develop`
  2. Desarrollar la funcionalidad
  3. Merge a `develop` mediante Pull Request
  4. Eliminar la rama feature

#### 🔴 `hotfix/*`
- **Propósito**: Correcciones urgentes en producción
- **Nomenclatura**: `hotfix/descripcion-bug`
- **Ciclo de vida**:
  1. Crear desde `main`
  2. Corregir el bug
  3. Merge a `main` Y `develop`
  4. Tag de versión en `main`
  5. Eliminar la rama hotfix

---

## Flujo de Trabajo Diario

### 1. Trabajar en `develop`

```bash
# Asegurarse de estar en develop
git checkout develop

# Actualizar desde GitHub
git pull origin develop

# Hacer cambios...
# Añadir archivos modificados
git add .

# Commit con mensaje descriptivo
git commit -m "Descripción clara del cambio"

# Subir a GitHub
git push origin develop
```

### 2. Crear una Nueva Feature

```bash
# Desde develop, crear rama feature
git checkout develop
git pull origin develop
git checkout -b feature/nombre-funcionalidad

# Desarrollar la funcionalidad...
git add .
git commit -m "Implementar [funcionalidad]"

# Subir a GitHub
git push -u origin feature/nombre-funcionalidad

# Crear Pull Request en GitHub desde feature/* hacia develop
# Revisar y aprobar
# Merge en GitHub
# Eliminar rama feature
```

### 3. Publicar una Nueva Versión

```bash
# Desde develop, asegurarse de que todo está listo
git checkout develop
git pull origin develop

# Crear Pull Request en GitHub desde develop hacia main
# Revisar cambios
# Merge en GitHub

# Actualizar main localmente
git checkout main
git pull origin main

# Crear tag de versión
git tag -a v1.0.0 -m "Versión 1.0.0 - Descripción de la release"
git push origin v1.0.0

# Volver a develop
git checkout develop
```

### 4. Hotfix Urgente

```bash
# Crear hotfix desde main
git checkout main
git pull origin main
git checkout -b hotfix/corregir-bug-critico

# Corregir el bug...
git add .
git commit -m "Fix: Corregir [bug crítico]"

# Subir a GitHub
git push -u origin hotfix/corregir-bug-critico

# Crear PR hacia main
# Merge en GitHub

# IMPORTANTE: También hacer merge a develop
git checkout develop
git pull origin develop
git merge hotfix/corregir-bug-critico
git push origin develop

# Crear tag de versión patch
git checkout main
git pull origin main
git tag -a v1.0.1 -m "Hotfix: [descripción]"
git push origin v1.0.1

# Eliminar rama hotfix
git branch -d hotfix/corregir-bug-critico
git push origin --delete hotfix/corregir-bug-critico
```

---

## Convenciones de Commits

Usar **Conventional Commits** para mensajes claros:

```
<tipo>: <descripción corta>

[cuerpo opcional con más detalles]

[footer opcional con referencias]
```

### Tipos de Commit:

- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de bug
- `docs:` - Cambios en documentación
- `style:` - Formato, espacios, etc. (sin cambio de código)
- `refactor:` - Refactorización de código
- `test:` - Añadir o modificar tests
- `chore:` - Tareas de mantenimiento, builds, etc.

### Ejemplos:

```bash
git commit -m "feat: Añadir validación de prefijos de variables"
git commit -m "fix: Corregir cálculo de porcentaje en métricas"
git commit -m "docs: Actualizar README con instrucciones de instalación"
git commit -m "refactor: Extraer lógica de análisis a módulo separado"
```

---

## Estado Actual

✅ **Rama actual**: `develop`  
✅ **Ramas disponibles**:
- `main` - Producción
- `develop` - Desarrollo activo

### Verificar Estado

```bash
# Ver todas las ramas
git branch -a

# Ver rama actual
git branch --show-current

# Ver estado
git status
```

---

## Comandos Útiles

```bash
# Cambiar de rama
git checkout nombre-rama

# Crear y cambiar a nueva rama
git checkout -b nueva-rama

# Ver diferencias entre ramas
git diff develop..main

# Ver historial gráfico
git log --oneline --graph --all -10

# Eliminar rama local
git branch -d nombre-rama

# Eliminar rama remota
git push origin --delete nombre-rama

# Ver ramas remotas
git branch -r

# Actualizar referencias remotas
git fetch --prune
```

---

## Protección de Ramas (Recomendado)

En GitHub, configurar protección para `main`:

1. Ir a **Settings → Branches**
2. Añadir regla para `main`:
   - ✅ Require pull request before merging
   - ✅ Require status checks to pass
   - ✅ Include administrators

---

## Resumen Rápido

| Rama | Propósito | Se actualiza desde | Se mergea a |
|------|-----------|-------------------|-------------|
| `main` | Producción estable | `develop` o `hotfix/*` | - |
| `develop` | Desarrollo activo | `feature/*` | `main` |
| `feature/*` | Nueva funcionalidad | `develop` | `develop` |
| `hotfix/*` | Corrección urgente | `main` | `main` y `develop` |

**Regla de oro**: Siempre trabajar en `develop` o en ramas `feature/*`, nunca directamente en `main`.
