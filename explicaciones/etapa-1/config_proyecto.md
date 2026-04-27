# Archivos de configuración del proyecto

## `requirements.txt`

```
tinydb>=4.8.0
openai>=1.0.0
schedule>=1.2.0
pystray>=0.19.0
plyer>=2.1.0
Pillow>=10.0.0
typer>=0.12.0
pytest>=8.0.0
freezegun>=1.5.0
python-dotenv>=1.0.0
platformdirs>=4.0.0
filelock>=3.14.0
```

Lista de dependencias externas de la app. `pip install -r requirements.txt` las instala todas.

| Librería | Para qué se usa |
|---|---|
| `tinydb` | Base de datos NoSQL embebida (archivos JSON) |
| `openai` | Cliente para llamar a la API LLM compatible con OpenAI |
| `schedule` | Scheduler simple para disparar jobs a intervalos |
| `pystray` | Icono en el system tray (barra de tareas) |
| `plyer` | Notificaciones nativas del SO (toasts) |
| `Pillow` | Manejo de imágenes (requerido por pystray para el icono) |
| `typer` | Construir el CLI de administración con tipado y `--help` |
| `pytest` | Framework de tests |
| `freezegun` | Congela el tiempo en tests (para probar lógica de fechas) |
| `python-dotenv` | Carga variables de entorno desde el archivo `.env` |
| `platformdirs` | Resuelve rutas del SO (AppData, Logs, etc.) |
| `filelock` | Lock de instancia única basado en archivos |

`>=4.8.0` significa "versión 4.8.0 o superior". Evita instalar versiones antiguas con bugs, pero permite actualizaciones automáticas de patches.

---

## `.gitignore`

Indica a git qué archivos **nunca debe incluir** en commits.

```
# Secretos — NEVER commit .env
.env
.env.*
!.env.example
```
- `.env` — el archivo con la API key real. Nunca debe subir al repositorio.
- `.env.*` — cualquier variante (`.env.local`, `.env.production`, etc.) también ignorada.
- `!.env.example` — la excepción: `.env.example` **sí** se commitea porque es la plantilla sin datos reales.

```
__pycache__/
*.py[cod]
*.pyo
```
Archivos compilados de Python que Python genera automáticamente. Son específicos de cada máquina y no tienen sentido en el repositorio.

```
.venv/
venv/
env/
```
El entorno virtual con todas las dependencias instaladas. No se commitea porque cualquiera puede recrearlo con `pip install -r requirements.txt`.

```
.pytest_cache/
*.egg-info/
build/
dist/
```
Carpetas generadas por pytest y por el empaquetado de Python. Son derivadas del código, no fuente.

```
*.log
```
Archivos de log. Son locales a cada máquina y pueden ser grandes.

```
# VS Code — commit settings.json (interpreter path), ignore user-specific files
.vscode/*
!.vscode/settings.json
```
- `.vscode/*` — ignora todo dentro de `.vscode/`.
- `!.vscode/settings.json` — excepción: este archivo específico sí se commitea porque configura el intérprete de Python del proyecto (apunta a `.venv`).

---

## `.env.example`

```
# OpenAI-compatible LLM API
FACTPOP_API_KEY=sk-replace-me
FACTPOP_BASE_URL=https://api.openai.com/v1
FACTPOP_MODEL=gpt-4o-mini

# Optional
# FACTPOP_LLM_TIMEOUT_SECONDS=20
```

**Plantilla** del archivo `.env`. Se commitea al repo para que cualquier desarrollador sepa qué variables necesita configurar.

- `FACTPOP_API_KEY` — la API key de OpenAI (o compatible). El valor `sk-replace-me` es un placeholder — el usuario lo reemplaza con su key real en `.env`.
- `FACTPOP_BASE_URL` — endpoint de la API. Cambiando esto se puede usar Ollama, Azure OpenAI, o cualquier API compatible.
- `FACTPOP_MODEL` — nombre del modelo a usar (ej: `gpt-4o-mini`, `gpt-4`, `llama3`).
- `FACTPOP_LLM_TIMEOUT_SECONDS` — comentado porque es opcional.

**¿Cómo se usa?**
1. Copiar `.env.example` a `.env`
2. Editar `.env` con los valores reales
3. La app los lee con `load_dotenv()` al arrancar

---

## `pyrightconfig.json`

```json
{
  "venvPath": ".",
  "venv": ".venv",
  "pythonVersion": "3.13",
  "include": ["factpop", "tests"]
}
```

Configuración para Pyright (el analizador de tipos de VS Code/Pylance).

- `"venvPath": "."` — busca el venv en el directorio actual del proyecto.
- `"venv": ".venv"` — nombre de la carpeta del venv.
- `"pythonVersion": "3.13"` — dice a Pyright que analice el código asumiendo Python 3.13 (para que no marque como error funciones o tipos que solo existen en esa versión).
- `"include": [...]` — carpetas a analizar. Sin esto, Pyright podría ignorar el código de la app.

**Sin este archivo:** VS Code muestra warnings falsos como "Cannot find module pytest" porque no sabe dónde están instaladas las dependencias.

---

## `.vscode/settings.json`

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
  "python.analysis.extraPaths": ["${workspaceFolder}"],
  "python.testing.pytestEnabled": true,
  "python.testing.pytestPath": "${workspaceFolder}/.venv/Scripts/pytest.exe",
  "python.testing.pytestArgs": ["tests"]
}
```

Configuración de VS Code específica del proyecto (no del usuario):

- `"python.defaultInterpreterPath"` — le dice a VS Code qué Python usar. Sin esto, usa el Python del sistema y no encuentra las dependencias del proyecto.
- `"python.analysis.extraPaths"` — agrega la raíz del proyecto al path de análisis para que las importaciones `from factpop.xxx import yyy` se resuelvan correctamente.
- `"python.testing.pytestEnabled": true` — habilita pytest como framework de tests en el panel de Testing de VS Code.
- `"python.testing.pytestPath"` — ruta exacta al ejecutable de pytest dentro del venv.
- `"python.testing.pytestArgs": ["tests"]` — carpeta donde VS Code busca los tests.
