import pytest
from fastapi import HTTPException

from app.core.enums import UserRole, ChallengeJuniorProgress
from app.repositories.challenge_repository import ChallengeRepository
from app.repositories.user_repository import UserRepository
from app.schemas.challenge import ChallengeCreateDTO
from app.schemas.challenge_junior import ChallengeJuniorCreateDTO, ChallengeJuniorUpdateDTO
from app.schemas.user import UserCreateDTO
from app.services.challenge_junior_service import ChallengeJuniorService


def _junior_dto(n: int) -> UserCreateDTO:
    return UserCreateDTO(
        username=f"junior{n}",
        email=f"junior{n}@example.com",
        password="123456",
        role=UserRole.JUNIOR,
    )


class TestChallengeJuniorService:
    async def _setup(
        self,
        user_repository: UserRepository,
        challenge_repository: ChallengeRepository,
        challenges: list[ChallengeCreateDTO],
    ):
        junior = await user_repository.create(_junior_dto(1))
        hr = await user_repository.create(
            UserCreateDTO(username="hr1", email="hr1@example.com", password="123456", role=UserRole.HR)
        )
        challenge = await challenge_repository.create(challenges[0])
        return challenge, junior, hr

    async def test_create(
        self,
        challenges: list[ChallengeCreateDTO],
        user_repository: UserRepository,
        challenge_repository: ChallengeRepository,
        challenge_junior_service: ChallengeJuniorService,
    ):
        challenge, junior, hr = await self._setup(user_repository, challenge_repository, challenges)

        data = ChallengeJuniorCreateDTO(
            challenge_id=challenge.id,
            junior_id=junior.id,
            assigned_by=hr.id,
            progress=ChallengeJuniorProgress.GOING,
        )
        dto = await challenge_junior_service.create(data)

        assert dto.challenge_id == challenge.id
        assert dto.junior_id == junior.id
        assert dto.assigned_by == hr.id
        assert dto.progress == ChallengeJuniorProgress.GOING

    async def test_create_duplicate(
        self,
        challenges: list[ChallengeCreateDTO],
        user_repository: UserRepository,
        challenge_repository: ChallengeRepository,
        challenge_junior_service: ChallengeJuniorService,
    ):
        challenge, junior, hr = await self._setup(user_repository, challenge_repository, challenges)

        data = ChallengeJuniorCreateDTO(
            challenge_id=challenge.id,
            junior_id=junior.id,
            assigned_by=hr.id,
            progress=ChallengeJuniorProgress.GOING,
        )
        await challenge_junior_service.create(data)

        with pytest.raises(HTTPException) as exc_info:
            await challenge_junior_service.create(data)

        assert exc_info.value.status_code == 409

    async def test_get_by_id(
        self,
        challenges: list[ChallengeCreateDTO],
        user_repository: UserRepository,
        challenge_repository: ChallengeRepository,
        challenge_junior_service: ChallengeJuniorService,
    ):
        challenge, junior, hr = await self._setup(user_repository, challenge_repository, challenges)

        data = ChallengeJuniorCreateDTO(
            challenge_id=challenge.id,
            junior_id=junior.id,
            assigned_by=hr.id,
            progress=ChallengeJuniorProgress.GOING,
        )
        await challenge_junior_service.create(data)

        dto = await challenge_junior_service.get_by_id(challenge.id, junior.id)

        assert dto.challenge_id == challenge.id
        assert dto.junior_id == junior.id

    async def test_get_by_id_not_found(self, challenge_junior_service: ChallengeJuniorService):
        with pytest.raises(HTTPException) as exc_info:
            await challenge_junior_service.get_by_id(999, 999)

        assert exc_info.value.status_code == 404

    async def test_delete(
        self,
        challenges: list[ChallengeCreateDTO],
        user_repository: UserRepository,
        challenge_repository: ChallengeRepository,
        challenge_junior_service: ChallengeJuniorService,
    ):
        challenge, junior, hr = await self._setup(user_repository, challenge_repository, challenges)

        data = ChallengeJuniorCreateDTO(
            challenge_id=challenge.id,
            junior_id=junior.id,
            assigned_by=hr.id,
            progress=ChallengeJuniorProgress.GOING,
        )
        await challenge_junior_service.create(data)

        await challenge_junior_service.delete(challenge.id, junior.id)

        with pytest.raises(HTTPException) as exc_info:
            await challenge_junior_service.get_by_id(challenge.id, junior.id)

        assert exc_info.value.status_code == 404

    async def test_delete_not_found(self, challenge_junior_service: ChallengeJuniorService):
        with pytest.raises(HTTPException) as exc_info:
            await challenge_junior_service.delete(999, 999)

        assert exc_info.value.status_code == 404

    async def test_update(
        self,
        challenges: list[ChallengeCreateDTO],
        user_repository: UserRepository,
        challenge_repository: ChallengeRepository,
        challenge_junior_service: ChallengeJuniorService,
    ):
        challenge, junior, hr = await self._setup(user_repository, challenge_repository, challenges)

        data = ChallengeJuniorCreateDTO(
            challenge_id=challenge.id,
            junior_id=junior.id,
            assigned_by=hr.id,
            progress=ChallengeJuniorProgress.GOING,
        )
        await challenge_junior_service.create(data)

        update_data = ChallengeJuniorUpdateDTO(progress=ChallengeJuniorProgress.DONE)
        dto = await challenge_junior_service.update(challenge.id, junior.id, update_data)

        assert dto.progress == ChallengeJuniorProgress.DONE
        assert dto.challenge_id == challenge.id
        assert dto.junior_id == junior.id
        assert dto.assigned_by == hr.id

    async def test_update_not_found(self, challenge_junior_service: ChallengeJuniorService):
        with pytest.raises(HTTPException) as exc_info:
            await challenge_junior_service.update(
                999, 999, ChallengeJuniorUpdateDTO(progress=ChallengeJuniorProgress.DONE)
            )

        assert exc_info.value.status_code == 404

    async def test_get_all(
        self,
        challenges: list[ChallengeCreateDTO],
        user_repository: UserRepository,
        challenge_repository: ChallengeRepository,
        challenge_junior_service: ChallengeJuniorService,
    ):
        challenge, junior, hr = await self._setup(user_repository, challenge_repository, challenges)
        junior2 = await user_repository.create(_junior_dto(2))

        await challenge_junior_service.create(
            ChallengeJuniorCreateDTO(
                challenge_id=challenge.id, junior_id=junior.id,
                assigned_by=hr.id, progress=ChallengeJuniorProgress.GOING,
            )
        )
        await challenge_junior_service.create(
            ChallengeJuniorCreateDTO(
                challenge_id=challenge.id, junior_id=junior2.id,
                assigned_by=hr.id, progress=ChallengeJuniorProgress.IN_PROGRESS,
            )
        )

        result = await challenge_junior_service.get_all()

        assert len(result) == 2
        junior_ids = {dto.junior_id for dto in result}
        assert junior_ids == {junior.id, junior2.id}
