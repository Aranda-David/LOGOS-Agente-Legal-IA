import os
from typing import Optional, List, Union
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from sentence_transformers import CrossEncoder

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "data", "chroma_db")

# --- INSTANCIAS EN CACHÉ (Singletons) ---
_vector_store: Optional[Chroma] = None
_reranker_model: Optional[CrossEncoder] = None


def _obtener_vector_store() -> Optional[Chroma]:
    """Carga ChromaDB una sola vez en memoria optimizando recursos."""
    global _vector_store

    if _vector_store is not None:
        return _vector_store

    if not os.path.exists(DB_DIR):
        print(f"⚠️ [RAG] La ruta de base de datos no existe: {DB_DIR}")
        return None

    print("⚡ [RAG] Conectando a ChromaDB nativo...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    _vector_store = Chroma(
        collection_name="base_conocimiento_logos",
        embedding_function=embeddings,
        persist_directory=DB_DIR
    )
    return _vector_store


def _obtener_reranker() -> CrossEncoder:
    """Carga el modelo Cross-Encoder una sola vez en memoria para el reranking."""
    global _reranker_model
    if _reranker_model is None:
        print("⚡ [RAG] Cargando modelo Cross-Encoder (Reranker) de precisión...")
        _reranker_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker_model


def reordenar_con_rerank(peticion: str, documentos: List[Document], top_n: int = 6) -> List[Document]:
    """Reordena los documentos recuperados utilizando un Cross-Encoder para máxima precisión."""
    if not documentos:
        return []

    model = _obtener_reranker()
    pares = [[peticion, doc.page_content] for doc in documentos]
    scores = model.predict(pares)

    docs_con_score = sorted(zip(documentos, scores), key=lambda x: x[1], reverse=True)
    print(
        f"🎯 [Rerank] Filtrados y reordenados los {len(documentos)} fragmentos iniciales. Quedan los {min(top_n, len(documentos))} mejores.")

    return [doc for doc, score in docs_con_score[:top_n]]


def buscar_contexto_legal(peticion: str, jurisdiccion_filtro: Union[str, list, dict, None] = None, k: int = 14) -> str:
    """
    Busca fragmentos normativos aplicando un enfoque Híbrido Universal (Ensemble: Vectorial + BM25)
    refinado con un Cross-Encoder Reranker para garantizar coincidencia conceptual y exacta de plazos.
    """
    store = _obtener_vector_store()
    if not store:
        return "⚠️ [RAG] Base de datos vectorial no disponible o vacía."

    # --- NORMALIZACIÓN ROBUSTA DEL FILTRO ---
    jurisdicciones = []

    if isinstance(jurisdiccion_filtro, dict):
        jurisdicciones = jurisdiccion_filtro.get("jurisdicciones",
                                                 jurisdiccion_filtro.get("jurisdicciones_detectadas", ["general"]))
    elif isinstance(jurisdiccion_filtro, list):
        jurisdicciones = jurisdiccion_filtro
    elif isinstance(jurisdiccion_filtro, str):
        jurisdicciones = [jurisdiccion_filtro]
    else:
        jurisdicciones = ["general"]

    jurisdicciones_limpias = [j.lower().strip() for j in jurisdicciones if j]
    if not jurisdicciones_limpias:
        jurisdicciones_limpias = ["general"]

    if len(jurisdicciones_limpias) > 1:
        filtro = {"jurisdiccion": {"$in": jurisdicciones_limpias}}
    else:
        filtro = {"jurisdiccion": jurisdicciones_limpias[0]}

    print(f"🔍 [RAG Hybrid Filter] Aplicando filtro a ChromaDB: {filtro}")

    resultados: List[Document] = []
    try:
        # 1. Recuperador Vectorial (Semántico)
        vector_retriever = store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k, "filter": filtro}
        )

        # 2. Carga del corpus filtrado para construir el índice léxico BM25 en tiempo de ejecución
        raw_data = store.get(where=filtro) if filtro else store.get()
        documentos_filtrados = [
            Document(page_content=text, metadata=meta)
            for text, meta in zip(raw_data.get("documents", []), raw_data.get("metadatas", []))
        ]

        if documentos_filtrados:
            # 3. Recuperador Léxico por Coincidencia Exacta de Términos (BM25)
            bm25_retriever = BM25Retriever.from_documents(documentos_filtrados)
            bm25_retriever.k = k

            # 4. Fusión de ambos mundos (Ensemble: 60% semántico, 40% léxico exacto)
            ensemble_retriever = EnsembleRetriever(
                retrievers=[vector_retriever, bm25_retriever],
                weights=[0.6, 0.4]
            )
            resultados = ensemble_retriever.invoke(peticion)
        else:
            resultados = store.similarity_search(peticion, k=k, filter=filtro)

    except Exception as e:
        print(f"⚠️ [RAG] Error en búsqueda híbrida ({e}), recurriendo a vectorial pura...")
        try:
            if filtro:
                resultados = store.similarity_search(peticion, k=k, filter=filtro)
            else:
                resultados = store.similarity_search(peticion, k=k)
        except Exception as ex:
            print(f"❌ [RAG] Error crítico en búsqueda vectorial: {ex}")

    # Fallback global si no hay resultados
    if not resultados and filtro is not None:
        print("🔄 [RAG] Resultados vacíos con filtro, ejecutando búsqueda global de respaldo...")
        try:
            resultados = store.similarity_search(peticion, k=max(6, k // 2))
        except Exception:
            pass

    if not resultados:
        return "⚠️ [RAG] No se han encontrado fragmentos normativos relevantes en la base de conocimiento para esta consulta."

    # --- 5. APLICAR RERANKING POR CROSS-ENCODER ---
    resultados_optimizados = reordenar_con_rerank(peticion, resultados, top_n=6)

    # Formateo estructurado del contexto para los nodos del grafo
    contexto_partes = []
    for doc in resultados_optimizados:
        jurisdiccion_doc = doc.metadata.get('jurisdiccion', 'general').upper()
        origen = doc.metadata.get('origen_fichero', 'desconocido')
        contenido = doc.page_content.strip()
        contexto_partes.append(f"--- FRAGMENTO [{jurisdiccion_doc} - {origen}] ---\n{contenido}")

    return "\n\n".join(contexto_partes)