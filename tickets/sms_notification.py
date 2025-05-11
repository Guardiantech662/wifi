from twilio.rest import Client
from django.conf import settings

def send_sms(to_number, message):
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_number
        )
        print(f"SMS sent to {to_number}")
    except Exception as e:
        print(f"SMS send failed: {e}")
