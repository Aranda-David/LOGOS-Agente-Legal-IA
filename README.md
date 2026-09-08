<div align="center">

# ⚖️ LOGOS — Agente Legal Inteligente

¡Asistente legal local de alto rendimiento para la **auditoría de riesgos**, **redacción jurídica** y **gestión documental** en el derecho español!

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/Orquestación-LangGraph-FF6F00?style=for-the-badge&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama%20%2F%20Llama%203.2-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![RGPD Compliance](https://img.shields.io/badge/Privacidad-100%25%20Local%20%2F%20RGPD-008000?style=for-the-badge&logo=shield&logoColor=white)](#)
[![License](https://img.shields.io/badge/Licencia-MIT-blue?style=for-the-badge)](LICENSE)

</div>

---

## ✨ Características Destacadas

* 🤖 **Flujo Multi-Agente Autónomo:** Arquitectura basada en grafos direccionados (LangGraph) con enrutamiento inteligente entre nodos especializados (Auditoría, Redacción y Consultas Generales).
* 📜 **Rigor Legislativo Español:** Respuestas orientadas a la precisión dogmática y jurisprudencial con citación explícita de artículos y normativa vigente.
* 📄 **Procesamiento Multiformato:** Lectura y extracción directa de datos a partir de archivos `.pdf`, `.docx`, `.rtf`, `.txt` y `.md`.
* 📑 **Generación de Dictámenes Dual:** Exportación instantánea de informes y borradores jurídicos en formato `.docx` (Microsoft Word) y `.pdf` (ReportLab).
* 🔒 **Privacy-First & RGPD Compliance:** Ejecución 100% local sobre Ollama sin envío de datos a servidores externos, garantizando el cumplimiento del RGPD y la máxima confidencialidad.

---

## 🛠️ Arquitectura y Tecnologías

| Componente | Tecnología |
| :--- | :--- |
| **Orquestación de Agentes** | LangGraph / LangChain |
| **Modelo de Lenguaje (LLM)** | Ollama (Llama 3.2) |
| **Interfaz Web (Frontend)** | Streamlit |
| **Generación Documental** | ReportLab (PDF) & `python-docx` (DOCX) |
| **Parsing Documental** | `pypdf` & `striprtf` |

---

## 🚀 Instalación y Configuración Local

### 1. Requisitos Previos

* Python 3.10 o superior instalado.
* [Ollama](https://ollama.com/) instalado en el sistema.
* Git instalado.

### 2. Descargar el modelo en Ollama

```bash
ollama run llama3.2