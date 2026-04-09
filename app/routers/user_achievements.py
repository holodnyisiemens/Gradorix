from typing import Optional

from fastapi import APIRouter, Depends

from app.auth.utils import get_current_user, require_roles
from app.core.enums import UserRole
from app.dependencies import UserAchievementServiceDep, AchievementServiceDep, NotificationServiceDep
from app.models.user import User
from app.schemas.user_achievement import UserAchievementCreateDTO, UserAchievementReadDTO, UserAchievementUpdateDTO
from app.ws.notify import push_notification

router = APIRouter(prefix="/user-achievements", tags=["User Achievements"])


@router.get("/", response_model=list[UserAchievementReadDTO])
async def get_all(
    user_id: Optional[int] = None,
    service: UserAchievementServiceDep = ...,
    _: User = Depends(get_current_user),
):
    return await service.get_all(user_id=user_id)


@router.get("/{user_id}/{achievement_id}", response_model=UserAchievementReadDTO)
async def get_by_id(
    user_id: int,
    achievement_id: int,
    service: UserAchievementServiceDep = ...,
    _: User = Depends(get_current_user),
):
    return await service.get_by_id(user_id, achievement_id)


@router.post("/", response_model=UserAchievementReadDTO, status_code=201)
async def create(
    data: UserAchievementCreateDTO,
    service: UserAchievementServiceDep,
    achievement_service: AchievementServiceDep,
    notification_service: NotificationServiceDep,
    _: User = Depends(require_roles(UserRole.HR)),
):
    result = await service.create(data)

    try:
        achievement = await achievement_service.get_by_id(data.achievement_id)
        await push_notification(
            data.user_id,
            f"🏆 Вы получили достижение «{achievement.title}»! +{achievement.xp} XP",
            notification_service,
        )
    except Exception:
        pass

    return result


@router.patch("/{user_id}/{achievement_id}", response_model=UserAchievementReadDTO)
async def update(
    user_id: int,
    achievement_id: int,
    data: UserAchievementUpdateDTO,
    service: UserAchievementServiceDep = ...,
    _: User = Depends(require_roles(UserRole.HR)),
):
    return await service.update(user_id, achievement_id, data)


@router.delete("/{user_id}/{achievement_id}", status_code=204)
async def delete(
    user_id: int,
    achievement_id: int,
    service: UserAchievementServiceDep = ...,
    _: User = Depends(require_roles(UserRole.HR)),
):
    await service.delete(user_id, achievement_id)
