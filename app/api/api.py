from fastapi import APIRouter

from app.core.config import settings
from app.api.endpoints import (
    users,
    participations,
    dashboard,
)

router = APIRouter()


router.include_router(
    users.router, prefix=settings.USER_SECTION, tags=["users"])
router.include_router(participations.router,
                      prefix=settings.PARTICIPATION_SECTION, tags=["participations"])
router.include_router(
    dashboard.router, prefix=settings.DASHBOARD_SECTION, tags=["dashboard"])

api_router = router
