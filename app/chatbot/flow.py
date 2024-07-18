from app.chatbot.steps import Steps
from app.schemas.user import User
from app.schemas.participation import Participation, Status
from app.chatbot.transitions import *
from app.core.services.priority_number import set_priority_number


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
    Steps.VALIDATE_PHOTO: MultimediaUploadTransition(
        success_step=Steps.PRIORITY_NUMBER,
        failure_step=Steps.INVALID_PHOTO,
        message_template='HX842b1bcba42432bd76984e35a3c406c8',
        format_args=ClassMapping([(None, 'current_participations')]),
    ),
    Steps.ONBOARDING_INVALID_PHOTO: MultimediaUploadTransition(
        success_step=Steps.ONBOARDING_NAME,
        failure_step=Steps.ONBOARDING_INVALID_PHOTO,
        message_template='HX2158e4b989cc8436f1c0eba4fdf45dc7'
    ),
    Steps.INVALID_PHOTO: MultimediaUploadTransition(
        success_step=Steps.PRIORITY_NUMBER,
        failure_step=Steps.INVALID_PHOTO,
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
        upload_params=ClassMapping([(User, 'complete')]),
        format_args=ClassMapping([(User, 'name'), (User, 'email')])
    ),
    Steps.PRIORITY_NUMBER: ServerTransition(
        transitions={
            True: Steps.DASHBOARD_WAITING,
            False: Steps.NO_PRIZE,
        },
        action=set_priority_number,
        message_template='HX04cb615e50500f09dea065f819a26b10',
        status=Status.PENDING.value
    ),
    Steps.NO_PRIZE: ServerTransition(
        transitions=None,
        message_template='HX9129b50ae4c409e207caace3e00f991f',
        format_args=ClassMapping([(Participation, 'priority_number')]),
        status=Status.COMPLETE.value
    ),
    Steps.DASHBOARD_WAITING: DashboardTransition(
        transitions={
            'valid': Steps.DASHBOARD_CONFIRMATION,
            'invalid': Steps.DASHBOARD_REJECTION,
        },
        message_template='HXf5e5575d9a622b9f6c396797433f4688',
        format_args=ClassMapping(
            [(Participation, 'priority_number'), (Participation, 'prize_name')])
    ),
    Steps.DASHBOARD_CONFIRMATION: DashboardTransition(
        message_template='HXaccd22243567d67d646ef272416481f9',
        format_args=ClassMapping([
            (Participation, 'prize_amount'),
            (Participation, 'priority_number'),
            (Participation, 'prize_url'),
            (Participation, 'prize_code')
        ]),
        status=Status.COMPLETE.value
    ),
    Steps.DASHBOARD_REJECTION: DashboardTransition(
        message_template='HX07c4758573a8f0dc490e45c604a7a55f',
        status=Status.REJECTED.value
    ),
    Steps.NEW_PARTICIPATION: ResponseIndependentTransition(
        next_step=Steps.VALIDATE_PHOTO,
        message_template='HX842b1bcba42432bd76984e35a3c406c8',
    ),
    Steps.MAX_PARTICIPATIONS: ServerTransition(
        transitions=None,
        message_template='HX4fa1b484f4549d844bb2489db9bf21d8',
    ),
}
