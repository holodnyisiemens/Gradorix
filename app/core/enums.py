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


class TaskStatus(StrEnum):
    DRAFT = "DRAFT"
    UPCOMING = "UPCOMING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    # PENDING = "pending"
    # APPROVED = "approved"
    # REJECTED = "rejected"
    # REVISION = "revision"


class EventStatus(StrEnum):
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CalendarEventType(StrEnum):
    CHALLENGE = "challenge"
    MEETING = "meeting"
    DEADLINE = "deadline"


class AchievementCategory(StrEnum):
    MILESTONE = "milestone"
    CHALLENGE = "challenge"
    STREAK = "streak"
    SOCIAL = "social"
    SPECIAL = "special"


class ActivityType(StrEnum):
    ACHIEVEMENT = "achievement"
    TASK = "task"
    TEST = "test"
    EVENT = "event"
    CUSTOM = "custom"


class TeamStatus(StrEnum):
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
