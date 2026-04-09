from fastapi import APIRouter, Depends

from app.auth.utils import get_current_user, require_roles
from app.core.enums import UserRole
from app.dependencies import ChallengeServiceDep, ChallengeJuniorServiceDep
from app.models.user import User
from app.schemas.challenge import ChallengeCreateDTO, ChallengeReadDTO, ChallengeUpdateDTO

router = APIRouter(prefix="/challenges", tags=["Challenges"])


@router.get("/", response_model=list[ChallengeReadDTO])
async def get_all(
    service: ChallengeServiceDep,
    current_user: User = Depends(get_current_user),
):
    # JUNIOR doesn't see DRAFT challenges
    exclude_draft = current_user.role == UserRole.JUNIOR
    return await service.get_all(exclude_draft=exclude_draft)


@router.get("/{challenge_id}", response_model=ChallengeReadDTO)
async def get_by_id(
    challenge_id: int,
    service: ChallengeServiceDep,
    _: User = Depends(get_current_user),
):
    return await service.get_by_id(challenge_id)


@router.post("/", response_model=ChallengeReadDTO, status_code=201)
async def create(
    data: ChallengeCreateDTO,
    service: ChallengeServiceDep,
    _: User = Depends(require_roles(UserRole.HR)),
):
    return await service.create(data)


@router.patch("/{challenge_id}", response_model=ChallengeReadDTO)
async def update(
    challenge_id: int,
    data: ChallengeUpdateDTO,
    service: ChallengeServiceDep,
    cj_service: ChallengeJuniorServiceDep,
    _: User = Depends(require_roles(UserRole.HR)),
):
    return await service.update(challenge_id, data, challenge_junior_service=cj_service)


@router.delete("/{challenge_id}", status_code=204)
async def delete(
    challenge_id: int,
    service: ChallengeServiceDep,
    _: User = Depends(require_roles(UserRole.HR)),
):
    await service.delete(challenge_id)
