from annotated_types import MaxLen
from typing import Annotated, Optional

from app.schemas.base import BaseDTO


class NotificationCreateDTO(BaseDTO):
    user_id: int
    message: Annotated[str, MaxLen(1000)]
    is_read: bool = False


class NotificationReadDTO(BaseDTO):
    id: int
    user_id: int
    message: str
    is_read: bool


class NotificationUpdateDTO(BaseDTO):
    user_id: Optional[int] = None
    message: Optional[Annotated[str, MaxLen(1000)]] = None
    is_read: Optional[bool] = None
