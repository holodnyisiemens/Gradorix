from app.repositories.challenge_repository import ChallengeRepository
from app.schemas.challenge import ChallengeCreateDTO, ChallengeUpdateDTO


class TestChallengeRepository:
    async def test_create_challenges(self, challenges: list[ChallengeCreateDTO], challenge_repository: ChallengeRepository):
        challenge = await challenge_repository.create(challenges[0])

        assert challenge.id is not None
        assert challenge.title  == challenges[0].title
        assert challenge.description == challenges[0].description
        assert challenge.url == challenges[0].url
        assert challenge.status == challenges[0].status

    async def test_delete_challenge(self, challenges: list[ChallengeCreateDTO], challenge_repository: ChallengeRepository):
        challenge = await challenge_repository.create(challenges[0])
        await challenge_repository.delete(challenge)

        found_challenge = await challenge_repository.get_by_id(challenge.id)
        assert found_challenge is None

    async def test_update_challenge(self, challenges: list[ChallengeCreateDTO], challenge_repository: ChallengeRepository):
        challenge = await challenge_repository.create(challenges[0])

        new_challenge_data = ChallengeUpdateDTO(title="Updated")

        await challenge_repository.update(challenge, new_challenge_data)
        updated_challenge = await challenge_repository.get_by_id(challenge.id)

        assert updated_challenge.title == new_challenge_data.title

        assert updated_challenge.id == challenge.id
        assert updated_challenge.description == challenges[0].description
        assert updated_challenge.url == challenges[0].url
        assert updated_challenge.status == challenges[0].status

    async def test_get_all(self, challenges: list[ChallengeCreateDTO], challenge_repository: ChallengeRepository):
        await challenge_repository.create(challenges[0])
        await challenge_repository.create(challenges[1])

        challenges_list = await challenge_repository.get_all()

        challenge_messages = [challenge.title for challenge in challenges_list]

        assert len(challenges_list) == 2
        assert set(challenge_messages) == {challenges[0].title, challenges[1].title}
