from typing import Optional

from fastapi import APIRouter, Depends

from app.auth.utils import get_current_user, require_roles
from app.core.enums import UserRole
from app.dependencies import QuizResultServiceDep
from app.models.user import User
from app.schemas.quiz_result import QuizResultCreateDTO, QuizResultReadDTO, QuizResultUpdateDTO

router = APIRouter(prefix="/quiz-results", tags=["Quiz Results"])


@router.get("/", response_model=list[QuizResultReadDTO])
async def get_all(
    user_id: Optional[int] = None,
    quiz_id: Optional[int] = None,
    service: QuizResultServiceDep = ...,
    _: User = Depends(get_current_user),
):
    return await service.get_all(user_id=user_id, quiz_id=quiz_id)


@router.get("/{result_id}", response_model=QuizResultReadDTO)
async def get_by_id(
    result_id: int,
    service: QuizResultServiceDep = ...,
    _: User = Depends(get_current_user),
):
    return await service.get_by_id(result_id)


@router.post("/", response_model=QuizResultReadDTO, status_code=201)
async def create(
    data: QuizResultCreateDTO,
    service: QuizResultServiceDep = ...,
    _: User = Depends(get_current_user),
):
    return await service.create(data)


@router.patch("/{result_id}", response_model=QuizResultReadDTO)
async def update(
    result_id: int,
    data: QuizResultUpdateDTO,
    service: QuizResultServiceDep = ...,
    _: User = Depends(require_roles(UserRole.HR)),
):
    return await service.update(result_id, data)


@router.delete("/{result_id}", status_code=204)
async def delete(
    result_id: int,
    service: QuizResultServiceDep = ...,
    _: User = Depends(require_roles(UserRole.HR)),
):
    await service.delete(result_id)
