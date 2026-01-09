from twilio.rest import Client 
from django.conf import settings 
import logging

logger = logging.getLogger(__name__)

def send_whatsapp_notification(recipient_number, message_body):
    """
    Sends a WhatsApp message via Twilio.
    Returns True if successful, False otherwise.
    """
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_WHATSAPP_NUMBER]):
        logger.warning("Twilio API credentials are missing.")
        return False

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Ensure the 'whatsapp:' prefix is added here so models.py doesn't need to worry about it
        formatted_to = f"whatsapp:{recipient_number}"
        
        message = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_NUMBER, 
            body=message_body,
            to=formatted_to 
        )
        print(f"✅ Success! SID: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ Twilio Error: {e}")
        return False