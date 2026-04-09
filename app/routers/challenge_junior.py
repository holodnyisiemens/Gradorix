from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from starlette import status as http_status

from app.auth.utils import get_current_user, require_roles
from app.core.enums import ChallengeJuniorProgress, ChallengeStatus, UserRole
from app.dependencies import ChallengeJuniorServiceDep, ChallengeServiceDep, NotificationServiceDep
from app.models.user import User
from app.schemas.challenge_junior import ChallengeJuniorCreateDTO, ChallengeJuniorReadDTO, ChallengeJuniorUpdateDTO
from app.ws.notify import push_notification

router = APIRouter(prefix="/challenge-junior", tags=["Challenge-Junior"])


@router.get("/", response_model=list[ChallengeJuniorReadDTO])
async def get_all(
    junior_id: Optional[int] = None,
    assigned_by: Optional[int] = None,
    service: ChallengeJuniorServiceDep = ...,
    _: User = Depends(get_current_user),
):
    return await service.get_all(junior_id=junior_id, assigned_by=assigned_by)


@router.get("/{challenge_id}/{junior_id}", response_model=ChallengeJuniorReadDTO)
async def get_by_id(
    challenge_id: int,
    junior_id: int,
    service: ChallengeJuniorServiceDep,
    _: User = Depends(get_current_user),
):
    return await service.get_by_id(challenge_id, junior_id)


@router.post("/", response_model=ChallengeJuniorReadDTO, status_code=201)
async def create(
    data: ChallengeJuniorCreateDTO,
    service: ChallengeJuniorServiceDep,
    challenge_service: ChallengeServiceDep,
    notification_service: NotificationServiceDep,
    _: User = Depends(require_roles(UserRole.HR, UserRole.MENTOR)),
):
    result = await service.create(data)

    try:
        challenge = await challenge_service.get_by_id(data.challenge_id)
        await push_notification(
            data.junior_id,
            f"🎯 Вам назначена задача «{challenge.title}»",
            notification_service,
        )
    except Exception:
        pass

    return result


@router.patch("/{challenge_id}/{junior_id}", response_model=ChallengeJuniorReadDTO)
async def update(
    challenge_id: int,
    junior_id: int,
    data: ChallengeJuniorUpdateDTO,
    service: ChallengeJuniorServiceDep,
    challenge_service: ChallengeServiceDep,
    notification_service: NotificationServiceDep,
    current_user: User = Depends(get_current_user),
):
    # JUNIOR can only update their own assignment
    if current_user.role == UserRole.JUNIOR and current_user.id != junior_id:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="Forbidden")

    challenge = await challenge_service.get_by_id(challenge_id)

    if current_user.role == UserRole.JUNIOR:
        # HiPo can only work on ACTIVE challenges
        if challenge.status != ChallengeStatus.ACTIVE:
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail=f"Challenge is not ACTIVE (current status: {challenge.status})",
            )
        # Strip HR-only fields
        data = data.model_copy(update={"awarded_points": None, "feedback": None})

    result = await service.update(challenge_id, junior_id, data)

    # Notify HR when task is marked DONE
    if data.progress == ChallengeJuniorProgress.DONE:
        try:
            await push_notification(
                result.assigned_by,
                f"✅ HiPo выполнил задачу «{challenge.title}»",
                notification_service,
            )
        except Exception:
            pass

    return result


@router.delete("/{challenge_id}/{junior_id}", status_code=204)
async def delete(
    challenge_id: int,
    junior_id: int,
    service: ChallengeJuniorServiceDep,
    _: User = Depends(require_roles(UserRole.HR, UserRole.MENTOR)),
):
    await service.delete(challenge_id, junior_id)
