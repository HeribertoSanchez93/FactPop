# Etapa 3 — Schedule Configuration

| Archivo | Explicación |
|---|---|
| `factpop/features/schedules/errors.py` | [errors.md](errors.md) |
| `factpop/features/schedules/models.py` | [models.md](models.md) |
| `factpop/features/schedules/service.py` | [schedule_service.md](schedule_service.md) |
| `factpop/features/schedules/cli.py` | [cli.md](cli.md) |
| `factpop/features/settings/repository.py` | [settings_repository.md](settings_repository.md) |
| `factpop/features/settings/service.py` | [settings_service.md](settings_service.md) |
| `factpop/features/settings/cli.py` | [cli.md](cli.md) |
| Tests (4 archivos, 56 tests nuevos) | [tests.md](tests.md) |

## Estructura agregada

```
factpop/
  features/
    schedules/
      errors.py    ← InvalidTimeFormatError, TimeAlreadyExistsError, TimeNotFoundError
      models.py    ← RandomModeConfig dataclass
      service.py   ← ScheduleService (validación HH:MM + lógica de horarios)
      cli.py       ← schedules add/remove/list/random enable/disable
    settings/
      repository.py ← TinyDBSettingsRepository (key-value genérico)
      service.py    ← SettingsService (acceso tipado a app_config)
      cli.py        ← quiz toggle on/off

tests/
  integration/
    test_settings_repository.py  ← 9 tests
  unit/features/
    test_settings_service.py     ← 9 tests
    test_schedule_service.py     ← 22 tests
    test_schedule_cli.py         ← 16 tests
```

## Relación entre módulos

```
ScheduleService  →  SettingsService  →  TinyDBSettingsRepository  →  TinyDB(app_config)
     CLI         →  ScheduleService
  settings CLI   →  SettingsService
```

- `ScheduleService` nunca toca TinyDB directamente — delega a `SettingsService`.
- `SettingsService` es el único punto de acceso a `app_config`.
- Toda la validación (HH:MM, duplicados, etc.) vive en `ScheduleService`, no en settings.

## Gate de aceptación (todos pasan)

| Check | Resultado |
|---|---|
| `schedules add 09:00` | `OK: Time '09:00' added to schedule.` |
| `schedules add 25:00` | `Error: Invalid time '25:00'...` + exit 1 |
| `schedules add 09:00` (duplicado) | `Error: Time '09:00' is already...` + exit 1 |
| `schedules list` | muestra tiempo + estado random |
| `schedules random enable --start 08:00 --end 22:00 --max 4` | `OK: Random mode enabled...` |
| `quiz toggle off` | `OK: Quizzes disabled.` |
| `quiz toggle on` | `OK: Quizzes enabled.` |
| 124 tests pytest | todos pasan |
