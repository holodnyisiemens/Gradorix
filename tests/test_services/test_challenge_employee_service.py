import pytest
from fastapi import HTTPException

from app.core.enums import UserRole, ChallengeEmployeeProgress
from app.repositories.challenge_repository import ChallengeRepository
from app.repositories.user_repository import UserRepository
from app.schemas.challenge import ChallengeCreateDTO
from app.schemas.challenge_employee import ChallengeEmployeeCreateDTO, ChallengeEmployeeUpdateDTO
from app.schemas.user import UserCreateDTO
from app.services.challenge_employee_service import ChallengeEmployeeService


def _employee_dto(n: int) -> UserCreateDTO:
    return UserCreateDTO(username=f"employee{n}", password="123456", role=UserRole.EMPLOYEE)


class TestChallengeEmployeeService:
    async def _setup(
        self,
        user_repository: UserRepository,
        challenge_repository: ChallengeRepository,
        challenges: list[ChallengeCreateDTO],
    ):
        employee = await user_repository.create(_employee_dto(1))
        hr = await user_repository.create(
            UserCreateDTO(username="hr1", password="123456", role=UserRole.HR)
        )
        challenge = await challenge_repository.create(challenges[0])
        return challenge, employee, hr

    async def test_create(
        self,
        challenges: list[ChallengeCreateDTO],
        user_repository: UserRepository,
        challenge_repository: ChallengeRepository,
        challenge_employee_service: ChallengeEmployeeService,
    ):
        challenge, employee, hr = await self._setup(user_repository, challenge_repository, challenges)

        data = ChallengeEmployeeCreateDTO(
            challenge_id=challenge.id,
            employee_id=employee.id,
            assigned_by=hr.id,
            progress=ChallengeEmployeeProgress.GOING,
        )
        dto = await challenge_employee_service.create(data)

        assert dto.challenge_id == challenge.id
        assert dto.employee_id == employee.id
        assert dto.assigned_by == hr.id
        assert dto.progress == ChallengeEmployeeProgress.GOING

    async def test_create_duplicate(
        self,
        challenges: list[ChallengeCreateDTO],
        user_repository: UserRepository,
        challenge_repository: ChallengeRepository,
        challenge_employee_service: ChallengeEmployeeService,
    ):
        challenge, employee, hr = await self._setup(user_repository, challenge_repository, challenges)

        data = ChallengeEmployeeCreateDTO(
            challenge_id=challenge.id,
            employee_id=employee.id,
            assigned_by=hr.id,
            progress=ChallengeEmployeeProgress.GOING,
        )
        await challenge_employee_service.create(data)

        with pytest.raises(HTTPException) as exc_info:
            await challenge_employee_service.create(data)

        assert exc_info.value.status_code == 409

    async def test_get_by_id(
        self,
        challenges: list[ChallengeCreateDTO],
        user_repository: UserRepository,
        challenge_repository: ChallengeRepository,
        challenge_employee_service: ChallengeEmployeeService,
    ):
        challenge, employee, hr = await self._setup(user_repository, challenge_repository, challenges)

        data = ChallengeEmployeeCreateDTO(
            challenge_id=challenge.id,
            employee_id=employee.id,
            assigned_by=hr.id,
            progress=ChallengeEmployeeProgress.GOING,
        )
        await challenge_employee_service.create(data)

        dto = await challenge_employee_service.get_by_id(challenge.id, employee.id)

        assert dto.challenge_id == challenge.id
        assert dto.employee_id == employee.id

    async def test_get_by_id_not_found(self, challenge_employee_service: ChallengeEmployeeService):
        with pytest.raises(HTTPException) as exc_info:
            await challenge_employee_service.get_by_id(999, 999)

        assert exc_info.value.status_code == 404

    async def test_delete(
        self,
        challenges: list[ChallengeCreateDTO],
        user_repository: UserRepository,
        challenge_repository: ChallengeRepository,
        challenge_employee_service: ChallengeEmployeeService,
    ):
        challenge, employee, hr = await self._setup(user_repository, challenge_repository, challenges)

        data = ChallengeEmployeeCreateDTO(
            challenge_id=challenge.id,
            employee_id=employee.id,
            assigned_by=hr.id,
            progress=ChallengeEmployeeProgress.GOING,
        )
        await challenge_employee_service.create(data)
        await challenge_employee_service.delete(challenge.id, employee.id)

        with pytest.raises(HTTPException) as exc_info:
            await challenge_employee_service.get_by_id(challenge.id, employee.id)

        assert exc_info.value.status_code == 404

    async def test_delete_not_found(self, challenge_employee_service: ChallengeEmployeeService):
        with pytest.raises(HTTPException) as exc_info:
            await challenge_employee_service.delete(999, 999)

        assert exc_info.value.status_code == 404

    async def test_update(
        self,
        challenges: list[ChallengeCreateDTO],
        user_repository: UserRepository,
        challenge_repository: ChallengeRepository,
        challenge_employee_service: ChallengeEmployeeService,
    ):
        challenge, employee, hr = await self._setup(user_repository, challenge_repository, challenges)

        data = ChallengeEmployeeCreateDTO(
            challenge_id=challenge.id,
            employee_id=employee.id,
            assigned_by=hr.id,
            progress=ChallengeEmployeeProgress.GOING,
        )
        await challenge_employee_service.create(data)

        update_data = ChallengeEmployeeUpdateDTO(progress=ChallengeEmployeeProgress.DONE)
        dto = await challenge_employee_service.update(challenge.id, employee.id, update_data)

        assert dto.progress == ChallengeEmployeeProgress.DONE
        assert dto.challenge_id == challenge.id
        assert dto.employee_id == employee.id
        assert dto.assigned_by == hr.id

    async def test_update_not_found(self, challenge_employee_service: ChallengeEmployeeService):
        with pytest.raises(HTTPException) as exc_info:
            await challenge_employee_service.update(
                999, 999, ChallengeEmployeeUpdateDTO(progress=ChallengeEmployeeProgress.DONE)
            )

        assert exc_info.value.status_code == 404

    async def test_get_all(
        self,
        challenges: list[ChallengeCreateDTO],
        user_repository: UserRepository,
        challenge_repository: ChallengeRepository,
        challenge_employee_service: ChallengeEmployeeService,
    ):
        challenge, employee, hr = await self._setup(user_repository, challenge_repository, challenges)
        employee2 = await user_repository.create(_employee_dto(2))

        await challenge_employee_service.create(
            ChallengeEmployeeCreateDTO(
                challenge_id=challenge.id, employee_id=employee.id,
                assigned_by=hr.id, progress=ChallengeEmployeeProgress.GOING,
            )
        )
        await challenge_employee_service.create(
            ChallengeEmployeeCreateDTO(
                challenge_id=challenge.id, employee_id=employee2.id,
                assigned_by=hr.id, progress=ChallengeEmployeeProgress.IN_PROGRESS,
            )
        )

        result = await challenge_employee_service.get_all()

        assert len(result) == 2
        employee_ids = {dto.employee_id for dto in result}
        assert employee_ids == {employee.id, employee2.id}
