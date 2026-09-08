import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

# Cargar variables de entorno desde la raíz
load_dotenv()

# Instancia centralizada del LLM
llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "llama3.2"),
    temperature=0
)