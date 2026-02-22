from enum import StrEnum

class UserRole(str, StrEnum):
    HR = "HR"
    MENTOR = "MENTOR"
    JUNIOR = "JUNIOR"
