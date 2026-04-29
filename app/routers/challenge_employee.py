from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from starlette import status as http_status

from app.auth.utils import get_current_user, require_roles
from app.core.enums import ChallengeEmployeeProgress, ChallengeStatus, UserRole
from app.dependencies import ChallengeEmployeeServiceDep, ChallengeServiceDep, NotificationServiceDep, PushServiceDep
from app.models.user import User
from app.schemas.challenge_employee import ChallengeEmployeeCreateDTO, ChallengeEmployeeReadDTO, ChallengeEmployeeUpdateDTO
from app.ws.notify import push_notification

router = APIRouter(prefix="/challenge-employee", tags=["Challenge-Employee"])


@router.get("/", response_model=list[ChallengeEmployeeReadDTO])
async def get_all(
    employee_id: Optional[int] = None,
    assigned_by: Optional[int] = None,
    service: ChallengeEmployeeServiceDep = ...,
    _: User = Depends(get_current_user),
):
    return await service.get_all(employee_id=employee_id, assigned_by=assigned_by)


@router.get("/{challenge_id}/{employee_id}", response_model=ChallengeEmployeeReadDTO)
async def get_by_id(
    challenge_id: int,
    employee_id: int,
    service: ChallengeEmployeeServiceDep,
    _: User = Depends(get_current_user),
):
    return await service.get_by_id(challenge_id, employee_id)


@router.post("/", response_model=ChallengeEmployeeReadDTO, status_code=201)
async def create(
    data: ChallengeEmployeeCreateDTO,
    service: ChallengeEmployeeServiceDep,
    challenge_service: ChallengeServiceDep,
    notification_service: NotificationServiceDep,
    push_service: PushServiceDep,
    _: User = Depends(require_roles(UserRole.HR, UserRole.MENTOR)),
):
    result = await service.create(data)
    try:
        challenge = await challenge_service.get_by_id(data.challenge_id)
        await push_notification(
            data.employee_id,
            f"🎯 Вам назначена задача «{challenge.title}»",
            notification_service,
            push_service=push_service,
            link=f"/challenges/{data.challenge_id}",
        )
    except Exception:
        pass
    return result


@router.patch("/{challenge_id}/{employee_id}", response_model=ChallengeEmployeeReadDTO)
async def update(
    challenge_id: int,
    employee_id: int,
    data: ChallengeEmployeeUpdateDTO,
    service: ChallengeEmployeeServiceDep,
    challenge_service: ChallengeServiceDep,
    notification_service: NotificationServiceDep,
    push_service: PushServiceDep,
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.EMPLOYEE and current_user.id != employee_id:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="Forbidden")

    challenge = await challenge_service.get_by_id(challenge_id)

    if current_user.role == UserRole.EMPLOYEE:
        if challenge.status != ChallengeStatus.ACTIVE:
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail=f"Challenge is not ACTIVE (current status: {challenge.status})",
            )
        data = data.model_copy(update={"awarded_points": None, "feedback": None})

    result = await service.update(challenge_id, employee_id, data)

    if data.progress == ChallengeEmployeeProgress.DONE:
        try:
            employee_name = current_user.username
            await push_notification(
                result.assigned_by,
                f"📋 {employee_name} отправил задачу «{challenge.title}» на проверку",
                notification_service,
                push_service=push_service,
                link="/points",
            )
        except Exception:
            pass

    return result


@router.delete("/{challenge_id}/{employee_id}", status_code=204)
async def delete(
    challenge_id: int,
    employee_id: int,
    service: ChallengeEmployeeServiceDep,
    _: User = Depends(require_roles(UserRole.HR, UserRole.MENTOR)),
):
    await service.delete(challenge_id, employee_id)
