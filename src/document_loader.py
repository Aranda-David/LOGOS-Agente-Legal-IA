import io
from typing import Optional
from pypdf import PdfReader
from docx import Document


def cargar_texto_desde_archivo(uploaded_file) -> Optional[str]:
    """
    Recibe un objeto de archivo subido mediante Streamlit (BytesIO)
    y extrae el texto según el formato (.pdf, .docx, .txt).
    """
    if uploaded_file is None:
        return None

    nombre_archivo = uploaded_file.name.lower()
    texto_extraido = ""

    try:
        # 1. Procesar archivos PDF -- Necesitamos la libreria requerida, ver requirements.txt
        if nombre_archivo.endswith(".pdf"):
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                texto_pagina = page.extract_text()
                if texto_pagina:
                    texto_extraido += texto_pagina + "\n"

        # 2. Procesar archivos Word (.docx) -- Necesitamos la libreria requerida, ver requirements.txt
        elif nombre_archivo.endswith(".docx"):
            doc_bytes = io.BytesIO(uploaded_file.read())
            doc = Document(doc_bytes)
            for paragrafo in doc.paragraphs:
                if paragrafo.text:
                    texto_extraido += paragrafo.text + "\n"

        # 3. Procesar archivos de texto plano (.txt)
        elif nombre_archivo.endswith(".txt"):
            texto_extraido = uploaded_file.read().decode("utf-8", errors="ignore")

        else:
            print(f"Formato no soportado: {nombre_archivo}")
            return None

        return texto_extraido.strip()

    except Exception as e:
        print(f"Error al leer el archivo {nombre_archivo}: {e}")
        return None