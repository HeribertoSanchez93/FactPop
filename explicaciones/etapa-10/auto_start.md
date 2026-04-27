# `factpop/app/auto_start.py` y `auto_start_cli.py`

## `auto_start.py` — lógica pura (testada)

### `_startup_folder()` → Path

Devuelve `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup` — la carpeta donde Windows ejecuta scripts al iniciar sesión. Patcheable en tests con `unittest.mock.patch`.

### `get_startup_script_path()` → Path

Combina `_startup_folder()` con `"FactPop.vbs"`. El nombre `FactPop` se usará como identificador único — si el usuario instala FactPop en múltiples directorios, el script del último `install` gana.

### `build_startup_script_content(python_exe, project_dir)` → str

Genera un VBScript que lanza FactPop sin ventana de consola:

```vbscript
Set WShell = CreateObject("WScript.Shell")
WShell.CurrentDirectory = "C:\Users\PC\Desktop\SDD\FactPop"
WShell.Run """C:\...\pythonw.exe"" -m factpop", 0, False
Set WShell = Nothing
```

- `pythonw.exe` en vez de `python.exe` → sin ventana de consola negra al arrancar
- `0` como segundo arg → `WindowStyle = 0` (oculto)
- `False` → no esperar a que termine (fire and forget)
- `CurrentDirectory` → necesario para que `load_dotenv()` encuentre `.env`

### `install_auto_start()` → Path

Detecta el ejecutable Python del venv (`sys.executable`), deduce `pythonw.exe`, detecta `project_dir` como el directorio dos niveles arriba de `auto_start.py`, construye el VBS, lo escribe en la carpeta Startup.

### `remove_auto_start()` → bool

Elimina el VBS si existe. `True` = existía y se borró.

---

## `auto_start_cli.py` — CLI commands

```
factpop-cli autostart
  install   ← escribe FactPop.vbs en %APPDATA%\...\Startup\
  remove    ← borra el VBS
  status    ← muestra si está configurado
```

No tienen tests adicionales — su lógica es trivial (llama a `auto_start.py` y hace echo). La lógica real está en `auto_start.py` que sí está testeada.
