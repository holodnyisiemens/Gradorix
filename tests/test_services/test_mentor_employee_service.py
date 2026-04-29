import pytest
from fastapi import HTTPException

from app.core.enums import UserRole
from app.schemas.mentor_employee import MentorEmployeeCreateDTO, MentorEmployeeUpdateDTO
from app.schemas.user import UserCreateDTO
from app.services.mentor_employee_service import MentorEmployeeService
from app.repositories.user_repository import UserRepository


def _make_users() -> tuple[UserCreateDTO, UserCreateDTO, UserCreateDTO]:
    hr = UserCreateDTO(username="hr1", password="123456", role=UserRole.HR)
    mentor = UserCreateDTO(username="mentor1", password="123456", role=UserRole.MENTOR)
    employee = UserCreateDTO(username="employee1", password="123456", role=UserRole.EMPLOYEE)
    return hr, mentor, employee


class TestMentorEmployeeService:
    async def _setup_users(self, user_repository: UserRepository):
        hr, mentor, employee = _make_users()
        hr_user = await user_repository.create(hr)
        mentor_user = await user_repository.create(mentor)
        employee_user = await user_repository.create(employee)
        return hr_user, mentor_user, employee_user

    async def test_create(self, user_repository: UserRepository, mentor_employee_service: MentorEmployeeService):
        hr, mentor, employee = await self._setup_users(user_repository)

        data = MentorEmployeeCreateDTO(mentor_id=mentor.id, employee_id=employee.id, assigned_by=hr.id)
        dto = await mentor_employee_service.create(data)

        assert dto.mentor_id == mentor.id
        assert dto.employee_id == employee.id
        assert dto.assigned_by == hr.id

    async def test_create_duplicate(self, user_repository: UserRepository, mentor_employee_service: MentorEmployeeService):
        hr, mentor, employee = await self._setup_users(user_repository)

        data = MentorEmployeeCreateDTO(mentor_id=mentor.id, employee_id=employee.id, assigned_by=hr.id)
        await mentor_employee_service.create(data)

        with pytest.raises(HTTPException) as exc_info:
            await mentor_employee_service.create(data)

        assert exc_info.value.status_code == 409

    async def test_get_by_id(self, user_repository: UserRepository, mentor_employee_service: MentorEmployeeService):
        hr, mentor, employee = await self._setup_users(user_repository)

        data = MentorEmployeeCreateDTO(mentor_id=mentor.id, employee_id=employee.id, assigned_by=hr.id)
        await mentor_employee_service.create(data)

        dto = await mentor_employee_service.get_by_id(mentor.id, employee.id)

        assert dto.mentor_id == mentor.id
        assert dto.employee_id == employee.id

    async def test_get_by_id_not_found(self, mentor_employee_service: MentorEmployeeService):
        with pytest.raises(HTTPException) as exc_info:
            await mentor_employee_service.get_by_id(999, 999)

        assert exc_info.value.status_code == 404

    async def test_delete(self, user_repository: UserRepository, mentor_employee_service: MentorEmployeeService):
        hr, mentor, employee = await self._setup_users(user_repository)

        data = MentorEmployeeCreateDTO(mentor_id=mentor.id, employee_id=employee.id, assigned_by=hr.id)
        await mentor_employee_service.create(data)
        await mentor_employee_service.delete(mentor.id, employee.id)

        with pytest.raises(HTTPException) as exc_info:
            await mentor_employee_service.get_by_id(mentor.id, employee.id)

        assert exc_info.value.status_code == 404

    async def test_delete_not_found(self, mentor_employee_service: MentorEmployeeService):
        with pytest.raises(HTTPException) as exc_info:
            await mentor_employee_service.delete(999, 999)

        assert exc_info.value.status_code == 404

    async def test_update(self, user_repository: UserRepository, mentor_employee_service: MentorEmployeeService):
        hr, mentor, employee = await self._setup_users(user_repository)
        second_employee = await user_repository.create(
            UserCreateDTO(username="employee2", password="123456", role=UserRole.EMPLOYEE)
        )

        data = MentorEmployeeCreateDTO(mentor_id=mentor.id, employee_id=employee.id, assigned_by=hr.id)
        await mentor_employee_service.create(data)

        update_data = MentorEmployeeUpdateDTO(assigned_by=second_employee.id)
        dto = await mentor_employee_service.update(mentor.id, employee.id, update_data)

        assert dto.assigned_by == second_employee.id
        assert dto.mentor_id == mentor.id
        assert dto.employee_id == employee.id

    async def test_update_not_found(self, mentor_employee_service: MentorEmployeeService):
        with pytest.raises(HTTPException) as exc_info:
            await mentor_employee_service.update(999, 999, MentorEmployeeUpdateDTO(assigned_by=1))

        assert exc_info.value.status_code == 404

    async def test_get_all(self, user_repository: UserRepository, mentor_employee_service: MentorEmployeeService):
        hr, mentor, employee = await self._setup_users(user_repository)
        second_employee = await user_repository.create(
            UserCreateDTO(username="employee2", password="123456", role=UserRole.EMPLOYEE)
        )

        await mentor_employee_service.create(
            MentorEmployeeCreateDTO(mentor_id=mentor.id, employee_id=employee.id, assigned_by=hr.id)
        )
        await mentor_employee_service.create(
            MentorEmployeeCreateDTO(mentor_id=mentor.id, employee_id=second_employee.id, assigned_by=hr.id)
        )

        result = await mentor_employee_service.get_all()

        assert len(result) == 2
        employee_ids = {dto.employee_id for dto in result}
        assert employee_ids == {employee.id, second_employee.id}
