from app.chatbot.user_flow import *
INVALID_PHOTO_MAX_OPPORTUNITIES = 3
DAILTY_PARTICIPAITONS = 5

FLOW = {
    Steps.ONBOARDING.value: FlowStep(
        name=Steps.ONBOARDING.value,
        transition=ResponseDependentTransition(
            transitions={
                'si acepto': Steps.ONBOARDING_PHOTO.value,
                'no acepto': Steps.ONBOARDING_TERMS.value,
            })),
    Steps.ONBOARDING_TERMS.value: FlowStep(
        name=Steps.ONBOARDING_TERMS.value,
        transition=ResponseDependentTransition(
            transitions={
                'si acepto': Steps.ONBOARDING_PHOTO.value,
            })),
    Steps.ONBOARDING_PHOTO.value: FlowStep(
        name=Steps.ONBOARDING_PHOTO.value,
        transition=MultimediaUploadTransition(
            success_step=Steps.ONBOARDING_NAME.value,
            failure_step=Steps.ONBOARDING_INVALID_PHOTO.value)),
    Steps.ONBOARDING_INVALID_PHOTO.value: FlowStep(
        name=Steps.ONBOARDING_INVALID_PHOTO.value,
        transition=MultimediaUploadTransition(
            success_step=Steps.ONBOARDING_NAME.value,
            failure_step=Steps.ONBOARDING_INVALID_PHOTO.value)),
    Steps.ONBOARDING_NAME.value: FlowStep(
        name=Steps.ONBOARDING_NAME.value,
        transition=ResponseIndependentTransition(
            next_step=Steps.ONBOARDING_EMAIL.value)),
    Steps.ONBOARDING_EMAIL.value: FlowStep(
        name=Steps.ONBOARDING_EMAIL.value,
        transition=ResponseIndependentTransition(
            next_step=Steps.ONBOARDING_CONFIRMATION.value)),
    Steps.ONBOARDING_CONFIRMATION.value: FlowStep(
        name=Steps.ONBOARDING_CONFIRMATION.value,
        transition=ResponseDependentTransition(
            transitions={
                'confirmar': Steps.PRIORITY_NUMBER.value,
                'editar': Steps.ONBOARDING_NAME.value,
            })),
    Steps.PRIORITY_NUMBER.value: FlowStep(
        name=Steps.PRIORITY_NUMBER.value,
        transition=DashboardTransition(
            end_step=Steps.DASHBOARD_WAITING.value)),
    Steps.DASHBOARD_WAITING.value: FlowStep(
        name=Steps.DASHBOARD_WAITING.value,
        transition=ResponseDependentTransition(
            transitions={
                'valid': Steps.DASHBOARD_CONFIRMATION.value,
                'invalid': Steps.DASHBOARD_REJECTION.value,
            })),
    Steps.DASHBOARD_CONFIRMATION.value: FlowStep(
        name=Steps.DASHBOARD_CONFIRMATION.value,
        transition=ResponseIndependentTransition(
            next_step=None)),
    Steps.DASHBOARD_REJECTION.value: FlowStep(
        name=Steps.DASHBOARD_REJECTION.value,
        transition=ResponseIndependentTransition(
            next_step=None)),
    Steps.VALIDATE_PHOTO.value: FlowStep(
        name=Steps.VALIDATE_PHOTO.value,
        transition=MultimediaUploadTransition(
            success_step=Steps.PRIORITY_NUMBER.value,
            failure_step=Steps.INVALID_PHOTO.value)),
    Steps.INVALID_PHOTO.value: FlowStep(
        name=Steps.INVALID_PHOTO.value,
        transition=MultimediaUploadTransition(
            success_step=Steps.PRIORITY_NUMBER.value,
            failure_step=Steps.INVALID_PHOTO.value))
}


def get_user_flow(user: User) -> UserFlowManager:
    return UserFlowManager(user, FLOW)
