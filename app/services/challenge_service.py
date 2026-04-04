from typing import Optional

from fastapi import HTTPException
from starlette import status

from app.repositories.activity_repository import ActivityRepository
from app.repositories.user_points_repository import UserPointsRepository
from app.schemas.activity import ActivityCreateDTO, ActivityUpdateDTO
from app.schemas.challenge import ChallengeCreateDTO, ChallengeReadDTO, ChallengeUpdateDTO
from app.services.activity_service import ActivityService
from app.core.enums import ActivityType, TaskStatus


class ChallengeService:
    def __init__(self, activity_repo: ActivityRepository, points_repo: UserPointsRepository):
        self.activity_service = ActivityService(activity_repo, points_repo)

    async def _get_or_404(self, challenge_id: int):
        challenge = await self.activity_service.repo.get_by_id(challenge_id)
        if not challenge or challenge.activity_type != ActivityType.TASK:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Challenge with ID {challenge_id} not found")
        return challenge

    def _to_challenge(self, activity) -> ChallengeReadDTO:
        return ChallengeReadDTO(
            id=activity.id,
            title=activity.title,
            description=activity.description,
            url=activity.url,
            status=activity.task_status,
            date=activity.date,
        )

    async def get_by_id(self, challenge_id: int) -> ChallengeReadDTO:
        challenge = await self._get_or_404(challenge_id)
        return self._to_challenge(challenge)

    async def create(self, data: ChallengeCreateDTO) -> ChallengeReadDTO:
        activity_data = ActivityCreateDTO(
            title=data.title,
            description=data.description or "",
            activity_type=ActivityType.TASK,
            task_status=data.status,
            date=data.date,
            url=data.url,
        )
        activity = await self.activity_service.create(activity_data)
        return self._to_challenge(activity)

    async def delete(self, challenge_id: int) -> None:
        await self.activity_service.delete(challenge_id)

    async def update(self, challenge_id: int, data: ChallengeUpdateDTO) -> ChallengeReadDTO:
        update_payload = data.model_dump(exclude_unset=True)
        if "status" in update_payload:
            update_payload["task_status"] = update_payload.pop("status")

        activity_data = ActivityUpdateDTO(**update_payload, activity_type=ActivityType.TASK)
        activity = await self.activity_service.update(challenge_id, activity_data)
        return self._to_challenge(activity)

    async def get_all(self, status: Optional[TaskStatus] = None) -> list[ChallengeReadDTO]:
        activities = await self.activity_service.repo.get_all(
            activity_type=ActivityType.TASK,
            task_status=status,
        )
        return [self._to_challenge(activity) for activity in activities]
