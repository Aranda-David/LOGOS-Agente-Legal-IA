from src.graph import app_grafo


def ejecutar_chat():
    print("==================================================")
    print("      LOGOS - AGENTE LEGAL IA LOCAL     ")
    print("==================================================")
    print("Escribe tu consulta legal para LOGOS (o escribe 'salir' para finalizar).\n")

    while True:
        try:
            peticion_usuario = input("\nAbogado > ")

            if peticion_usuario.lower().strip() in ["salir", "exit", "quit"]:
                print("\nCerrando sesión en Logos...")
                break

            if not peticion_usuario.strip():
                continue

            estado_inicial = {
                "peticion_usuario": peticion_usuario,
                "tipo_tarea": "",
                "historial_mensajes": [],
                "respuesta_final": ""
            }

            print("\nLogos está procesando tu consulta...")
            resultado = app_grafo.invoke(estado_inicial)

            print("\n--- RESPUESTA DE LOGOS ---")
            print(resultado["respuesta_final"])
            print("\n" + "=" * 50)

        except KeyboardInterrupt:
            print("\nSesión interrumpida en Logos.")
            break


if __name__ == "__main__":
    ejecutar_chat()