from langgraph.graph import StateGraph, START, END
from src.state import State
from src.config import llm
from src.rag import buscar_contexto_legal
from src.prompts import (
    PROMPT_CLASIFICADOR,
    PROMPT_AUDITORIA,
    PROMPT_REDACCION,
    PROMPT_GENERAL,
    PROMPT_VERIFICADOR,
    PROMPT_CONVERSACIONAL
)


# --- NODOS DEL GRAFO ---

def nodo_clasificador(state: State) -> dict:
    """Clasifica la tarea, detecta si es charla coloquial y extrae las jurisdicciones implicadas de forma precisa."""
    peticion = state["peticion_usuario"].lower()
    doc = state.get("texto_documento")

    # 0. Detección amplia de charla coloquial, filosófica, saludos y debates
    if any(k in peticion for k in [
        "entre tú y yo", "juicio", "verdad absoluta", "qué opinas", "filosofía", "opinión", "ajedrez",
        "qué tal", "cómo llevas", "café", "código", "día", "hola", "estás", "quién eres", "buenas"
    ]):
        categoria = "conversacional"
    # 1. Detección de la Tarea técnica
    elif doc or any(k in peticion for k in ["audita", "revisa este escrito", "analiza el siguiente contrato"]):
        categoria = "auditoria"
    elif any(k in peticion for k in ["redacta", "elabora un modelo", "escribe una demanda", "recurso", "burofax"]):
        categoria = "redaccion"
    else:
        categoria = "general"

    # 2. Detección múltiple y refinada de Jurisdicciones (Aislamiento de Extranjería y RGPD)
    jurisdicciones_detectadas = []

    if any(k in peticion for k in ["penal", "delito", "prisión", "pena", "lecrim", "hurto", "estafa"]):
        jurisdicciones_detectadas.append("penal")
    if any(k in peticion for k in
           ["civil", "contrato", "matrimonio", "divorcio", "herencia", "curatela", "prescripción",
            "acciones personales", "obligación", "arrendamiento", "desahucio", "lau"]):
        jurisdicciones_detectadas.append("civil")
    if any(k in peticion for k in ["laboral", "despido", "trabajador", "salario", "ere", "estatuto"]):
        jurisdicciones_detectadas.append("laboral")
    if any(k in peticion for k in ["mercantil", "sociedad", "administrador", "concurso"]):
        jurisdicciones_detectadas.append("mercantil")

    # Subcategorías administrativas estrictamente separadas para evitar contaminación cruzada en el RAG
    if any(k in peticion for k in
           ["extranjería", "visado", "residencia", "arraigo", "estancia", "tarjeta de identidad de extranjero"]):
        jurisdicciones_detectadas.append("extranjeria")
    if any(k in peticion for k in ["protección de datos", "rgpd", "lopd", "aepd", "privacidad"]):
        jurisdicciones_detectadas.append("proteccion_datos")
    if any(k in peticion for k in
           ["multa", "ayuntamiento", "contencioso", "ley 39/2015", "procedimiento administrativo", "lrjap"]):
        jurisdicciones_detectadas.append("procedimiento_administrativo")

    # Si ninguna de las específicas coincide pero menciona genéricamente lo administrativo
    if not jurisdicciones_detectadas and any(k in peticion for k in ["administrativo", "administración pública"]):
        jurisdicciones_detectadas.append("administrativo")

    # Si no detecta ninguna o es general/conversacional
    if not jurisdicciones_detectadas:
        jurisdicciones_detectadas = ["general"]

    print(f"\n[CLASIFICADOR] Tarea -> '{categoria}' | Jurisdicciones detectadas -> {jurisdicciones_detectadas}")

    return {
        "tipo_tarea": categoria,
        "jurisdicciones": jurisdicciones_detectadas
    }


def nodo_conversacional(state: State) -> dict:
    """Nodo libre de RAG para debates, reflexiones y charlas coloquiales."""
    peticion = state["peticion_usuario"]
    print(f"\n☕ [CONVERSACIONAL] Abriendo debate sin restricciones RAG...")

    res = (PROMPT_CONVERSACIONAL | llm).invoke({
        "peticion": peticion
    })

    return {
        "contexto_rag": "No requerido (Modo conversacional/debate)",
        "respuesta_final": res.content
    }


def nodo_auditoria(state: State) -> dict:
    """Nodo especializado en revisar y auditar escritos jurídicos del usuario."""
    peticion = state["peticion_usuario"]
    doc = state.get("texto_documento") or "No se ha proporcionado un archivo adjunto."

    print(f"\n🕵️ [AUDITORIA] Estado bruto recibido: {state}")
    jurisdicciones = state.get("jurisdicciones", ["general"])
    print(f"📂 [AUDITORIA] Jurisdicciones extraídas del state: {jurisdicciones}")

    contexto_rag = buscar_contexto_legal(peticion, jurisdiccion_filtro=jurisdicciones)

    res = (PROMPT_AUDITORIA | llm).invoke({
        "peticion": peticion,
        "documento": doc,
        "contexto_rag": contexto_rag if contexto_rag else "Sin contexto RAG disponible."
    })

    return {
        "contexto_rag": contexto_rag,
        "borrador_respuesta": res.content
    }


