import os
import glob
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# Al estar ingest.py dentro de /src, debemos subir dos niveles para llegar a la raíz del proyecto (AgenteIALegal)
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)

# Rutas apuntando a la raíz del proyecto
DOCS_DIR = os.path.join(BASE_DIR, "data", "legislacion")
DB_DIR = os.path.join(BASE_DIR, "data", "chroma_db")


def cargar_documentos_por_jurisdiccion() -> List[Document]:
    """
    Recorre las subcarpetas de 'data/legislacion/' y procesa los PDFs,
    asignando una jurisdicción y subcategoría precisa según el archivo para evitar mezclas.
    """
    documentos: List[Document] = []

    if not os.path.exists(DOCS_DIR):
        print(f"⚠️ La carpeta no existe: {DOCS_DIR}")
        print(f"Comprueba que existe {DOCS_DIR}")
        return []

    print(f"🔍 Buscando legislación en: {DOCS_DIR}")

    # Iterar sobre cada subcarpeta (administrativo, civil, general, laboral, mercantil, penal)
    for carpeta in os.listdir(DOCS_DIR):
        ruta_subcarpeta = os.path.join(DOCS_DIR, carpeta)

        if not os.path.isdir(ruta_subcarpeta):
            continue

        jurisdiccion_base = carpeta.lower().strip()
        print(f"\n📂 Procesando área base: [{jurisdiccion_base.upper()}]")

        # Buscar ficheros PDF soportados
        archivos = glob.glob(os.path.join(ruta_subcarpeta, "*.pdf"))

        for ruta_archivo in archivos:
            nombre_fichero = os.path.basename(ruta_archivo)

            # Ignorar archivos ocultos o temporales
            if nombre_fichero.startswith("."):
                continue

            # Extraer la norma automáticamente del nombre del fichero
            nombre_norma = os.path.splitext(nombre_fichero)[0].lower()

            # --- REFINAMIENTO DE METADATOS POR NORMA ---
            # Evitamos que todo lo que esté en 'administrativo' comparta la misma etiqueta ciega
            jurisdiccion_efectiva = jurisdiccion_base
            if jurisdiccion_base == "administrativo":
                if any(k in nombre_norma for k in ["extranj", "visado", "residencia", "loe"]):
                    jurisdiccion_efectiva = "extranjeria"
                elif any(k in nombre_norma for k in ["proteccion", "datos", "rgpd", "lopd"]):
                    jurisdiccion_efectiva = "proteccion_datos"
                elif any(k in nombre_norma for k in ["39", "40", "procedimiento", "lrjap"]):
                    jurisdiccion_efectiva = "procedimiento_administrativo"

            try:
                loader = PyPDFLoader(ruta_archivo)
                paginas = loader.load()

                for p in paginas:
                    p.metadata["jurisdiccion"] = jurisdiccion_efectiva  # Jurisdicción refinada para filtros exactos
                    p.metadata["jurisdiccion_base"] = jurisdiccion_base  # Carpeta física original de respaldo
                    p.metadata["norma"] = nombre_norma
                    p.metadata["origen_fichero"] = nombre_fichero
                    p.metadata["source"] = ruta_archivo
                    documentos.append(p)

                print(f"  └─ PDF cargado ({len(paginas)} págs): {nombre_fichero} ➔ [jurisdicción: {jurisdiccion_efectiva}]")

            except Exception as e:
                print(f"  ❌ Error al procesar {nombre_fichero}: {e}")

    return documentos


def ejecutar_ingesta():
    print("🚀 Iniciando proceso de ingesta de legislación en ChromaDB...")

    # 1. Cargar documentos
    docs = cargar_documentos_por_jurisdiccion()
    if not docs:
        print("⚠️ No se encontraron documentos válidos para procesar.")
        return

    print(f"\n📄 Total de páginas/documentos base cargados: {len(docs)}")

    # 2. Fragmentación (Chunking optimizado para textos jurídicos del BOE)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1800,
        chunk_overlap=200,
        separators=[
            "\n\nArtículo ",
            "\nArtículo ",
            "CAPÍTULO ",
            "TÍTULO ",
            "\n\n",
            "\n",
            ". "
        ]
    )

    chunks = text_splitter.split_documents(docs)
    total_chunks = len(chunks)
    print(f"🧩 Total de fragmentos (chunks) generados: {total_chunks}")

    # 3. Vectorización por lotes seguros
    print("\n⚡ Conectando con 'nomic-embed-text' e insertando por lotes en ChromaDB...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    vectorstore = Chroma(
        collection_name="base_conocimiento_logos",
        embedding_function=embeddings,
        persist_directory=DB_DIR
    )

    # Lote de 50 para evitar saturar 
    batch_size = 50
    total_lotes = (total_chunks + batch_size - 1) // batch_size

    for i in range(0, total_chunks, batch_size):
        lote = chunks[i:i + batch_size]
        num_lote = (i // batch_size) + 1
        print(f"📦 Indexando lote {num_lote}/{total_lotes} ({len(lote)} chunks)...")

        try:
            vectorstore.add_documents(documents=lote)
        except Exception as e:
            print(f"❌ Error en lote {num_lote}: {e} - Reintentando...")
            vectorstore.add_documents(documents=lote)

    print(f"\n✅ ¡Ingesta completada con éxito! Base de datos persistida en: {DB_DIR}")


if __name__ == "__main__":
    ejecutar_ingesta()