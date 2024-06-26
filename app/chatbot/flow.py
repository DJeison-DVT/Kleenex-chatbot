from app.chatbot.user_flow import *
from app.chatbot.steps import Steps
from app.chatbot.messages import messages

INVALID_PHOTO_MAX_OPPORTUNITIES = 3
DAILTY_PARTICIPAITONS = 5

FLOW = {
    Steps.ONBOARDING: ResponseDependentTransition(
        transitions={
            'si acepto': Steps.ONBOARDING_PHOTO,
            'no acepto': Steps.ONBOARDING_TERMS,
        },
        message_template=messages[Steps.ONBOARDING]
    ),
    Steps.ONBOARDING_TERMS: ResponseDependentTransition(
        transitions={
            'si acepto': Steps.ONBOARDING_PHOTO,
        },
        message_template=messages[Steps.ONBOARDING_TERMS]
    ),
    Steps.ONBOARDING_PHOTO: MultimediaUploadTransition(
        success_step=Steps.ONBOARDING_NAME,
        failure_step=Steps.ONBOARDING_INVALID_PHOTO,
        message_template=messages[Steps.ONBOARDING_PHOTO]
    ),
    Steps.ONBOARDING_INVALID_PHOTO: MultimediaUploadTransition(
        success_step=Steps.ONBOARDING_NAME,
        failure_step=Steps.ONBOARDING_INVALID_PHOTO,
        message_template=messages[Steps.INVALID_PHOTO]
    ),
    Steps.ONBOARDING_NAME: ResponseIndependentTransition(
        next_step=Steps.ONBOARDING_EMAIL,
        message_template=messages[Steps.ONBOARDING_NAME]
    ),
    Steps.ONBOARDING_EMAIL: ResponseIndependentTransition(
        next_step=Steps.ONBOARDING_CONFIRMATION,
        message_template=messages[Steps.ONBOARDING_EMAIL]
    ),
    Steps.ONBOARDING_CONFIRMATION: ResponseDependentTransition(
        transitions={
            'confirmar': Steps.PRIORITY_NUMBER,
            'editar': Steps.ONBOARDING_NAME,
        },
        message_template=messages[Steps.ONBOARDING_CONFIRMATION]
    ),
    Steps.PRIORITY_NUMBER: ServerTransition(
        transitions={
            True: Steps.DASHBOARD_WAITING,
            False: Steps.NO_PRIZE,
        },
        message_template=messages[Steps.PRIORITY_NUMBER],
        format_args={'participation_number': '1234'}
    ),
    Steps.NO_PRIZE: ServerTransition(
        transitions=None,
        message_template=messages[Steps.NO_PRIZE]
    ),
    Steps.DASHBOARD_WAITING: ResponseDependentTransition(
        transitions={
            'valid': Steps.DASHBOARD_CONFIRMATION,
            'invalid': Steps.DASHBOARD_REJECTION,
        },
        message_template=messages[Steps.DASHBOARD_WAITING]
    ),
    Steps.DASHBOARD_CONFIRMATION: ResponseIndependentTransition(
        next_step=None,
        message_template=messages[Steps.DASHBOARD_CONFIRMATION]
    ),
    Steps.DASHBOARD_REJECTION: ResponseIndependentTransition(
        next_step=None,
        message_template=messages[Steps.DASHBOARD_REJECTION]
    )
}
