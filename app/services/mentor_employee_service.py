from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette import status

from app.models.mentor_employee import MentorEmployee
from app.repositories.mentor_employee_repository import MentorEmployeeRepository
from app.schemas.mentor_employee import MentorEmployeeCreateDTO, MentorEmployeeReadDTO, MentorEmployeeUpdateDTO


class MentorEmployeeService:
    def __init__(self, mentor_employee_repo: MentorEmployeeRepository):
        self.mentor_employee_repo = mentor_employee_repo

    async def _get_or_404(self, mentor_id: int, employee_id: int) -> MentorEmployee:
        obj = await self.mentor_employee_repo.get_by_id(mentor_id, employee_id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"MentorEmployee with mentor_id={mentor_id} and employee_id={employee_id} not found",
            )
        return obj

    async def get_by_id(self, mentor_id: int, employee_id: int) -> MentorEmployeeReadDTO:
        obj = await self._get_or_404(mentor_id, employee_id)
        return MentorEmployeeReadDTO.model_validate(obj)

    async def create(self, data: MentorEmployeeCreateDTO) -> MentorEmployeeReadDTO:
        existing = await self.mentor_employee_repo.get_by_id(data.mentor_id, data.employee_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="MentorEmployee pair already exists",
            )
        try:
            obj = await self.mentor_employee_repo.create(data)
            await self.mentor_employee_repo.session.commit()
        except IntegrityError:
            await self.mentor_employee_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="MentorEmployee pair already exists or referenced user not found",
            )
        except SQLAlchemyError:
            await self.mentor_employee_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MentorEmployee creation error",
            )
        return MentorEmployeeReadDTO.model_validate(obj)

    async def delete(self, mentor_id: int, employee_id: int) -> None:
        obj = await self._get_or_404(mentor_id, employee_id)
        try:
            await self.mentor_employee_repo.delete(obj)
            await self.mentor_employee_repo.session.commit()
        except SQLAlchemyError:
            await self.mentor_employee_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MentorEmployee delete error",
            )

    async def update(
        self, mentor_id: int, employee_id: int, data: MentorEmployeeUpdateDTO
    ) -> MentorEmployeeReadDTO:
        obj = await self._get_or_404(mentor_id, employee_id)
        try:
            obj = await self.mentor_employee_repo.update(obj, data)
            await self.mentor_employee_repo.session.commit()
        except IntegrityError:
            await self.mentor_employee_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="MentorEmployee pair already exists or referenced user not found",
            )
        except SQLAlchemyError:
            await self.mentor_employee_repo.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MentorEmployee update error",
            )
        return MentorEmployeeReadDTO.model_validate(obj)

    async def get_all(self, mentor_id: Optional[int] = None, employee_id: Optional[int] = None) -> list[MentorEmployeeReadDTO]:
        pairs = await self.mentor_employee_repo.get_all(mentor_id=mentor_id, employee_id=employee_id)
        return [MentorEmployeeReadDTO.model_validate(p) for p in pairs]
