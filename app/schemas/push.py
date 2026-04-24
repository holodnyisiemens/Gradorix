from typing import Optional

from app.schemas.base import BaseDTO


class PushSubscriptionKeys(BaseDTO):
    p256dh: str
    auth: str


class PushSubscriptionInfo(BaseDTO):
    endpoint: str
    expirationTime: Optional[int] = None
    keys: PushSubscriptionKeys


class PushSubscribeDTO(BaseDTO):
    user_id: int
    subscription: PushSubscriptionInfo
