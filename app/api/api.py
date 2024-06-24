from fastapi import APIRouter

from app.api.endpoints import (
    users,
    participations
)

router = APIRouter()

router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(participations.router,
                      prefix="/participations", tags=["participations"])

api_router = router
