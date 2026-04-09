from typing import Optional

from fastapi import APIRouter, Depends

from app.auth.utils import get_current_user, require_roles
from app.core.enums import UserRole
from app.dependencies import QuizServiceDep, UserServiceDep, NotificationServiceDep
from app.models.user import User
from app.schemas.quiz import QuizCreateDTO, QuizReadDTO, QuizUpdateDTO
from app.ws.notify import push_notification

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.get("/", response_model=list[QuizReadDTO])
async def get_all(
    available: Optional[bool] = None,
    service: QuizServiceDep = ...,
    _: User = Depends(get_current_user),
):
    return await service.get_all(available=available)


@router.get("/{quiz_id}", response_model=QuizReadDTO)
async def get_by_id(
    quiz_id: int,
    service: QuizServiceDep = ...,
    _: User = Depends(get_current_user),
):
    return await service.get_by_id(quiz_id)


@router.post("/", response_model=QuizReadDTO, status_code=201)
async def create(
    data: QuizCreateDTO,
    service: QuizServiceDep,
    user_service: UserServiceDep,
    notification_service: NotificationServiceDep,
    _: User = Depends(require_roles(UserRole.HR)),
):
    result = await service.create(data)

    try:
        juniors = await user_service.get_all_by_role(UserRole.JUNIOR)
        for junior in juniors:
            await push_notification(
                junior.id,
                f"📊 Доступен новый тест «{result.title}»",
                notification_service,
            )
    except Exception:
        pass

    return result


@router.patch("/{quiz_id}", response_model=QuizReadDTO)
async def update(
    quiz_id: int,
    data: QuizUpdateDTO,
    service: QuizServiceDep = ...,
    _: User = Depends(require_roles(UserRole.HR)),
):
    return await service.update(quiz_id, data)


@router.delete("/{quiz_id}", status_code=204)
async def delete(
    quiz_id: int,
    service: QuizServiceDep = ...,
    _: User = Depends(require_roles(UserRole.HR)),
):
    await service.delete(quiz_id)
