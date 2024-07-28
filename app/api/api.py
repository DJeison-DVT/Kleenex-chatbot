from fastapi import APIRouter

from app.core.config import settings
from app.api.endpoints import (
    users,
    participations,
    dashboard,
    auth,
)

router = APIRouter()


router.include_router(
    users.router, prefix=settings.USER_SECTION, tags=["users"])
router.include_router(participations.router,
                      prefix=settings.PARTICIPATION_SECTION, tags=["participations"])
router.include_router(
    dashboard.router, prefix=settings.DASHBOARD_SECTION, tags=["dashboard"])
router.include_router(
    auth.router, prefix=settings.AUTH_SECTION, tags=['auth']
)

api_router = router
