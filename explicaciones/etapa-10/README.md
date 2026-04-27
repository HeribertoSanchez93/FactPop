# Etapa 10 — Integración: Settings Window + Auto-start + Docs

| Archivo | Explicación |
|---|---|
| `factpop/features/settings/tk_settings.py` | [tk_settings.md](tk_settings.md) |
| `factpop/app/auto_start.py` | [auto_start.md](auto_start.md) |
| `factpop/app/auto_start_cli.py` | [auto_start.md](auto_start.md) |
| `factpop/app/status_cli.py` | [status_cli.md](status_cli.md) |
| `README.md` | Instalación y uso — config file exception (no tests) |
| Tests (2 archivos, 17 tests nuevos) | [tests.md](tests.md) |

## Estructura agregada

```
factpop/
  features/settings/
    tk_settings.py     ← ventana tkinter con tabs Topics/Schedule/History
  app/
    auto_start.py      ← utilidad para instalar/remover startup script Windows
    auto_start_cli.py  ← factpop-cli autostart install/remove/status
    status_cli.py      ← factpop-cli status (resumen de configuración)

README.md              ← guía de instalación y uso
tests/manual-qa.md     ← checklist Stage 10 (settings window, auto-start, smoke)
```

## TDD: qué se testeo y qué no

### Testado automáticamente

| Componente | Tests |
|---|---|
| `auto_start.py` pura lógica | 9 tests: path en carpeta startup, VBS content, is_configured |
| `factpop-cli status` | 8 tests: topics count, schedule, quiz state, history count, review queue |

### Excepción TDD documentada (GUI / config files)

| Componente | Razón |
|---|---|
| `tk_settings.py` | tkinter requiere display server; testing tkinter rendering no es práctico |
| `README.md` | Es un archivo de documentación (config file exception) |
| Auto-start script VBS | Es un archivo de configuración/scripting del SO |

## CLI completo después de Etapa 10

```
factpop-cli
  status                      ← NUEVO: resumen de toda la configuración
  topics    add/list/activate/deactivate/delete
  schedules add/remove/list/random enable|disable
  quiz      toggle on|off / simulate [--date]
  llm       ping
  facts     generate [--topic] [--show]
  history   list [--topic] [--saved-only]
  reviews   list
  autostart install/remove/status    ← NUEVO
```

## Gate de aceptación

| Check | Método |
|---|---|
| `factpop-cli status` muestra todos los módulos | Automatizado |
| `autostart install/status/remove` funciona | Automatizado (lógica pura) |
| Settings window abre con 3 tabs | Manual QA |
| Cambios en settings persisten | Manual QA |
| Auto-start VBS en carpeta Startup | Manual QA |
| End-to-end smoke: 8 pasos | Manual QA (ver tests/manual-qa.md) |
| 359 tests totales | Automatizado |
