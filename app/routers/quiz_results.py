from typing import Optional

from fastapi import APIRouter

from app.dependencies import QuizResultServiceDep
from app.schemas.quiz_result import QuizResultCreateDTO, QuizResultReadDTO

router = APIRouter(prefix="/quiz-results", tags=["Quiz Results"])


@router.get("/", response_model=list[QuizResultReadDTO])
async def get_all(
    user_id: Optional[int] = None,
    quiz_id: Optional[int] = None,
    service: QuizResultServiceDep = ...,
):
    return await service.get_all(user_id=user_id, quiz_id=quiz_id)


@router.get("/{result_id}", response_model=QuizResultReadDTO)
async def get_by_id(result_id: int, service: QuizResultServiceDep = ...):
    return await service.get_by_id(result_id)


@router.post("/", response_model=QuizResultReadDTO, status_code=201)
async def create(data: QuizResultCreateDTO, service: QuizResultServiceDep = ...):
    return await service.create(data)


@router.delete("/{result_id}", status_code=204)
async def delete(result_id: int, service: QuizResultServiceDep = ...):
    await service.delete(result_id)
