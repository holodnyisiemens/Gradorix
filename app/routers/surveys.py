from typing import Optional

from fastapi import APIRouter, Depends

from app.auth.utils import get_current_user, require_roles
from app.core.enums import UserRole
from app.dependencies import SurveyServiceDep
from app.models.user import User
from app.schemas.survey import SurveyCreateDTO, SurveyReadDTO, SurveyUpdateDTO

router = APIRouter(prefix="/surveys", tags=["Surveys"])


@router.get("/", response_model=list[SurveyReadDTO])
async def get_all(
    available: Optional[bool] = None,
    service: SurveyServiceDep = ...,
    user: User = Depends(get_current_user),
):
    exclude_completed = user.id if user.role == UserRole.EMPLOYEE else None
    return await service.get_all(available=available, exclude_completed_for_user_id=exclude_completed)


@router.get("/{survey_id}", response_model=SurveyReadDTO)
async def get_by_id(
    survey_id: int,
    service: SurveyServiceDep = ...,
    user: User = Depends(get_current_user),
):
    block_if_completed = user.role == UserRole.EMPLOYEE
    return await service.get_by_id(survey_id, user_id=user.id, block_if_completed=block_if_completed)


@router.post("/", response_model=SurveyReadDTO, status_code=201)
async def create(
    data: SurveyCreateDTO,
    service: SurveyServiceDep,
    _: User = Depends(require_roles(UserRole.HR)),
):
    return await service.create(data)


@router.patch("/{survey_id}", response_model=SurveyReadDTO)
async def update(
    survey_id: int,
    data: SurveyUpdateDTO,
    service: SurveyServiceDep = ...,
    _: User = Depends(require_roles(UserRole.HR)),
):
    return await service.update(survey_id, data)


@router.delete("/{survey_id}", status_code=204)
async def delete(
    survey_id: int,
    service: SurveyServiceDep = ...,
    _: User = Depends(require_roles(UserRole.HR)),
):
    await service.delete(survey_id)
