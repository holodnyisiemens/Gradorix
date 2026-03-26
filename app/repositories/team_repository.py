from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Team
from app.models.team_member import TeamMember
from app.schemas.team import TeamCreateDTO, TeamUpdateDTO


class TeamRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, team_id: int) -> Optional[Team]:
        return await self.session.get(Team, team_id)

    async def create(self, data: TeamCreateDTO) -> tuple[Team, list[int]]:
        member_ids = data.member_ids
        team = Team(
            name=data.name,
            project=data.project,
            status=data.status,
            mentor_id=data.mentor_id,
            description=data.description,
        )
        self.session.add(team)
        await self.session.flush()

        for user_id in member_ids:
            self.session.add(TeamMember(team_id=team.id, user_id=user_id))
        await self.session.flush()
        await self.session.refresh(team)

        return team, member_ids

    async def delete(self, team: Team) -> None:
        await self.session.delete(team)
        await self.session.flush()

    async def update(self, team: Team, data: TeamUpdateDTO) -> tuple[Team, list[int]]:
        update_data = data.model_dump(exclude_unset=True)
        member_ids = update_data.pop("member_ids", None)

        for field, value in update_data.items():
            setattr(team, field, value)

        if member_ids is not None:
            # Заменяем участников
            stmt = select(TeamMember).where(TeamMember.team_id == team.id)
            result = await self.session.execute(stmt)
            for existing in result.scalars().all():
                await self.session.delete(existing)
            await self.session.flush()

            for user_id in member_ids:
                self.session.add(TeamMember(team_id=team.id, user_id=user_id))
        else:
            member_ids = await self.get_member_ids(team.id)

        await self.session.flush()
        await self.session.refresh(team)
        return team, member_ids

    async def get_member_ids(self, team_id: int) -> list[int]:
        stmt = select(TeamMember.user_id).where(TeamMember.team_id == team_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all(self, mentor_id: Optional[int] = None) -> list[Team]:
        stmt = select(Team)
        if mentor_id is not None:
            stmt = stmt.where(Team.mentor_id == mentor_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
