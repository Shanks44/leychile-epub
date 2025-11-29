# Contribuir a LeyChile ePub Generator

¡Gracias por tu interés en contribuir a LeyChile ePub Generator! 🇨🇱

Este proyecto tiene como objetivo facilitar el acceso a la legislación chilena en formato digital portable. Toda contribución es bienvenida, desde correcciones de errores hasta nuevas funcionalidades.

## Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [¿Cómo puedo contribuir?](#cómo-puedo-contribuir)
  - [Reportar Bugs](#reportar-bugs)
  - [Sugerir Mejoras](#sugerir-mejoras)
  - [Tu Primera Contribución de Código](#tu-primera-contribución-de-código)
  - [Pull Requests](#pull-requests)
- [Guías de Estilo](#guías-de-estilo)
  - [Mensajes de Git Commit](#mensajes-de-git-commit)
  - [Estilo de Código Python](#estilo-de-código-python)
  - [Documentación](#documentación)
- [Configuración del Entorno de Desarrollo](#configuración-del-entorno-de-desarrollo)
- [Estructura del Proyecto](#estructura-del-proyecto)

## Código de Conducta

Este proyecto y todos sus participantes están gobernados por el [Código de Conducta](CODE_OF_CONDUCT.md). Al participar, se espera que respetes este código. Por favor, reporta comportamientos inaceptables a luis@aguilera.cl.

## ¿Cómo puedo contribuir?

### Reportar Bugs

Los bugs se rastrean como [GitHub Issues](https://github.com/laguileracl/leychile-epub/issues).

Antes de crear un reporte de bug, por favor verifica que:
- Estás usando la última versión del proyecto
- El bug no ha sido reportado previamente

Al crear un reporte de bug, incluye:
- **Título claro y descriptivo**
- **Pasos exactos para reproducir el problema**
- **Comportamiento esperado vs comportamiento actual**
- **Capturas de pantalla** si aplica
- **Tu entorno**: Sistema operativo, versión de Python, etc.

Usa esta plantilla:

```markdown
**Descripción del Bug**
Una descripción clara y concisa del bug.

**Para Reproducir**
Pasos para reproducir el comportamiento:
1. Ir a '...'
2. Ejecutar '...'
3. Ver error

**Comportamiento Esperado**
Qué esperabas que sucediera.

**Capturas de Pantalla**
Si aplica, agrega capturas de pantalla.

**Entorno:**
 - OS: [ej. macOS 14.0]
 - Python: [ej. 3.12.0]
 - Versión del proyecto: [ej. 1.0.0]

**Contexto Adicional**
Cualquier otro contexto sobre el problema.
```

### Sugerir Mejoras

Las sugerencias de mejora también se rastrean como [GitHub Issues](https://github.com/laguileracl/leychile-epub/issues).

Antes de sugerir una mejora:
- Verifica que no exista ya una sugerencia similar
- Considera si la mejora encaja con el alcance del proyecto

Al crear una sugerencia, incluye:
- **Título claro y descriptivo**
- **Descripción detallada de la mejora propuesta**
- **Explicación de por qué sería útil** para la mayoría de usuarios
- **Ejemplos de cómo funcionaría**

### Tu Primera Contribución de Código

¿No sabes por dónde empezar? Busca issues con las etiquetas:
- `good first issue` - Issues sencillos para principiantes
- `help wanted` - Issues donde se necesita ayuda extra
- `documentation` - Mejoras a la documentación

### Pull Requests

1. **Fork** el repositorio
2. **Crea una branch** desde `main`:
   ```bash
   git checkout -b feature/mi-nueva-funcionalidad
   ```
3. **Haz tus cambios** siguiendo las guías de estilo
4. **Escribe o actualiza tests** si corresponde
5. **Asegúrate** de que todos los tests pasen
6. **Commit** tus cambios con mensajes descriptivos
7. **Push** a tu fork
8. **Abre un Pull Request**

#### Proceso de Revisión

- Un maintainer revisará tu PR
- Pueden solicitar cambios o mejoras
- Una vez aprobado, se hará merge

## Guías de Estilo

### Mensajes de Git Commit

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(<alcance opcional>): <descripción>

[cuerpo opcional]

[pie opcional]
```

**Tipos:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Cambios de formato (no afectan código)
- `refactor`: Refactorización de código
- `test`: Agregar o modificar tests
- `chore`: Tareas de mantenimiento

**Ejemplos:**
```
feat(scraper): agregar soporte para decretos supremos
fix(epub): corregir encoding de caracteres especiales
docs: actualizar instrucciones de instalación
```

### Estilo de Código Python

Seguimos [PEP 8](https://peps.python.org/pep-0008/) con algunas adaptaciones:

- **Longitud máxima de línea**: 100 caracteres
- **Imports**: Agrupados (stdlib, third-party, local) y ordenados alfabéticamente
- **Docstrings**: Formato Google
- **Type Hints**: Requeridos para funciones públicas

Ejemplo:
```python
from typing import Optional

def obtener_ley(id_norma: int, incluir_historial: bool = False) -> Optional[dict]:
    """Obtiene los datos de una ley desde la BCN.
    
    Args:
        id_norma: Identificador único de la norma en BCN.
        incluir_historial: Si True, incluye versiones anteriores.
        
    Returns:
        Diccionario con los datos de la ley, o None si no se encuentra.
        
    Raises:
        BCNConnectionError: Si no se puede conectar a la BCN.
    """
    ...
```

**Herramientas recomendadas:**
- `black` para formateo automático
- `isort` para ordenar imports
- `flake8` o `ruff` para linting
- `mypy` para verificación de tipos

### Documentación

- Documenta todas las funciones y clases públicas
- Usa español para documentación orientada a usuarios
- Usa inglés para comentarios técnicos en código si lo prefieres
- Mantén el README actualizado

## Configuración del Entorno de Desarrollo

```bash
# Clonar el repositorio
git clone https://github.com/laguileracl/leychile-epub.git
cd leychile-epub

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar dependencias de desarrollo (cuando estén disponibles)
pip install -r requirements-dev.txt

# Ejecutar tests
pytest

# Verificar estilo de código
flake8 .
black --check .
mypy .
```

## Estructura del Proyecto

```
leychile-epub/
├── bcn_scraper.py      # Scraper para la API de BCN
├── epub_generator.py   # Generador de archivos ePub
├── cli.py              # Interfaz de línea de comandos
├── app.py              # Interfaz web (Streamlit)
├── main.py             # Punto de entrada principal
├── tests/              # Tests unitarios y de integración
├── docs/               # Documentación adicional
├── requirements.txt    # Dependencias de producción
├── requirements-dev.txt # Dependencias de desarrollo
└── pyproject.toml      # Configuración del proyecto
```

---

## ¿Preguntas?

Si tienes preguntas, no dudes en:
- Abrir un [Issue](https://github.com/laguileracl/leychile-epub/issues)
- Contactar al maintainer: luis@aguilera.cl

¡Gracias por contribuir! 🙌
