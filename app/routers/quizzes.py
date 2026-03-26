from typing import Optional

from fastapi import APIRouter

from app.dependencies import QuizServiceDep
from app.schemas.quiz import QuizCreateDTO, QuizReadDTO, QuizUpdateDTO

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.get("/", response_model=list[QuizReadDTO])
async def get_all(available: Optional[bool] = None, service: QuizServiceDep = ...):
    return await service.get_all(available=available)


@router.get("/{quiz_id}", response_model=QuizReadDTO)
async def get_by_id(quiz_id: int, service: QuizServiceDep = ...):
    return await service.get_by_id(quiz_id)


@router.post("/", response_model=QuizReadDTO, status_code=201)
async def create(data: QuizCreateDTO, service: QuizServiceDep = ...):
    return await service.create(data)


@router.patch("/{quiz_id}", response_model=QuizReadDTO)
async def update(quiz_id: int, data: QuizUpdateDTO, service: QuizServiceDep = ...):
    return await service.update(quiz_id, data)


@router.delete("/{quiz_id}", status_code=204)
async def delete(quiz_id: int, service: QuizServiceDep = ...):
    await service.delete(quiz_id)
