from enum import Enum


class Steps(Enum):
    ONBOARDING = 'onboarding'
    ONBOARDING_TERMS = 'onboarding_terms'
    ONBOARDING_PHOTO = 'onboarding_photo'
    ONBOARDING_INVALID_PHOTO = 'onboarding_invalid_photo'
    ONBOARDING_NAME = 'onboarding_name'
    ONBOARDING_EMAIL = 'onboarding_email'
    ONBOARDING_CONFIRMATION = 'onboarding_confirmation'
    PRIORITY_NUMBER = 'priority_number'
    NO_PRIZE = 'no_prize'
    DASHBOARD_WAITING = 'dashboard_waiting'
    DASHBOARD_CONFIRMATION = 'dashboard_confirmation'
    DASHBOARD_REJECTION = 'dashboard_rejection'
    VALIDATE_PHOTO = 'validate_photo'
    INVALID_PHOTO = 'invalid_photo'
