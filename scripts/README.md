# Scripts de Desarrollo

Esta carpeta contiene scripts de utilidad y herramientas de desarrollo.

## Scripts Disponibles

- **add_reframework_exceptions.py**: Añade excepciones REFramework al sistema
- **alternative_chart_method.py**: Método alternativo para generación de gráficos
- **fix_*.py**: Scripts de corrección rápida de bugs específicos
- **generate_*.py**: Generadores de código/UI/reportes
- **update_*.py**: Scripts de actualización de configuración/datos
- **verify_*.py**: Scripts de verificación y validación

## Uso

Estos scripts son herramientas de desarrollo one-off creadas para tareas específicas durante la evolución del proyecto.

**Importante**:
- No son parte del flujo de trabajo normal del usuario final
- Pueden estar desactualizados o no funcionar con la versión actual
- Se mantienen por referencia histórica y posible reutilización

## sync_bbpp_sets.py

Script especial que sincroniza reglas desde el archivo Master a los conjuntos individuales (BBPP_UiPath.json, BBPP_NTTData.json, etc.).

### Uso:
```bash
python sync_bbpp_sets.py
```

Esto actualiza todos los conjuntos BBPP con las reglas del Master.
