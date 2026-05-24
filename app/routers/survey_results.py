from typing import Optional

from fastapi import APIRouter, Depends

from app.auth.utils import get_current_user, require_roles
from app.core.enums import UserRole
from app.dependencies import SurveyResultServiceDep
from app.models.user import User
from app.schemas.survey_result import SurveyResultCreateDTO, SurveyResultReadDTO, SurveyResultUpdateDTO

router = APIRouter(prefix="/survey-results", tags=["Survey Results"])


@router.get("/", response_model=list[SurveyResultReadDTO])
async def get_all(
    user_id: Optional[int] = None,
    survey_id: Optional[int] = None,
    service: SurveyResultServiceDep = ...,
    _: User = Depends(get_current_user),
):
    return await service.get_all(user_id=user_id, survey_id=survey_id)


@router.get("/statistics")
async def get_statistics(
    survey_id: int,
    service: SurveyResultServiceDep = ...,
    _: User = Depends(get_current_user),
):
    return await service.get_statistics(survey_id)


@router.get("/{result_id}", response_model=SurveyResultReadDTO)
async def get_by_id(
    result_id: int,
    service: SurveyResultServiceDep = ...,
    _: User = Depends(get_current_user),
):
    return await service.get_by_id(result_id)


@router.post("/", response_model=SurveyResultReadDTO, status_code=201)
async def create(
    data: SurveyResultCreateDTO,
    service: SurveyResultServiceDep = ...,
    user: User = Depends(get_current_user),
):
    return await service.create(user.id, data)


@router.patch("/{result_id}", response_model=SurveyResultReadDTO)
async def update(
    result_id: int,
    data: SurveyResultUpdateDTO,
    service: SurveyResultServiceDep = ...,
    _: User = Depends(require_roles(UserRole.HR)),
):
    return await service.update(result_id, data)


@router.delete("/{result_id}", status_code=204)
async def delete(
    result_id: int,
    service: SurveyResultServiceDep = ...,
    _: User = Depends(require_roles(UserRole.HR)),
):
    await service.delete(result_id)
