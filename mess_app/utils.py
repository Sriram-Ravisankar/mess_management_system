from twilio.rest import Client 
from django.conf import settings 
import logging

logger = logging.getLogger(__name__)

def send_whatsapp_notification(recipient_number, message_body):
    
    # Check if Twilio settings are configured before attempting to send
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_WHATSAPP_NUMBER]):
        logger.warning("Twilio API credentials are missing. Skipping WhatsApp notification.")
        return False

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        # NOTE: recipient_number must be prepended with 'whatsapp:' if sending via WhatsApp
        
        message = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            body=message_body,
            to=recipient_number # e.g. 'whatsapp:+1234567890'
        )
        logger.info(f"WhatsApp message sent to {recipient_number}. SID: {message.sid}")
        return True
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message to {recipient_number}: {e}")
        return False