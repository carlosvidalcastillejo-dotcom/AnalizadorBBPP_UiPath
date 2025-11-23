# 🔒 Guía de Control de Versiones - Analizador BBPP UiPath

## ✅ Git Configurado Exitosamente

**Repositorio inicializado**: `c:\Users\Imrik\Documents\analizador_bbpp_Antigravity\analizador_bbpp_v0.2.6_COMPLETO`

**Configuración**:
- Usuario: Carlos Vidal Castillejo
- Email: carlos.vidal@nttdata.com
- Commit inicial: v0.10.4 Release (62 archivos, 16,407 líneas)

## 📋 Comandos Esenciales para Usar

### Antes de Hacer Cambios Importantes

```powershell
# Ver estado actual
git status

# Ver cambios no guardados
git diff

# Crear un punto de guardado (commit)
git add .
git commit -m "Descripción clara del cambio"
```

### Si Algo Sale Mal

```powershell
# Ver historial de commits
git log --oneline

# Volver al último commit (DESCARTAR cambios actuales)
git reset --hard HEAD

# Volver a un commit específico
git reset --hard <commit-hash>

# Ver diferencias con el último commit
git diff HEAD
```

### Crear Ramas para Experimentos

```powershell
# Crear rama nueva para probar algo
git checkout -b feature/nueva-funcionalidad

# Volver a la rama principal
git checkout master

# Ver todas las ramas
git branch -a
```

## 🎯 Flujo de Trabajo Recomendado

### 1. Antes de Compilar una Nueva Versión

```powershell
# Asegurarse de que todo está guardado
git add .
git commit -m "Pre-compilación v0.X.X - Cambios preparados"
```

### 2. Después de Compilar Exitosamente

```powershell
# Guardar la versión compilada
git add .
git commit -m "v0.X.X Release - Compilación exitosa"
git tag v0.X.X
```

### 3. Si Encuentras un Error

```powershell
# Opción 1: Volver al último commit bueno
git reset --hard HEAD~1

# Opción 2: Volver a una versión específica (tag)
git reset --hard v0.10.4
```

## 🚨 Situaciones de Emergencia

### "¡Se rompió todo!"

```powershell
# Volver al commit inicial (v0.10.4)
git reset --hard 0753f7c

# O volver al último commit
git reset --hard HEAD
```

### "Quiero ver qué cambió"

```powershell
# Ver cambios en un archivo específico
git diff src/ui/main_window.py

# Ver cambios entre commits
git diff HEAD~1 HEAD
```

### "Quiero recuperar un archivo específico"

```powershell
# Recuperar archivo del último commit
git checkout HEAD -- src/ui/main_window.py

# Recuperar archivo de un commit específico
git checkout <commit-hash> -- src/ui/main_window.py
```

## 📊 Estrategia de Commits

### Commits Frecuentes

**Hacer commit después de**:
- ✅ Cada compilación exitosa
- ✅ Cada fix importante
- ✅ Antes de cambios grandes
- ✅ Al final del día de trabajo

### Mensajes de Commit Claros

**Buenos ejemplos**:
```
✅ "v0.10.4 - Fix zona horaria en métricas"
✅ "Añadir filtro de proyectos en dashboard"
✅ "Corregir SyntaxError en main_window.py línea 1141"
```

**Malos ejemplos**:
```
❌ "fix"
❌ "cambios"
❌ "wip"
```

## 🔄 Workflow Diario Recomendado

### Al Empezar el Día

```powershell
# Ver estado
git status

# Ver último commit
git log -1
```

### Durante el Trabajo

```powershell
# Cada hora o después de cambios importantes
git add .
git commit -m "Descripción del cambio"
```

### Al Terminar el Día

```powershell
# Guardar todo el trabajo
git add .
git commit -m "EOD - Trabajo del día guardado"

# Ver resumen del día
git log --oneline --since="1 day ago"
```

## 🎓 Comandos Útiles Adicionales

### Ver Historial Visual

```powershell
# Historial completo
git log --graph --oneline --all

# Últimos 10 commits
git log --oneline -10
```

### Comparar Versiones

```powershell
# Ver qué cambió entre dos versiones
git diff v0.10.3 v0.10.4

# Ver archivos modificados
git diff --name-only HEAD~1 HEAD
```

### Crear Backup Manual

```powershell
# Crear tag de backup
git tag backup-$(Get-Date -Format "yyyyMMdd-HHmm")

# Ver todos los tags
git tag -l
```

## ⚠️ Reglas de Oro

1. **NUNCA** borres la carpeta `.git`
2. **SIEMPRE** haz commit antes de cambios grandes
3. **SIEMPRE** haz commit después de compilaciones exitosas
4. **NUNCA** hagas `git reset --hard` sin estar seguro
5. **SIEMPRE** verifica con `git status` antes de hacer reset

## 🆘 Contactos de Emergencia

Si algo sale muy mal y no sabes cómo recuperarlo:
1. **NO TOQUES NADA**
2. Copia toda la carpeta a un lugar seguro
3. Pide ayuda antes de hacer más cambios

## 📌 Estado Actual

**Versión Actual**: v0.10.4 Release
**Commit**: 0753f7c
**Fecha**: 2025-11-23 18:32
**Estado**: ✅ Sistema completamente funcional
**Archivos**: 62 archivos versionados
**Líneas**: 16,407 líneas de código

---

**¡Git está configurado y listo para proteger tu código!** 🛡️
