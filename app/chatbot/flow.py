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
        message_template=messages[Steps.ONBOARDING],
        upload_params=[('user', 'terms')],
        format_args=['current_participations']
    ),
    Steps.ONBOARDING_TERMS: ResponseDependentTransition(
        transitions={
            'si acepto': Steps.ONBOARDING_PHOTO,
        },
        upload_params=[('user', 'terms')],
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
        message_template=messages[Steps.ONBOARDING_NAME],
        upload_params=[('user', 'name')]
    ),
    Steps.ONBOARDING_EMAIL: ResponseIndependentTransition(
        next_step=Steps.ONBOARDING_CONFIRMATION,
        message_template=messages[Steps.ONBOARDING_EMAIL],
        upload_params=[('user', 'email')]
    ),
    Steps.ONBOARDING_CONFIRMATION: ResponseDependentTransition(
        transitions={
            'confirmar': Steps.PRIORITY_NUMBER,
            'editar': Steps.ONBOARDING_NAME,
        },
        message_template=messages[Steps.ONBOARDING_CONFIRMATION],
        format_args=['name', 'email']
    ),
    Steps.PRIORITY_NUMBER: ServerTransition(
        transitions={
            True: Steps.DASHBOARD_WAITING,
            False: Steps.NO_PRIZE,
        },
        api_endpoint='participation-number/',
        message_template=messages[Steps.PRIORITY_NUMBER],
        upload_params=[('participation', 'priority_number')]
    ),
    Steps.NO_PRIZE: ServerTransition(
        transitions=None,
        message_template=messages[Steps.NO_PRIZE],
        format_args=['priority_number'],
        upload_params=[('participation', 'status')]
    ),
    Steps.DASHBOARD_WAITING: DashboardTransition(
        transitions={
            'valid': Steps.DASHBOARD_CONFIRMATION,
            'invalid': Steps.DASHBOARD_REJECTION,
        },
        message_template=messages[Steps.DASHBOARD_WAITING],
        format_args=['priority_number', 'prize_name']
    ),
    Steps.DASHBOARD_CONFIRMATION: DashboardTransition(
        message_template=messages[Steps.DASHBOARD_CONFIRMATION],
        format_args=['prize_amount', 'priority_number',
                     'prize_url', 'prize_code']
    ),
    Steps.DASHBOARD_REJECTION: DashboardTransition(
        message_template=messages[Steps.DASHBOARD_REJECTION]
    )
}
