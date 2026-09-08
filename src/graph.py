from langgraph.graph import StateGraph, START, END
from langchain_core.prompts import ChatPromptTemplate
from src.state import State
from src.config import llm

# --- PROMPTS ESPECIALIZADOS CON CITAS LEGISLATIVAS RIGUROSAS ---

PROMPT_CLASIFICADOR = ChatPromptTemplate.from_messages([
    (
        "system",
        "Analiza la petición del usuario y responde ÚNICAMENTE con una de estas palabras: "
        "'auditoria', 'redaccion', 'comparacion' o 'general'."
    ),
    ("user", "{peticion}")
])

PROMPT_AUDITORIA = ChatPromptTemplate.from_messages([
    (
        "system",
        "Eres LOGOS, un experto auditor jurídico en legislación española.\n"
        "Tu tarea es auditar la consulta o texto proporcionado e identificar riesgos, vacíos y cláusulas abusivas.\n\n"
        "REQUISITO OBLIGATORIO DE RIGOR:\n"
        "Debes fundamentar jurídicamente tu análisis citando expresamente los Códigos, Leyes y Artículos exactos "
        "aplicables (ej. 'Art. 1124 del Código Civil', 'Art. 3 del Estatuto de los Trabajadores', 'Art. 82 del Real Decreto Legislativo 1/2007', etc.).\n"
        "Estructura tu respuesta en 3 bloques:\n"
        "1. 📌 **Análisis de Riesgos y Nulidades**\n"
        "2. ⚖️ **Fundamentación Legal y Artículos Aplicables** (Cita exacta de leyes)\n"
        "3. 💡 **Recomendaciones de Corrección**"
    ),
    ("user", "{peticion}")
])

PROMPT_REDACCION = ChatPromptTemplate.from_messages([
    (
        "system",
        "Eres LOGOS, abogado especialista en redacción jurídica en derecho español.\n"
        "Redacta el documento, cláusula o escrito solicitado utilizando lenguaje técnico impecable.\n\n"
        "REQUISITO OBLIGATORIO DE RIGOR:\n"
        "Incluye una nota jurídica al pie o sección previa indicando los artículos y leyes de referencia "
        "en los que se fundamenta la validez de la cláusula o documento redactado."
    ),
    ("user", "{peticion}")
])

PROMPT_GENERAL = ChatPromptTemplate.from_messages([
    (
        "system",
        "Eres LOGOS, un abogado consultor y asistente jurídico experto en legislación española.\n"
        "Atiende la consulta del usuario con absoluto rigor técnico.\n\n"
        "REQUISITO OBLIGATORIO DE RIGOR:\n"
        "Cada afirmación legal que realices DEBE ir acompañada de la cita exacta de la ley, real decreto o artículo correspondiente "
        "del ordenamiento jurídico español."
    ),
    ("user", "{peticion}")
])


# --- NODOS DEL GRAFO ---

def nodo_clasificador(state: State) -> dict:
    cadena = PROMPT_CLASIFICADOR | llm
    res = cadena.invoke({"peticion": state["peticion_usuario"]}).content.strip().lower()

    categoria = "general"
    for opcion in ["auditoria", "redaccion", "comparacion"]:
        if opcion in res:
            categoria = opcion
            break

    print(f"-> LOGOS clasificó la tarea como: [{categoria.upper()}]")
    return {"tipo_tarea": categoria}


def nodo_auditoria(state: State) -> dict:
    res = (PROMPT_AUDITORIA | llm).invoke({"peticion": state["peticion_usuario"]})
    return {"respuesta_final": res.content}


def nodo_redaccion(state: State) -> dict:
    res = (PROMPT_REDACCION | llm).invoke({"peticion": state["peticion_usuario"]})
    return {"respuesta_final": res.content}


def nodo_general(state: State) -> dict:
    res = (PROMPT_GENERAL | llm).invoke({"peticion": state["peticion_usuario"]})
    return {"respuesta_final": res.content}


def enrutador(state: State) -> str:
    tarea = state.get("tipo_tarea", "general")
    if tarea == "auditoria":
        return "nodo_auditoria"
    elif tarea == "redaccion":
        return "nodo_redaccion"
    else:
        return "nodo_general"


# --- CONSTRUCCIÓN DEL GRAFO ---

builder = StateGraph(State)

builder.add_node("clasificar", nodo_clasificador)
builder.add_node("nodo_auditoria", nodo_auditoria)
builder.add_node("nodo_redaccion", nodo_redaccion)
builder.add_node("nodo_general", nodo_general)

builder.add_edge(START, "clasificar")

builder.add_conditional_edges(
    "clasificar",
    enrutador,
    {
        "nodo_auditoria": "nodo_auditoria",
        "nodo_redaccion": "nodo_redaccion",
        "nodo_general": "nodo_general"
    }
)

builder.add_edge("nodo_auditoria", END)
builder.add_edge("nodo_redaccion", END)
builder.add_edge("nodo_general", END)

app_grafo = builder.compile()