def nodo_redaccion(state: State) -> dict:
    """Nodo especializado en redactar contratos, demandas, recursos y escritos procesales."""
    peticion = state["peticion_usuario"]
    doc = state.get("texto_documento") or "No se ha proporcionado un archivo adjunto."

    print(f"\n🕵️ [REDACCION] Estado bruto recibido: {state}")
    jurisdicciones = state.get("jurisdicciones", ["general"])
    print(f"📂 [REDACCION] Jurisdicciones extraídas del state: {jurisdicciones}")

    contexto_rag = buscar_contexto_legal(peticion, jurisdiccion_filtro=jurisdicciones)

    res = (PROMPT_REDACCION | llm).invoke({
        "peticion": peticion,
        "documento": doc,
        "contexto_rag": contexto_rag if contexto_rag else "Sin contexto RAG disponible."
    })

    return {
        "contexto_rag": contexto_rag,
        "borrador_respuesta": res.content
    }


def nodo_general(state: State) -> dict:
    """Nodo para consultas teóricas estrictas de artículos y códigos."""
    peticion = state["peticion_usuario"]

    print(f"\n🕵️ [GENERAL] Estado bruto recibido: {state}")
    jurisdicciones = state.get("jurisdicciones", ["general"])
    print(f"📂 [GENERAL] Jurisdicciones extraídas del state: {jurisdicciones}")

    contexto_rag = buscar_contexto_legal(peticion, jurisdiccion_filtro=jurisdicciones)

    res = (PROMPT_GENERAL | llm).invoke({
        "peticion": peticion,
        "contexto_rag": contexto_rag if contexto_rag else "Sin contexto RAG disponible."
    })

    return {
        "contexto_rag": contexto_rag,
        "borrador_respuesta": res.content
    }


def enrutador(state: State) -> str:
    """Determina hacia qué nodo especializado derivar la consulta."""
    tarea = state.get("tipo_tarea", "general")
    if tarea == "conversacional":
        return "nodo_conversacional"
    elif tarea == "auditoria":
        return "nodo_auditoria"
    elif tarea == "redaccion":
        return "nodo_redaccion"
    else:
        return "nodo_general"


def nodo_verificador(state: State) -> dict:
    """Nodo crítico de control: pule el borrador, elimina alucinaciones y aplica filtros de estilo."""
    peticion = state["peticion_usuario"]
    contexto_rag = state.get("contexto_rag", "Sin contexto RAG disponible.")
    borrador = state.get("borrador_respuesta", "")

    print("\n[VERIFICADOR] Analizando borrador en busca de alucinaciones normativas...")

    res = (PROMPT_VERIFICADOR | llm).invoke({
        "peticion": peticion,
        "contexto_rag": contexto_rag,
        "borrador": borrador
    })

    texto_final = res.content

    # --- FILTRO PROGRAMÁTICO DE SEGURIDAD EXTRAJUDICIAL ---
    # Si la petición es de un burofax o requerimiento y el modelo ha metido la palabra prohibida "suplico", la saneamos.
    if any(k in peticion.lower() for k in ["burofax", "requerimiento", "notificación"]):
        if "suplico" in texto_final.lower():
            print(
                "⚠️ [VERIFICADOR] Detectada palabra 'suplico' en documento extrajudicial. Aplicando purga programática...")
            # Reemplazamos encabezados de suplico judicial por requerimiento imperativo
            texto_final = texto_final.replace("### Suplico", "### Requerimiento")
            texto_final = texto_final.replace("## Suplico", "## Requerimiento")
            texto_final = texto_final.replace("Suplico", "Por todo lo expuesto, requiero")
            texto_final = texto_final.replace("suplico", "requiero")

    return {
        "respuesta_final": texto_final
    }


# --- CONSTRUCCIÓN DEL GRAFO ---

builder = StateGraph(State)

builder.add_node("clasificar", nodo_clasificador)
builder.add_node("nodo_conversacional", nodo_conversacional)
builder.add_node("nodo_auditoria", nodo_auditoria)
builder.add_node("nodo_redaccion", nodo_redaccion)
builder.add_node("nodo_general", nodo_general)
builder.add_node("verificar", nodo_verificador)

builder.add_edge(START, "clasificar")

builder.add_conditional_edges(
    "clasificar",
    enrutador,
    {
        "nodo_conversacional": "nodo_conversacional",
        "nodo_auditoria": "nodo_auditoria",
        "nodo_redaccion": "nodo_redaccion",
        "nodo_general": "nodo_general"
    }
)

# Las rutas técnicas pasan por el filtro del verificador; la conversacional va directa al END
builder.add_edge("nodo_conversacional", END)
builder.add_edge("nodo_auditoria", "verificar")
builder.add_edge("nodo_redaccion", "verificar")
builder.add_edge("nodo_general", "verificar")

builder.add_edge("verificar", END)

app_grafo = builder.compile()