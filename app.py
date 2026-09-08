import io
import html
import streamlit as st
from pypdf import PdfReader
from docx import Document
from striprtf.striprtf import rtf_to_text
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from src.graph import app_grafo

# Configuración de la página
st.set_page_config(
    page_title="LOGOS - Agente IA Legal",
    page_icon="⚖️",
    layout="wide"
)


# --- FUNCIÓN DE EXTRACCIÓN MULTIFORMATO ---
def extraer_texto_documento(archivo) -> str:
    """Extrae texto de archivos PDF, DOCX, RTF, TXT y MD."""
    nombre = archivo.name.lower()
    texto = ""

    try:
        if nombre.endswith(".pdf"):
            reader = PdfReader(archivo)
            for page in reader.pages:
                texto += page.extract_text() or ""

        elif nombre.endswith(".docx"):
            doc = Document(archivo)
            texto = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

        elif nombre.endswith(".rtf"):
            contenido_rtf = archivo.read().decode("utf-8", errors="ignore")
            texto = rtf_to_text(contenido_rtf)

        elif nombre.endswith((".txt", ".md")):
            texto = archivo.read().decode("utf-8", errors="ignore")

        elif nombre.endswith(".doc"):
            st.warning(
                "⚠️ Los archivos .doc antiguos no son directamente compatibles. Por favor, guárdalo como .docx en Word antes de adjuntarlo.")
            return ""

    except Exception as e:
        st.error(f"Error al procesar el archivo {archivo.name}: {str(e)}")
        return ""

    return texto.strip()


# --- FUNCIÓN PARA GENERAR DOCUMENTO WORD (.DOCX) ---
def crear_documento_word(texto_dictamen: str) -> io.BytesIO:
    """Genera un archivo .docx en memoria a partir del texto del dictamen."""
    doc = Document()
    doc.add_heading("LOGOS — Dictamen / Documento Jurídico", level=1)

    for line in texto_dictamen.split("\n"):
        if line.strip():
            doc.add_paragraph(line)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


# --- FUNCIÓN PARA GENERAR DOCUMENTO PDF (.PDF) ---
def crear_documento_pdf(texto_dictamen: str) -> io.BytesIO:
    """Genera un archivo PDF profesional en memoria a partir del texto del dictamen."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        'TituloDictamen',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        spaceAfter=12
    )
    estilo_cuerpo = ParagraphStyle(
        'CuerpoDictamen',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=8
    )

    story = []

    # Título principal
    story.append(Paragraph("LOGOS — Dictamen / Documento Jurídico", estilo_titulo))
    story.append(Spacer(1, 12))

    # Párrafos del texto (escapando caracteres HTML para evitar errores de sintaxis en ReportLab)
    for linea in texto_dictamen.split("\n"):
        linea_limpia = linea.strip()
        if linea_limpia:
            linea_escapada = html.escape(linea_limpia)
            story.append(Paragraph(linea_escapada, estilo_cuerpo))
        else:
            story.append(Spacer(1, 6))

    doc.build(story)
    buffer.seek(0)
    return buffer


# Estilo y título principal
st.title("⚖️ LOGOS — Agente Legal Inteligente")
st.caption("Sistema local de auditoría y redacción jurídica impulsado por LangGraph y Ollama (RGPD Compliant)")

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.image("https://img.icons8.com/scales", width=80)
    st.header("⚙️ Panel de Control")
    st.write("Configura la sesión o adjunta documentación.")

    modo_analisis = st.selectbox(
        "Modo de trabajo preferido:",
        ["Enrutado Automático (IA)", "Auditoría de Riesgos", "Redacción Jurídica", "Consulta General"]
    )

    st.divider()

    st.subheader("📄 Cargar Documento Legal")
    archivo_adjunto = st.file_uploader(
        "Adjunta tu documento (PDF, DOCX, RTF, TXT, MD)",
        type=["pdf", "docx", "rtf", "txt", "md"]
    )

    texto_documento_extraido = ""
    if archivo_adjunto is not None:
        texto_documento_extraido = extraer_texto_documento(archivo_adjunto)
        if texto_documento_extraido:
            st.success(f"✅ '{archivo_adjunto.name}' procesado correctamente.")

    st.divider()

    if st.button("🗑️ Limpiar Conversación"):
        st.session_state.mensajes = []
        st.rerun()

st.divider()

# --- CHAT PRINCIPAL ---

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Mostrar historial con botones de descarga para respuestas de LOGOS
for i, msg in enumerate(st.session_state.mensajes):
    with st.chat_message(msg["rol"]):
        st.markdown(msg["contenido"])

        if msg["rol"] == "assistant":
            col1, col2, _ = st.columns([1, 1, 3])
            with col1:
                buffer_word = crear_documento_word(msg["contenido"])
                st.download_button(
                    label="📥 Descargar Word (.docx)",
                    data=buffer_word,
                    file_name=f"Dictamen_LOGOS_{i}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"dl_word_{i}"
                )
            with col2:
                buffer_pdf = crear_documento_pdf(msg["contenido"])
                st.download_button(
                    label="📄 Descargar PDF (.pdf)",
                    data=buffer_pdf,
                    file_name=f"Dictamen_LOGOS_{i}.pdf",
                    mime="application/pdf",
                    key=f"dl_pdf_{i}"
                )

# Entrada del usuario
if peticion := st.chat_input("Escribe tu instrucción legal aquí..."):

    peticion_completa = peticion
    if texto_documento_extraido:
        peticion_completa = (
            f"{peticion}\n\n"
            f"--- TEXTO EXTRAÍDO DEL DOCUMENTO ADJUNTO ({archivo_adjunto.name}) ---\n"
            f"{texto_documento_extraido}"
        )

    st.session_state.mensajes.append({"rol": "user", "contenido": peticion})
    with st.chat_message("user"):
        st.markdown(peticion)

    with st.chat_message("assistant"):
        with st.spinner("LOGOS está analizando la documentación y la legislación aplicable..."):
            estado_inicial = {
                "peticion_usuario": peticion_completa,
                "tipo_tarea": "",
                "historial_mensajes": [],
                "respuesta_final": ""
            }

            resultado = app_grafo.invoke(estado_inicial)
            respuesta = resultado["respuesta_final"]

            st.markdown(respuesta)

            # Botones de descarga inmediatos para la respuesta recién generada
            col1, col2, _ = st.columns([1, 1, 3])
            with col1:
                buffer_word = crear_documento_word(respuesta)
                st.download_button(
                    label="📥 Descargar Word (.docx)",
                    data=buffer_word,
                    file_name="Dictamen_LOGOS.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="dl_word_nuevo"
                )
            with col2:
                buffer_pdf = crear_documento_pdf(respuesta)
                st.download_button(
                    label="📄 Descargar PDF (.pdf)",
                    data=buffer_pdf,
                    file_name="Dictamen_LOGOS.pdf",
                    mime="application/pdf",
                    key="dl_pdf_nuevo"
                )

            st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta})