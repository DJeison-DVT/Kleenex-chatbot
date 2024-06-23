from enum import Enum


class Steps(Enum):
    ONBOARDING = 'onboarding'
    ONBOARDING_TERMS = 'onboarding_terms'
    ONBOARDING_PHOTO = 'onboarding_photo'
    ONBOARDING_INVALID_PHOTO = 'onboarding_invalid_photo'
    ONBOARDING_NAME = 'onboarding_name'
    ONBOARDING_EMAIL = 'onboarding_email'
    ONBOARDING_CONFIRMATION = 'onboarding_confirmation'
    EXISTING_USER = 'existing_user'
    VALIDATE_PHOTO = 'validate_photo'
    INVALID_PHOTO = 'invalid_photo'
    PRIORITY_NUMBER = 'priority_number'
    DASHBOARD = 'dashboard_confirmation'
    DASHBOARD_WAITING = 'dashboard_waiting'
    DASHBOARD_CONFIRMATION = 'dashboard_confirmation'
    DASHBOARD_REJECTION = 'dashboard_rejection'

