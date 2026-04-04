from typing import Optional

from fastapi import APIRouter

from app.dependencies import ChallengeServiceDep
from app.schemas.challenge import ChallengeCreateDTO, ChallengeReadDTO, ChallengeUpdateDTO
from app.core.enums import TaskStatus

router = APIRouter(prefix="/challenges", tags=["Challenges"])


@router.get("/", response_model=list[ChallengeReadDTO])
async def get_all(status: Optional[TaskStatus] = None, service: ChallengeServiceDep = ...):
    return await service.get_all(status=status)


@router.get("/{challenge_id}", response_model=ChallengeReadDTO)
async def get_by_id(challenge_id: int, service: ChallengeServiceDep = ...):
    return await service.get_by_id(challenge_id)


@router.post("/", response_model=ChallengeReadDTO, status_code=201)
async def create(data: ChallengeCreateDTO, service: ChallengeServiceDep = ...):
    return await service.create(data)


@router.patch("/{challenge_id}", response_model=ChallengeReadDTO)
async def update(challenge_id: int, data: ChallengeUpdateDTO, service: ChallengeServiceDep = ...):
    return await service.update(challenge_id, data)


@router.delete("/{challenge_id}", status_code=204)
async def delete(challenge_id: int, service: ChallengeServiceDep = ...):
    await service.delete(challenge_id)
