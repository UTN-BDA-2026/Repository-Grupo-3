from flask import Blueprint, request

from app.config import ResponseBuilder
from app.services.chatbot_service import ChatbotService

ChatbotBP = Blueprint('Chatbot', __name__)


@ChatbotBP.route('/chatbot/query', methods=['POST'])
def handle_query():
    service = ChatbotService()
    response_builder = ResponseBuilder()
    try:
        data = request.get_json()
        message = data.get("message")
        if not message:
            return response_builder.add_message("Mensaje no puede estar vacío").add_status_code(400).build(), 400

        bot_reply = service.get_response(message)
        
        return response_builder.add_data({"reply": bot_reply}).add_status_code(200).build(), 200

    except Exception as e:
        return response_builder.add_message(str(e)).add_status_code(500).build(), 500