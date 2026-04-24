from fastapi import APIRouter, Depends, status

from app.auth.utils import get_current_user
from app.dependencies import PushServiceDep
from app.models.user import User
from app.schemas.push import PushSubscribeDTO

router = APIRouter(prefix="/push", tags=["Push"])


@router.post("/subscribe", status_code=status.HTTP_204_NO_CONTENT)
async def subscribe(
    data: PushSubscribeDTO,
    service: PushServiceDep,
    current_user: User = Depends(get_current_user),
):
    await service.subscribe(data, user_id=current_user.id)
