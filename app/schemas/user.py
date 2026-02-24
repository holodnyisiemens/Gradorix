from annotated_types import MaxLen, MinLen
from typing import Annotated, Optional

from pydantic import EmailStr

from app.schemas.base import BaseDTO
from app.schemas.enums import UserRole


class UserCreateDTO(BaseDTO):
    username: Annotated[str, MinLen(3), MaxLen(30)]
    email: Annotated[EmailStr, MaxLen(255)]
    password: Annotated[str, MinLen(6), MaxLen(72)]
    role: UserRole

    firstname: Optional[Annotated[str, MinLen(2), MaxLen(30)]]
    lastname: Optional[Annotated[str, MinLen(2), MaxLen(30)]]
    is_active: Optional[bool]


class UserReadDTO(BaseDTO):
    id: int
    username: str
    email: EmailStr
    role: UserRole

    firstname: Optional[str]
    lastname: Optional[str]
    is_active: bool


class UserUpdateDTO(BaseDTO):
    username: Optional[Annotated[str, MinLen(3), MaxLen(30)]] = None
    email: Optional[Annotated[EmailStr, MaxLen(255)]] = None
    role: Optional[UserRole] = None

    firstname: Optional[Annotated[str, MinLen(2), MaxLen(30)]] = None
    lastname: Optional[Annotated[str, MinLen(2), MaxLen(30)]] = None
    is_active: Optional[bool] = None


class UserChangePasswordDTO(BaseDTO):
    old_password: Annotated[str, MinLen(6), MaxLen(72)]
    new_password: Annotated[str, MinLen(6), MaxLen(72)]
