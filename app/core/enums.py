from enum import StrEnum

class UserRole(StrEnum):
    HR = "HR"
    MENTOR = "MENTOR"
    JUNIOR = "JUNIOR"


class ChallengeStatus(StrEnum):
    DRAFT = "DRAFT"
    UPCOMING = "UPCOMING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ChallengeJuniorProgress(StrEnum):
    GOING = "GOING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    SKIPPED = "SKIPPED"
