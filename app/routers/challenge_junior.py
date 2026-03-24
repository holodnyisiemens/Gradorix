from typing import Optional

from fastapi import APIRouter

from app.dependencies import ChallengeJuniorServiceDep
from app.schemas.challenge_junior import ChallengeJuniorCreateDTO, ChallengeJuniorReadDTO, ChallengeJuniorUpdateDTO

router = APIRouter(prefix="/challenge-junior", tags=["Challenge-Junior"])


@router.get("/", response_model=list[ChallengeJuniorReadDTO])
async def get_all(junior_id: Optional[int] = None, assigned_by: Optional[int] = None, service: ChallengeJuniorServiceDep = ...):
    return await service.get_all(junior_id=junior_id, assigned_by=assigned_by)


@router.get("/{challenge_id}/{junior_id}", response_model=ChallengeJuniorReadDTO)
async def get_by_id(challenge_id: int, junior_id: int, service: ChallengeJuniorServiceDep):
    return await service.get_by_id(challenge_id, junior_id)


@router.post("/", response_model=ChallengeJuniorReadDTO, status_code=201)
async def create(data: ChallengeJuniorCreateDTO, service: ChallengeJuniorServiceDep):
    return await service.create(data)


@router.patch("/{challenge_id}/{junior_id}", response_model=ChallengeJuniorReadDTO)
async def update(challenge_id: int, junior_id: int, data: ChallengeJuniorUpdateDTO, service: ChallengeJuniorServiceDep):
    return await service.update(challenge_id, junior_id, data)


@router.delete("/{challenge_id}/{junior_id}", status_code=204)
async def delete(challenge_id: int, junior_id: int, service: ChallengeJuniorServiceDep):
    await service.delete(challenge_id, junior_id)
