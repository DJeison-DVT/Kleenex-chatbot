from app.chatbot.user_flow import *
from app.chatbot.steps import Steps
from app.schemas.user import User
from app.schemas.participation import Participation

INVALID_PHOTO_MAX_OPPORTUNITIES = 3
DAILTY_PARTICIPAITONS = 5

FLOW = {
    Steps.ONBOARDING: ResponseDependentTransition(
        transitions={
            'si acepto': Steps.ONBOARDING_PHOTO,
            'no acepto': Steps.ONBOARDING_TERMS,
        },
        message_template='HX46115dd8934cc5820445eaaf697213a6',
        upload_params=ClassMapping([(User, 'terms')]),
        format_args=ClassMapping([(None, 'current_participations')])
    ),
    Steps.ONBOARDING_TERMS: ResponseDependentTransition(
        transitions={
            'si acepto': Steps.ONBOARDING_PHOTO,
        },
        upload_params=ClassMapping([(User, 'terms')]),
        message_template='HX1eb08f22c35eb59d07edd94015a74c13'
    ),
    Steps.ONBOARDING_PHOTO: MultimediaUploadTransition(
        success_step=Steps.ONBOARDING_NAME,
        failure_step=Steps.ONBOARDING_INVALID_PHOTO,
        message_template='HX0958631a027c2144d92996efbdf5fbdc'
    ),
    Steps.ONBOARDING_INVALID_PHOTO: MultimediaUploadTransition(
        success_step=Steps.ONBOARDING_NAME,
        failure_step=Steps.ONBOARDING_INVALID_PHOTO,
        message_template='HX2158e4b989cc8436f1c0eba4fdf45dc7'
    ),
    Steps.ONBOARDING_NAME: ResponseIndependentTransition(
        next_step=Steps.ONBOARDING_EMAIL,
        message_template='HXa52afbf47de9d5c5b5ffe2078920bafc',
        upload_params=ClassMapping([(User, 'name')])
    ),
    Steps.ONBOARDING_EMAIL: ResponseIndependentTransition(
        next_step=Steps.ONBOARDING_CONFIRMATION,
        message_template='HX3f6d826b3abebbc4efe6a1a72776279d',
        upload_params=ClassMapping([(User, 'email')])
    ),
    Steps.ONBOARDING_CONFIRMATION: ResponseDependentTransition(
        transitions={
            'confirmar': Steps.PRIORITY_NUMBER,
            'editar': Steps.ONBOARDING_NAME,
        },
        message_template='HX4fe9cbfa17572324cda8df6e4780b519',
        format_args=ClassMapping([(User, 'name'), (User, 'email')])
    ),
    Steps.PRIORITY_NUMBER: ServerTransition(
        transitions={
            True: Steps.DASHBOARD_WAITING,
            False: Steps.NO_PRIZE,
        },
        api_endpoint='participation-number/',
        message_template='HX04cb615e50500f09dea065f819a26b10',
        upload_params=ClassMapping([(Participation, 'priority_number')])
    ),
    Steps.NO_PRIZE: ServerTransition(
        transitions=None,
        message_template='HX9129b50ae4c409e207caace3e00f991f',
        format_args=ClassMapping([(Participation, 'priority_number')]),
        upload_params=ClassMapping([(Participation, 'status')])
    ),
    Steps.DASHBOARD_WAITING: DashboardTransition(
        transitions={
            'valid': Steps.DASHBOARD_CONFIRMATION,
            'invalid': Steps.DASHBOARD_REJECTION,
        },
        message_template='HXf5e5575d9a622b9f6c396797433f4688',
        format_args=ClassMapping([(Participation, 'priority_number'), (Participation, 'prize_name')])
    ),
    Steps.DASHBOARD_CONFIRMATION: DashboardTransition(
        message_template='HXaccd22243567d67d646ef272416481f9',
        format_args=ClassMapping([
            (Participation, 'prize_amount'),
            (Participation, 'priority_number'),
            (Participation, 'prize_url'),
            (Participation, 'prize_code')
        ])
    ),
    Steps.DASHBOARD_REJECTION: DashboardTransition(
        message_template='HX07c4758573a8f0dc490e45c604a7a55f'
    )
}
