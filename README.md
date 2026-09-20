<div align="center">

# ⚖️ LOGOS — Agente Legal Inteligente

¡Asistente legal local de alto rendimiento para la **auditoría de riesgos**, **redacción jurídica** y **gestión documental** en el derecho español!

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/Orquestación-LangGraph-FF6F00?style=for-the-badge&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama%20%2F%20Qwen2.5-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![RGPD Compliance](https://img.shields.io/badge/Privacidad-100%25%20Local%20%2F%20RGPD-008000?style=for-the-badge&logo=shield&logoColor=white)](#)
[![License](https://img.shields.io/badge/Licencia-MIT-blue?style=for-the-badge)](LICENSE)

</div>

---

## ✨ Características Destacadas

* 🤖 **Flujo Multi-Agente Autónomo:** Arquitectura basada en grafos direccionados (LangGraph) con enrutamiento inteligente entre nodos especializados (Auditoría, Redacción, Consultas Generales y modo Conversacional).
* 🔍 **RAG Híbrido Avanzado con Rerank:** Combinación de recuperación vectorial en ChromaDB y búsqueda léxica BM25, afinada mediante un modelo Cross-Encoder para garantizar la precisión estricta de plazos y artículos normativos sin contaminación cruzada entre jurisdicciones.
* 📜 **Rigor Legislativo Español:** Respuestas orientadas a la precisión dogmática y jurisprudencial con citación explícita de artículos y normativa vigente.
* 📄 **Procesamiento Multiformato:** Lectura y extracción directa de datos a partir de archivos `.pdf`, `.docx`, `.rtf`, `.txt` y `.md` mediante gestores dedicados.
* 🛡️ **Filtros de Seguridad Extrajudicial:** Mecanismos de purga programática en el nodo verificador para evitar terminología judicial inadecuada (como "suplico") en comunicaciones extrajudiciales.
* 🔒 **Privacy-First & RGPD Compliance:** Ejecución 100% local sobre Ollama sin envío de datos a servidores externos, garantizando la máxima confidencialidad.

---

## 🛠️ Arquitectura y Tecnologías

| Componente | Tecnología |
| :--- | :--- |
| **Orquestación de Agentes** | LangGraph / LangChain |
| **Modelo de Lenguaje (LLM)** | Ollama (Qwen2.5 / Llama) |
| **Base de Datos Vectorial & Híbrida** | ChromaDB & BM25 (`rank-bm25`) |
| **Reranker de Precisión** | `sentence-transformers` (Cross-Encoder) |
| **Interfaz Web (Frontend)** | Streamlit |
| **Procesamiento Documental** | `pypdf`, `python-docx`, `reportlab`, `striprtf` |

---

## 🚀 Instalación y Configuración Local

### 1. Requisitos Previos

* Python 3.10 o superior instalado en el sistema.
* [Ollama](https://ollama.com/) instalado y ejecutándose localmente.
* Git instalado.

### 2. Clonar el Repositorio

```bash
git clone [https://github.com/tu-usuario/LOGOS-Agente-Legal-IA.git](https://github.com/tu-usuario/LOGOS-Agente-Legal-IA.git)
cd LOGOS-Agente-Legal-IA
```
### 3. Configurar el Entorno Virtual e Instalar Dependencias

```bash
Bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```
### 4. Configurar Modelos en Ollama
Asegúrate de descargar el modelo de lenguaje y el de embeddings configurados en el proyecto:

```bash
Bash
ollama pull qwen2.5:14b-instruct
ollama pull nomic-embed-text
```
### 5. Ejecutar la Aplicación

```bash
Bash
streamlit run app.py
```
### 📂 Estructura del Proyecto

```bash

LOGOS-Agente-Legal-IA/
│
├── data/
│   ├── chroma_db/      # Base de datos vectorial persistente
│   ├── jurisprudencia/ # Corpus de sentencias y resoluciones
│   └── legislacion/    # Leyes y códigos fuente normativos
│
├── src/
│   ├── __init__.py
│   ├── config.py       # Configuración global del LLM y entorno
│   ├── document_loader.py # Utilidades de carga y parsing multiformato
│   ├── graph.py        # Definición del grafo de LangGraph y nodos de control
│   ├── ingest.py       # Pipeline de ingesta y segmentación de metadatos
│   ├── prompts.py      # Prompts especializados para cada nodo jurídico
│   ├── rag.py          # Motor de búsqueda híbrida (Vectorial + BM25) y Rerank
│   └── state.py        # Definición tipada del estado de los agentes
│
├── app.py              # Interfaz de usuario principal (Streamlit)
├── main.py             # Punto de entrada CLI principal
├── .env                # Variables de entorno locales
├── .env.example        # Plantilla de variables de entorno
├── .gitignore          # Archivos excluidos del control de versiones
├── requirements.txt    # Dependencias del proyecto
└── README.md           # Documentación del repositorio
```
### Licencia MIT
Copyright (c) 2026 David Aranda Dávila
