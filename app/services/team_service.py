from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.models.team import Team
from app.repositories.team_repository import TeamRepository
from app.schemas.team import TeamCreateDTO, TeamReadDTO, TeamUpdateDTO


def _to_dto(team: Team, member_ids: list[int]) -> TeamReadDTO:
    return TeamReadDTO(
        id=team.id,
        name=team.name,
        project=team.project,
        status=team.status,
        mentor_id=team.mentor_id,
        description=team.description,
        member_ids=member_ids,
    )


class TeamService:
    def __init__(self, repo: TeamRepository):
        self.repo = repo

    async def _get_or_404(self, team_id: int) -> Team:
        obj = await self.repo.get_by_id(team_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Team {team_id} not found")
        return obj

    async def get_by_id(self, team_id: int) -> TeamReadDTO:
        team = await self._get_or_404(team_id)
        member_ids = await self.repo.get_member_ids(team_id)
        return _to_dto(team, member_ids)

    async def get_all(self, mentor_id: Optional[int] = None) -> list[TeamReadDTO]:
        teams = await self.repo.get_all(mentor_id=mentor_id)
        result = []
        for team in teams:
            member_ids = await self.repo.get_member_ids(team.id)
            result.append(_to_dto(team, member_ids))
        return result

    async def create(self, data: TeamCreateDTO) -> TeamReadDTO:
        try:
            team, member_ids = await self.repo.create(data)
            await self.repo.session.commit()
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Referenced user not found")
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Team creation error")
        return _to_dto(team, member_ids)

    async def update(self, team_id: int, data: TeamUpdateDTO) -> TeamReadDTO:
        await self._get_or_404(team_id)
        team = await self.repo.get_by_id(team_id)
        try:
            team, member_ids = await self.repo.update(team, data)
            await self.repo.session.commit()
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Referenced user not found")
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Team update error")
        return _to_dto(team, member_ids)

    async def delete(self, team_id: int) -> None:
        team = await self._get_or_404(team_id)
        try:
            await self.repo.delete(team)
            await self.repo.session.commit()
        except SQLAlchemyError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Team delete error")
