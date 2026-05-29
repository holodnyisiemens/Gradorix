import datetime
from typing import Annotated, Optional

from annotated_types import MaxLen

from app.schemas.base import BaseDTO


class MentorChatMessageReadDTO(BaseDTO):
    id: str
    mentor_id: int
    employee_id: int
    sender_id: int
    body: str
    created_at: datetime.datetime


class MentorChatConversationDTO(BaseDTO):
    mentor_id: int
    employee_id: int
    peer_id: int
    last_message: Optional[MentorChatMessageReadDTO] = None
    unread_count: int = 0


class MentorChatSendDTO(BaseDTO):
    peer_id: int
    text: Annotated[str, MaxLen(4000)]
