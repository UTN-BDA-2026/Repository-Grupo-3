import os
import requests

class PushNotificationService:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_ids_raw = os.getenv('TELEGRAM_CHAT_IDS')
        
        if chat_ids_raw:
            self.chat_ids = [id.strip() for id in chat_ids_raw.split(',')]
        else:
            self.chat_ids = []
        
        self.is_configured = all([self.bot_token, self.chat_ids])
        if not self.is_configured:
            print("ADVERTENCIA: Telegram no configurado correctamente. Alertas deshabilitadas.")

    def send_notification(self, message, title="🔔 Alerta de Salón"):
        """Envía la notificación a todos los administradores configurados"""
        if not self.is_configured:
            return False

        texto_final = f"*{title}*\n\n{message}"
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        success = True
        for chat_id in self.chat_ids:
            payload = {
                "chat_id": chat_id,
                "text": texto_final,
                "parse_mode": "Markdown"
            }

            try:
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    print(f"Notificación enviada al admin {chat_id}")
                else:
                    print(f"Error Telegram (ID {chat_id}): {response.text}")
                    success = False
            except Exception as e:
                print(f"ERROR en Telegram Service para ID {chat_id}: {e}")
                success = False
        
        return success