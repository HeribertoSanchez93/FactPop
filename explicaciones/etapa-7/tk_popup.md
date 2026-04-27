# `factpop/features/notifications/tk_popup.py` — `TkPopupDispatcher`

**Sin tests automatizados — ver `tests/manual-qa.md` Stage 7.**

---

## Diseño de la ventana

```
┌─────────────────────────────────────────┐
│ [Java]                                  │  ← label topic (azul claro)
│                                         │
│ In Java, Optional is used to handle     │  ← texto del fact (wraplength 360px)
│ null values, preventing NPEs...         │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Optional<String> opt =              │ │  ← ejemplo (fondo más oscuro, Consolas)
│ │   Optional.of("value");             │ │
│ └─────────────────────────────────────┘ │
│ ─────────────────────────────────────── │  ← separador
│ [Show Another]  [Save]  [Close]         │  ← botones
└─────────────────────────────────────────┘
```

## Flujo de control con tkinter

```python
root = tk.Tk()
root.withdraw()          # oculta la ventana raíz invisible
popup = tk.Toplevel(root)
# ... configura la UI ...
root.mainloop()          # bloquea hasta que root.quit() sea llamado
root.destroy()           # limpieza

if show_another_requested[0]:
    on_show_another()    # genera nuevo fact y abre otra ventana
```

**¿Por qué `show_another_requested = [False]` en vez de una variable bool?**

Python no permite reasignar variables del scope externo desde una closure (sin `nonlocal`). Usar una lista de un elemento es un patrón alternativo: `show_another_requested[0] = True` modifica el contenido de la lista (mutable), no la variable.

## Threading model (Stage 9)

Para Stage 7 (CLI `--show`), se crea un `Tk()` nuevo por llamada. Esto es correcto para uso en línea de comandos.

En Stage 9 (scheduler daemon):
- pystray corre en el main thread
- El scheduler corre en un daemon thread
- Los popups se despachan al main thread via `root.after(0, callback)`
- `TkPopupDispatcher` necesitará un modo que reciba un root externo en vez de crear uno nuevo

Esto se resuelve en Stage 9 sin cambiar la interfaz del dispatcher.
