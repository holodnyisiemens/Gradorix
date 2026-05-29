from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.auth.utils import get_current_user
from app.dependencies import MentorChatServiceDep
from app.models.user import User
from app.schemas.mentor_chat import MentorChatConversationDTO, MentorChatMessageReadDTO

router = APIRouter(prefix="/mentor-chat", tags=["Mentor-Chat"])


@router.get("/conversations", response_model=list[MentorChatConversationDTO])
async def get_conversations(
    service: MentorChatServiceDep,
    current_user: User = Depends(get_current_user),
):
    return await service.get_conversations(current_user)


@router.get(
    "/{mentor_id}/{employee_id}/messages",
    response_model=list[MentorChatMessageReadDTO],
)
async def get_messages(
    mentor_id: int,
    employee_id: int,
    service: MentorChatServiceDep,
    limit: int = Query(50, ge=1, le=100),
    before_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    return await service.list_messages(
        current_user,
        mentor_id,
        employee_id,
        limit=limit,
        before_id=before_id,
    )


@router.post("/{mentor_id}/{employee_id}/read", status_code=204)
async def mark_read(
    mentor_id: int,
    employee_id: int,
    service: MentorChatServiceDep,
    current_user: User = Depends(get_current_user),
):
    await service.mark_read(current_user, mentor_id, employee_id)
