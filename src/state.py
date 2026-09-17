from typing import TypedDict, Optional, List

class State(TypedDict):
    peticion_usuario: str
    texto_documento: Optional[str]
    tipo_tarea: Optional[str]
    jurisdicciones: List[str]
    borrador_respuesta: Optional[str]
    respuesta_final: Optional[str]