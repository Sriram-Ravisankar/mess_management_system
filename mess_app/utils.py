# mess_app/utils.py

from twilio.rest import Client # type: ignore
from django.conf import settings # type: ignore
import logging

logger = logging.getLogger(__name__)

def send_whatsapp_notification(recipient_number, message_body):
    """
    Sends a WhatsApp message using the Twilio API.
    Recipient number must be in WhatsApp format, e.g., 'whatsapp:+919876543210'
    """
    # Check if Twilio settings are configured before attempting to send
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_WHATSAPP_NUMBER]):
        logger.warning("Twilio API credentials are missing. Skipping WhatsApp notification.")
        return False

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        # NOTE: recipient_number must be prepended with 'whatsapp:' if sending via WhatsApp
        # Ensure the phone number format matches Twilio requirements (E.164 format)
        
        message = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            body=message_body,
            to=recipient_number # Expects E.164 format, e.g. 'whatsapp:+1234567890'
        )
        logger.info(f"WhatsApp message sent to {recipient_number}. SID: {message.sid}")
        return True
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message to {recipient_number}: {e}")
        return False