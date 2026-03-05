import pytest
from fastapi import HTTPException

from app.schemas.challenge import ChallengeCreateDTO, ChallengeUpdateDTO
from app.services.challenge_service import ChallengeService


class TestChallengeService:
    async def test_create(self, challenges: list[ChallengeCreateDTO], challenge_service: ChallengeService):
        dto = await challenge_service.create(challenges[0])

        assert dto.id is not None
        assert dto.title == challenges[0].title
        assert dto.description == challenges[0].description
        assert dto.status == challenges[0].status

    async def test_get_by_id(self, challenges: list[ChallengeCreateDTO], challenge_service: ChallengeService):
        created = await challenge_service.create(challenges[0])

        dto = await challenge_service.get_by_id(created.id)

        assert dto.id == created.id
        assert dto.title == created.title
        assert dto.status == created.status

    async def test_get_by_id_not_found(self, challenge_service: ChallengeService):
        with pytest.raises(HTTPException) as exc_info:
            await challenge_service.get_by_id(999)

        assert exc_info.value.status_code == 404

    async def test_delete(self, challenges: list[ChallengeCreateDTO], challenge_service: ChallengeService):
        created = await challenge_service.create(challenges[0])

        await challenge_service.delete(created.id)

        with pytest.raises(HTTPException) as exc_info:
            await challenge_service.get_by_id(created.id)

        assert exc_info.value.status_code == 404

    async def test_delete_not_found(self, challenge_service: ChallengeService):
        with pytest.raises(HTTPException) as exc_info:
            await challenge_service.delete(999)

        assert exc_info.value.status_code == 404

    async def test_update(self, challenges: list[ChallengeCreateDTO], challenge_service: ChallengeService):
        created = await challenge_service.create(challenges[0])

        update_data = ChallengeUpdateDTO(title="Updated title", status="COMPLETED")
        dto = await challenge_service.update(created.id, update_data)

        assert dto.title == update_data.title
        assert dto.status == update_data.status
        assert dto.id == created.id
        assert dto.description == created.description

    async def test_update_not_found(self, challenge_service: ChallengeService):
        with pytest.raises(HTTPException) as exc_info:
            await challenge_service.update(999, ChallengeUpdateDTO(title="x"))

        assert exc_info.value.status_code == 404

    async def test_get_all(self, challenges: list[ChallengeCreateDTO], challenge_service: ChallengeService):
        await challenge_service.create(challenges[0])
        await challenge_service.create(challenges[1])

        result = await challenge_service.get_all()

        assert len(result) == 2
        titles = {dto.title for dto in result}
        assert titles == {challenges[0].title, challenges[1].title}
