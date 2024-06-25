

messages = {
    "error": (
        "😫 Lo siento, ocurrió un error inesperado. Por favor intenta más tarde o envíanos un correo a:"
    ),
    "welcome": (
        "👋Bienvenido a la promoción 'Kleenex contigo en cada historia' ❤️.\n"
        "Recuerda que para participar tienes que ser mayor de 18 años ✅.\n"
        "He leído 📖 y acepto el aviso de privacidad y términos y condiciones 🥸, puedes consultarlos en https://dmente.mx/kleenexcontigo 📃\n"
        "Hasta el momento se han registrado {tickets_registered} tickets 🛒🥳\n\n"
        "SI ACEPTO\n"
        "NO ACEPTO"
    ),
    "terms_denial": (
        "😫 Lo sentimos para poder participar es necesario aceptar "
        "terminos y condiciónes y Aviso de Privacidad, puedes pulsar "
        "'SI ACEPTO' ✅ para continuar\n\n"
        "SI ACEPTO"
    ),
    "ticket_submission": (
        "👋Bienvenido a la promoción 'Kleenex contigo en cada historia' ❤️.\n"
        "Por favor envía una foto de tu ticket o factura 📸🧾 para iniciar tu participación en la "
        "promoción 'Kleenex contigo en cada historia' ❤️ debe ser clara y legible.\n"
        "Hasta el momento se han registrado {tickets_registered} tickets 🛒🥳"
    ),
    "exceeded_participation": (
        "😫 Lo siento, has excedido el número de participaciones diarias autorizadas 📅, nos vemos mañana!!!"
    ),
    "registration_prompt": (
        "Por favor envía una foto de tu ticket o factura 📸🧾 para iniciar tu participación en la "
        "promoción 'Kleenex contigo en cada historia' ❤️ debe ser clara y legible."
    ),
    "registration_start": (
        "Iniciemos el registro. Te solicitaré algunos datos por única vez ✍️.\n"
        "¿Cuál es tu nombre completo? Sin abreviaturas.\n"
        "(Ej. María Guadalupe Pérez López)\n\n"
        "¿Cuál es tu correo electrónico?\n\n"
        "Muy bien. Estos son los datos que registraste:\n"
        "Nombre: {name}\n"
        "Correo electrónico: {email}."
    ),
    "edit_confirm_options": "✔️ CONFIRMAR\n❌ EDITAR",
    "poor_image_quality": (
        "😔 No pude leer correctamente tu ticket, por favor envía otra foto más clara y legible 🧾🤳"
    ),
    "processing_error": (
        "🤯 No pudimos procesar tu ticket de compra, si tienes dudas por favor envíanos un correo a: promociones@dmente.mx"
    ),
    "validating_ticket": "Por favor espera un momento, estamos validando tu ticket ⏳⏰",
    "participation_confirmation": (
        "Gracias por participar en la promoción 'Kleenex contigo en cada historia' ❤️\n"
        "Tu número de participación es {participation_number}\n"
        "Recuerda 👀 que mientras más tickets registres, más posibilidades tienes de ganar 🏆🥳\n"
        "Consulta prelación y premios en: https://dmente.mx/kleenexcontigo"
    ),
    "potential_winner_notification": (
        "¡¡Felicidades!! 👍👊😃🥳🎁 Eres el posible ganador de {prize}. Tu\n"
        "número de participación es {participation_number}. Vamos a validar tu ticket y nos\n"
        "pondremos en contacto contigo en un lapso de 48 a 72hrs hábiles.\n"
        "Gracias por registrarte con nosotros 🤩😃👏."
    ),
    "ticket_rejection": (
        "😔 Lo siento, tu ticket no cumple con la mecánica de participación.\n"
        "Puedes consultar términos y condiciones en https://dmente.mx/kleenexcontigo\n"
        "Si tienes dudas envíanos un correo a: promociones@dmente.mx"
    ),
    "winner_announcement": (
        "¡¡Felicidades!! 👍👊😃🥳🎁 Eres el ganador de un cupón digital con\n"
        "valor de ${prize_value} MXN. Tu número de participación es {participation_number}. Para poder recibir tu\n"
        "premio, entra en la siguiente enlace url {url}, con el siguiente código: {code}"
    ),
}

# Example usage
# print(messages["welcome"].format(tickets_registered=123))
# print(messages["registration_start"].format(name="John Doe", email="john.doe@example.com"))
# print(messages["participation_confirmation"].format(participation_number=456))
# print(messages["winner_announcement"].format(prize_value=1000, participation_number=789, url="https://example.com", code="ABCD1234"))
