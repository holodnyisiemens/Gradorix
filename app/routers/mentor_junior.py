from typing import Optional

from fastapi import APIRouter

from app.dependencies import MentorJuniorServiceDep
from app.schemas.mentor_junior import MentorJuniorCreateDTO, MentorJuniorReadDTO, MentorJuniorUpdateDTO

router = APIRouter(prefix="/mentor-junior", tags=["Mentor-Junior"])


@router.get("/", response_model=list[MentorJuniorReadDTO])
async def get_all(mentor_id: Optional[int] = None, junior_id: Optional[int] = None, service: MentorJuniorServiceDep = ...):
    return await service.get_all(mentor_id=mentor_id, junior_id=junior_id)


@router.get("/{mentor_id}/{junior_id}", response_model=MentorJuniorReadDTO)
async def get_by_id(mentor_id: int, junior_id: int, service: MentorJuniorServiceDep):
    return await service.get_by_id(mentor_id, junior_id)


@router.post("/", response_model=MentorJuniorReadDTO, status_code=201)
async def create(data: MentorJuniorCreateDTO, service: MentorJuniorServiceDep):
    return await service.create(data)


@router.patch("/{mentor_id}/{junior_id}", response_model=MentorJuniorReadDTO)
async def update(mentor_id: int, junior_id: int, data: MentorJuniorUpdateDTO, service: MentorJuniorServiceDep):
    return await service.update(mentor_id, junior_id, data)


@router.delete("/{mentor_id}/{junior_id}", status_code=204)
async def delete(mentor_id: int, junior_id: int, service: MentorJuniorServiceDep):
    await service.delete(mentor_id, junior_id)
