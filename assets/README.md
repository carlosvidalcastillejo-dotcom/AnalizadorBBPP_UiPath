# Assets del Analizador BBPP

Esta carpeta contiene recursos estáticos utilizados por la aplicación.

## Estructura

```
assets/
├── branding/          # Logos y branding personalizados (ignorado en git)
│   └── company_logo.* # Logo de la empresa (PNG/JPG)
└── README.md          # Este archivo
```

## Carpeta `branding/`

Esta carpeta **NO está versionada** en git (está en `.gitignore`) ya que cada instalación de la aplicación tendrá su propio branding personalizado.

### Funcionamiento

Cuando el usuario selecciona un logo personalizado desde la interfaz:

1. La aplicación copia el archivo seleccionado a `assets/branding/`
2. Lo renombra como `company_logo.{extension}` (mantiene la extensión original)
3. Guarda la ruta interna en la configuración del branding

### Ventajas

- ✅ El logo queda **embebido** en la aplicación
- ✅ **No se pierde** si el archivo original se mueve o elimina
- ✅ **Portable**: al copiar la carpeta del proyecto, el logo va incluido
- ✅ **Actualizable**: seleccionar un nuevo logo sobrescribe el anterior

### Restaurar Logo

Para eliminar el logo personalizado y volver al logo por defecto:
- Ir a "Configuración" → "Logo Personalizado" → Botón "Restaurar Logo"
- O eliminar manualmente el archivo de esta carpeta

## Notas

- Los archivos en `assets/branding/` son específicos de cada instalación
- Al clonar el repositorio, esta carpeta estará vacía (como es esperado)
- Formatos soportados: PNG, JPG, JPEG, GIF
