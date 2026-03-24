from typing import Optional

from fastapi import APIRouter

from app.dependencies import TeamServiceDep
from app.schemas.team import TeamCreateDTO, TeamReadDTO, TeamUpdateDTO

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("/", response_model=list[TeamReadDTO])
async def get_all(mentor_id: Optional[int] = None, service: TeamServiceDep = ...):
    return await service.get_all(mentor_id=mentor_id)


@router.get("/{team_id}", response_model=TeamReadDTO)
async def get_by_id(team_id: int, service: TeamServiceDep = ...):
    return await service.get_by_id(team_id)


@router.post("/", response_model=TeamReadDTO, status_code=201)
async def create(data: TeamCreateDTO, service: TeamServiceDep = ...):
    return await service.create(data)


@router.patch("/{team_id}", response_model=TeamReadDTO)
async def update(team_id: int, data: TeamUpdateDTO, service: TeamServiceDep = ...):
    return await service.update(team_id, data)


@router.delete("/{team_id}", status_code=204)
async def delete(team_id: int, service: TeamServiceDep = ...):
    await service.delete(team_id)
