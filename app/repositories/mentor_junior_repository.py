from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mentor_junior import MentorJunior
from app.schemas.mentor_junior import MentorJuniorCreateDTO, MentorJuniorUpdateDTO


class MentorJuniorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, mentor_id: int, junior_id: int) -> Optional[MentorJunior]:
        return await self.session.get(MentorJunior, (mentor_id, junior_id))

    async def create(self, mentor_junior_data: MentorJuniorCreateDTO) -> MentorJunior:
        mentor_junior = MentorJunior(**mentor_junior_data.model_dump())
        self.session.add(mentor_junior)

        await self.session.flush()
        await self.session.refresh(mentor_junior)

        return mentor_junior

    async def delete(self, mentor_junior: MentorJunior) -> None:
        await self.session.delete(mentor_junior)
        await self.session.flush()

    async def update(self, mentor_junior: MentorJunior, mentor_junior_data: MentorJuniorUpdateDTO) -> MentorJunior:
        update_data = mentor_junior_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(mentor_junior, field, value)

        await self.session.flush()
        await self.session.refresh(mentor_junior)

        return mentor_junior

    async def get_all(self) -> list[MentorJunior]:
        stmt = select(MentorJunior)
        result = await self.session.execute(stmt)
        return result.scalars().all()
