import os

from flask import current_app
from google.cloud import dialogflow
from google.oauth2 import service_account


class ChatbotService:
    def __init__(self):
        """
        Constructor ligero. 
        No accedemos a current_app aquí para evitar el RuntimeError de contexto.
        """
        self.language_code = 'es'

    def _get_credentials(self):
        """
        Método privado para obtener credenciales solo cuando se necesitan.
        """
        credentials_info = current_app.config.get('GOOGLE_CREDENTIALS')
        
        if not credentials_info or not credentials_info.get('project_id'):
            raise ValueError("Las credenciales de Google Cloud no están configuradas en la App.")
            
        project_id = credentials_info.get('project_id')
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        
        return project_id, credentials

    def get_response(self, user_message: str, user_id: str = "usuario_anonimo") -> str:
        """
        Envía el mensaje a Dialogflow y retorna la respuesta.
        """
        try:
            # Obtenemos las credenciales dentro del contexto de la petición
            project_id, credentials = self._get_credentials()

            # Inicializamos el cliente con las credenciales cargadas
            session_client = dialogflow.SessionsClient(credentials=credentials)
            session = session_client.session_path(project_id, user_id)

            # Preparar la entrada de texto
            text_input = dialogflow.TextInput(
                text=user_message, 
                language_code=self.language_code
            )
            query_input = dialogflow.QueryInput(text=text_input)

            # Petición a Dialogflow
            response = session_client.detect_intent(
                request={"session": session, "query_input": query_input}
            )

            return response.query_result.fulfillment_text

        except ValueError as ve:
            print(f"Error de configuración: {ve}")
            return "El servicio de chat no está disponible en este momento."
        except Exception as e:
            print(f"Error conectando con Dialogflow: {e}")
            return "Lo siento, tuve un problema conectando con mi servidor de inteligencia artificial."