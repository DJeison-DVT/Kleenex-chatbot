import os
import urllib.parse
import requests
from fastapi import HTTPException
from httpx import AsyncClient

from app.chatbot.steps import Steps
from app.schemas.user import User
from app.core.config import settings


class Message:
    def __init__(self, body):
        body_str = body.decode()
        parsed_body = urllib.parse.parse_qs(body_str)

        # Unique ID of the message
        self.sms_message_sid = parsed_body.get('SmsMessageSid', [None])[0]
        # Number of media files in the message
        self.num_media = int(parsed_body.get(
            'NumMedia', [0])[0])  # Convert to int
        # WhatsApp Profile name
        self.profile_name = parsed_body.get('ProfileName', [None])[0]
        # Type of message (e.g. 'text', 'image', 'audio', etc.)
        self.message_type = parsed_body.get('MessageType', [None])[0]
        # Content of the message
        self.body_content = parsed_body.get('Body', [None])[0]
        self.from_number = parsed_body.get('From', [None])[0]
        self.to_number = parsed_body.get('To', [None])[0]
        # Store media URLs if any
        self.media_urls = []
        if self.num_media > 0:
            self.media_urls = [
                urllib.parse.unquote(
                    parsed_body.get(f'MediaUrl{i}', [None])[0])
                for i in range(self.num_media)
            ]

    def download_media(self, folder_path='downloaded_media'):
        # Local Download Placeholder
        # TODO Implement download to cloud storage
        # Ensure the folder exists
        os.makedirs(folder_path, exist_ok=True)

        # Download each media file
        for url in self.media_urls:
            if url:
                response = requests.get(url)
                if response.status_code == 200:
                    file_path = os.path.join(
                        folder_path, f"media_{self.sms_message_sid}_{self.media_urls.index(url)}.jpeg")
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    print(f"Downloaded {file_path}")
                else:
                    print(f"Failed to download media from {url}")


def send_message(client, body: str, message: Message = None, user: User = None):
    from_number = None
    to_number = None

    print(user, message)
    if not message and user:
        from_number = user.phone
        to_number = settings.TWILIO_WHATSAPP_NUMBER

    else:
        from_number = message.to_number
        to_number = message.from_number

    print(f"Sending message from {from_number} to {to_number}")
    try:
        client.messages.create(
            from_=from_number,
            body=body,
            to=to_number
        )
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")


messages = {
    "error": (
        "😫 Lo siento, ocurrió un error inesperado. Por favor intenta más tarde o envíanos un correo a:"
    ),
    Steps.ONBOARDING: (
        "👋Bienvenido a la promoción 'Kleenex contigo en cada historia' ❤️.\n"
        "Recuerda que para participar tienes que ser mayor de 18 años ✅.\n"
        "He leído 📖 y acepto el aviso de privacidad y términos y condiciones 🥸, puedes consultarlos en https://dmente.mx/kleenexcontigo 📃\n"
        "Hasta el momento se han registrado {tickets_registered} tickets 🛒🥳\n\n"
        "SI ACEPTO\n"
        "NO ACEPTO"
    ),
    Steps.ONBOARDING_TERMS: (
        "😫 Lo sentimos para poder participar es necesario aceptar "
        "terminos y condiciónes y Aviso de Privacidad, puedes pulsar "
        "'SI ACEPTO' ✅ para continuar\n\n"
        "SI ACEPTO"
    ),
    "exceeded_participation": (
        "😫 Lo siento, has excedido el número de participaciones diarias autorizadas 📅, nos vemos mañana!!!"
    ),
    Steps.ONBOARDING_PHOTO: (
        "Por favor envía una foto de tu ticket o factura 📸🧾 para iniciar tu participación en la "
        "promoción 'Kleenex contigo en cada historia' ❤️ debe ser clara y legible."
    ),
    Steps.ONBOARDING_NAME: (
        "Iniciemos el registro. Te solicitaré algunos datos por única vez ✍️.\n"
        "¿Cuál es tu nombre completo? Sin abreviaturas.\n"
        "(Ej. María Guadalupe Pérez López)\n\n"
    ),
    Steps.ONBOARDING_EMAIL: (
        "¿Cuál es tu correo electrónico?\n\n"
    ),
    Steps.ONBOARDING_CONFIRMATION: (
        "Muy bien. Estos son los datos que registraste:\n"
        "Nombre: {name}\n"
        "Correo electrónico: {email}."
    ),
    Steps.INVALID_PHOTO: (
        "😔 No pude leer correctamente tu ticket, por favor envía otra foto más clara y legible 🧾🤳"
    ),
    "processing_error": (
        "🤯 No pudimos procesar tu ticket de compra, si tienes dudas por favor envíanos un correo a: promociones@dmente.mx"
    ),
    Steps.PRIORITY_NUMBER: "Por favor espera un momento, estamos validando tu ticket ⏳⏰",
    Steps.NO_PRIZE: (
        "Gracias por participar en la promoción 'Kleenex contigo en cada historia' ❤️\n"
        "Tu número de participación es {participation_number}\n"
        "Recuerda 👀 que mientras más tickets registres, más posibilidades tienes de ganar 🏆🥳\n"
        "Consulta prelación y premios en: https://dmente.mx/kleenexcontigo"
    ),
    Steps.DASHBOARD_WAITING: (
        "¡¡Felicidades!! 👍👊😃🥳🎁 Eres el posible ganador de {prize}. Tu\n"
        "número de participación es {participation_number}. Vamos a validar tu ticket y nos\n"
        "pondremos en contacto contigo en un lapso de 48 a 72hrs hábiles.\n"
        "Gracias por registrarte con nosotros 🤩😃👏."
    ),
    Steps.DASHBOARD_REJECTION: (
        "😔 Lo siento, tu ticket no cumple con la mecánica de participación.\n"
        "Puedes consultar términos y condiciones en https://dmente.mx/kleenexcontigo\n"
        "Si tienes dudas envíanos un correo a: promociones@dmente.mx"
    ),
    Steps.DASHBOARD_CONFIRMATION: (
        "¡¡Felicidades!! 👍👊😃🥳🎁 Eres el ganador de un cupón digital con\n"
        "valor de ${prize_value} MXN. Tu número de participación es {participation_number}. Para poder recibir tu\n"
        "premio, entra en la siguiente enlace url {url}, con el siguiente código: {code}"
    ),
}
