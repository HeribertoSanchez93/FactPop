# `scripts/bootstrap_dev.ps1` y `scripts/run_tests.ps1`

---

## `scripts/bootstrap_dev.ps1` — Setup del entorno de desarrollo

Script de PowerShell que prepara el entorno completo para un desarrollador nuevo (o para reinstalar). Se ejecuta una sola vez.

```powershell
$ErrorActionPreference = "Stop"
```
Configura PowerShell para que **detenga el script ante el primer error**. Por defecto, PowerShell continúa ejecutando aunque un comando falle. Con esta línea, si algo sale mal (ej: Python no está instalado), el script para inmediatamente en vez de ejecutar pasos siguientes en un estado inválido.

---

```powershell
Write-Host "==> Verifying Python 3.13..."
$pyVersion = python --version 2>&1
if ($pyVersion -notmatch "3\.13") {
    Write-Error "Python 3.13 required. Found: $pyVersion. Install it from https://python.org"
    exit 1
}
Write-Host "    $pyVersion"
```
- `python --version 2>&1` — ejecuta `python --version` y captura tanto stdout como stderr en `$pyVersion` (en algunas versiones de Python, `--version` escribe en stderr).
- `-notmatch "3\.13"` — verifica que el output NO coincida con `3.13` (regex, el punto es literal por el `\`).
- Si la versión no es 3.13 → muestra error y sale con código 1.
- Si pasa la verificación → imprime la versión encontrada.

---

```powershell
Write-Host "==> Creating .venv..."
python -m venv .venv
```
Crea el entorno virtual Python en la carpeta `.venv`. Un venv es un Python aislado — las dependencias instaladas aquí no afectan al Python del sistema ni a otros proyectos.

---

```powershell
Write-Host "==> Activating .venv..."
& .\.venv\Scripts\Activate.ps1
```
- `&` — operador de llamada en PowerShell, necesario para ejecutar scripts.
- `Activate.ps1` — script que modifica el `PATH` del proceso actual para que `python` y `pip` apunten al venv.

Después de este punto, todos los comandos `python` y `pip` del script usan el venv.

---

```powershell
Write-Host "==> Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt
```
- `pip install --upgrade pip --quiet` — actualiza pip a la versión más reciente (pip viejo puede tener bugs o no soportar paquetes nuevos). `--quiet` suprime output innecesario.
- `pip install -r requirements.txt` — instala todas las dependencias del proyecto listadas en `requirements.txt`.

---

```powershell
if (-not (Test-Path ".env")) {
    Write-Host "==> Copying .env.example -> .env (fill in FACTPOP_API_KEY before running)..."
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "ACTION REQUIRED: Open .env and set your FACTPOP_API_KEY."
} else {
    Write-Host "==> .env already exists, skipping copy."
}
```
- `Test-Path ".env"` — devuelve `$true` si el archivo `.env` existe.
- `-not (...)` — lo niega: si `.env` NO existe, entrar al bloque.
- `Copy-Item ".env.example" ".env"` — copia la plantilla como punto de partida.
- El bloque `else` evita sobreescribir un `.env` ya configurado al correr el script por segunda vez.

---

```powershell
Write-Host ""
Write-Host "Setup complete!"
Write-Host "  Activate venv : .\.venv\Scripts\Activate.ps1"
Write-Host "  Run daemon     : python -m factpop"
Write-Host "  Run CLI        : python -m factpop.app.cli --help"
```
Instrucciones finales para que el usuario sepa qué hacer después del setup.

---

## `scripts/run_tests.ps1` — Ejecutar el suite de tests

```powershell
$ErrorActionPreference = "Stop"
```
Detiene el script ante cualquier error (igual que en el bootstrap).

```powershell
Write-Host "==> Running FactPop test suite..."
& .\.venv\Scripts\pytest -q --tb=short $args
```
- `& .\.venv\Scripts\pytest` — ejecuta pytest desde el venv (asegura que use las dependencias correctas).
- `-q` — modo silencioso (quiet): muestra solo los resultados, no el nombre de cada test.
- `--tb=short` — cuando un test falla, muestra un traceback corto (solo las líneas más relevantes) en vez de el traceback completo.
- `$args` — pasa cualquier argumento adicional que el usuario haya dado al script. Por ejemplo: `.\scripts\run_tests.ps1 tests/integration` ejecutaría solo los tests de integración.

**Uso:**
```powershell
# Todos los tests
.\scripts\run_tests.ps1

# Solo una carpeta
.\scripts\run_tests.ps1 tests/unit

# Solo un archivo
.\scripts\run_tests.ps1 tests/integration/test_tinydb_factory.py

# Con más detalle (verbose)
.\scripts\run_tests.ps1 -v
```
