# `factpop/features/schedules/service.py`

**Propósito:** Contiene la lógica de negocio de los horarios: validación del formato HH:MM, gestión de la lista de horarios fijos, y configuración del modo aleatorio. Delega la persistencia a `SettingsService`.

---

```python
_TIME_RE = re.compile(r"^\d{2}:\d{2}$")
```
Expresión regular compilada una sola vez. `^\d{2}:\d{2}$` significa:
- `^` — inicio del string
- `\d{2}` — exactamente 2 dígitos
- `:` — dos puntos literales
- `\d{2}` — exactamente 2 dígitos
- `$` — fin del string

Acepta `"09:00"`, rechaza `"9:00"`, `"09:0"`, `"ab:cd"`, `"09-00"`.

---

```python
def _validate_time(time: str) -> None:
    if not _TIME_RE.match(time):
        raise InvalidTimeFormatError(
            f"'{time}' is not a valid time. Use HH:MM format (e.g., 09:00)."
        )
    hh, mm = int(time[:2]), int(time[3:])
    if hh > 23 or mm > 59:
        raise InvalidTimeFormatError(
            f"Invalid time '{time}': hours must be 00-23, minutes 00-59."
        )
```
**Dos niveles de validación:**
1. **Formato** — la regex verifica que sea `DD:DD` exactamente.
2. **Rango** — verifica que los números estén dentro de 00:00-23:59.

La función es privada al módulo (sin `self`) porque es utilidad pura sin estado.

---

```python
def add_time(self, time: str) -> None:
    _validate_time(time)
    times = self._settings.get_schedule_times()
    if time in times:
        raise TimeAlreadyExistsError(f"Time '{time}' is already in the schedule.")
    self._settings.set_schedule_times(times + [time])
```
1. Valida formato y rango.
2. Lee la lista actual.
3. Verifica duplicado.
4. Guarda la lista con el nuevo tiempo al final.

`times + [time]` crea una nueva lista — no muta la existente (Python: listas son mutables, pero aquí preferimos la inmutabilidad).

---

```python
def remove_time(self, time: str) -> None:
    times = self._settings.get_schedule_times()
    if time not in times:
        raise TimeNotFoundError(f"Time '{time}' not found in schedule.")
    self._settings.set_schedule_times([t for t in times if t != time])
```
List comprehension que filtra el tiempo a eliminar. Si no existe, lanza error antes de intentar modificar.

---

```python
def enable_random(self, start="08:00", end="22:00", max_per_day=3) -> None:
    _validate_time(start)
    _validate_time(end)
    self._settings.set_random_config(
        RandomModeConfig(enabled=True, start=start, end=end, max_per_day=max_per_day)
    )
```
Los parámetros tienen valores por defecto (spec: ventana 08:00-22:00, max 3). Valida ambos tiempos antes de guardar.

---

```python
def disable_random(self) -> None:
    current = self._settings.get_random_config()
    self._settings.set_random_config(
        RandomModeConfig(enabled=False, start=current.start, end=current.end, max_per_day=current.max_per_day)
    )
```
Lee la config actual, cambia solo `enabled=False`, y guarda. Así los demás valores (ventana, max) se **preservan** al desactivar — el usuario no tiene que reconfigurarlos al reactivar.
