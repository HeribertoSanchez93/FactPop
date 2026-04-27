# `factpop/app/status_cli.py` — `factpop-cli status`

**Propósito:** Muestra un resumen completo del estado de la app en un solo comando.

```
FactPop -- Current Status
====================================

Topics        : 1 active / 2 total
  [*] Java
  [ ] Kafka

Schedule times: 1 configured
  09:00
  Random mode : ON  (08:00 - 22:00, max 3/day)

Quizzes       : enabled
Fact history  : 14 facts recorded
Review queue  : 2 pending
```

Este comando es útil para:
- Verificar el estado después de cada etapa del gate de aceptación
- Confirmar que la configuración persiste después de reiniciar
- Diagnóstico rápido antes de reportar un bug

**Diseño:** En vez de usar un sub-Typer (`add_typer`), la función `status_command` se registra directamente en el app principal con `app.command("status")(status_command)`. Esto evita el problema de subgrupos anidados (`status status`) que ocurre cuando se usa `add_typer`.

**Todos los tests** de `test_cli_status.py` usan el mismo patrón de los tests de CLI anteriores: `CliRunner` + `tmp_path` DB + verificaciones de output.
