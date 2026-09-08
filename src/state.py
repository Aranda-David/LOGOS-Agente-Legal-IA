from typing import TypedDict, Annotated
import operator

class State(TypedDict):
    """
    Estructura de estado global para el flujo de trabajo del agente legal.
    """
    peticion_usuario: str
    tipo_tarea: str  # 'auditoria', 'redaccion', 'comparacion', 'general'
    historial_mensajes: Annotated[list, operator.add]
    respuesta_final: str