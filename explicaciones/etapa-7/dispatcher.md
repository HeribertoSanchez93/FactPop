# `factpop/features/notifications/dispatcher.py`

```python
@runtime_checkable
class NotificationDispatcher(Protocol):
    def show_fact(
        self,
        record: FactRecord,
        on_save: Callable[[], None],
        on_show_another: Callable[[], None],
    ) -> None: ...
```

**Propósito:** Define el contrato de cualquier implementación que muestre un popup de fact. Misma idea que `LLMClient` en Stage 4 — un protocolo pequeño que permite intercambiar implementaciones sin cambiar el código llamador.

**Implementaciones:**
- `TkPopupDispatcher` — producción: abre ventana tkinter con botones
- `NullDispatcher` — tests: registra llamadas sin mostrar UI

**Callbacks:**
- `on_save` — el dispatcher llama esto cuando el usuario hace click en "Save"
- `on_show_another` — el dispatcher llama esto cuando el usuario hace click en "Show Another"
- Close/X — no tiene callback; el dispatcher simplemente cierra la ventana

**¿Por qué callbacks y no valores de retorno?**

Si `show_fact()` devolviera un enum `Action.SAVE | Action.SHOW_ANOTHER | Action.CLOSE`, el llamador tendría que manejar la lógica después. Con callbacks, el dispatcher controla cuándo llamarlos (dentro del event loop de tkinter), y el llamador define QUÉ hacer sin saber CUÁNDO.
