from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.repositories.challenge_employee_repository import ChallengeEmployeeRepository
from app.repositories.challenge_repository import ChallengeRepository
from app.repositories.mentor_employee_repository import MentorEmployeeRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.repositories.calendar_event_repository import CalendarEventRepository
from app.repositories.achievement_repository import AchievementRepository
from app.repositories.user_achievement_repository import UserAchievementRepository
from app.repositories.user_points_repository import UserPointsRepository
from app.repositories.activity_repository import ActivityRepository
from app.repositories.team_repository import TeamRepository
from app.repositories.quiz_repository import QuizRepository
from app.repositories.quiz_result_repository import QuizResultRepository
from app.repositories.kb_repository import KBSectionRepository, KBArticleRepository
from app.repositories.meeting_attendance_repository import MeetingAttendanceRepository
from app.repositories.push_subscription_repository import PushSubscriptionRepository

from app.services.challenge_employee_service import ChallengeEmployeeService
from app.services.challenge_service import ChallengeService
from app.services.mentor_employee_service import MentorEmployeeService
from app.services.notification_service import NotificationService
from app.services.user_service import UserService
from app.services.calendar_event_service import CalendarEventService
from app.services.achievement_service import AchievementService
from app.services.user_achievement_service import UserAchievementService
from app.services.user_points_service import UserPointsService
from app.services.activity_service import ActivityService
from app.services.team_service import TeamService
from app.services.quiz_service import QuizService
from app.services.quiz_result_service import QuizResultService
from app.services.kb_service import KBSectionService, KBArticleService
from app.services.meeting_attendance_service import MeetingAttendanceService
from app.services.push_service import PushService


async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_user_service(session: SessionDep) -> UserService:
    return UserService(UserRepository(session))


def get_mentor_employee_service(session: SessionDep) -> MentorEmployeeService:
    return MentorEmployeeService(MentorEmployeeRepository(session))


def get_notification_service(session: SessionDep) -> NotificationService:
    return NotificationService(NotificationRepository(session))


def get_challenge_service(session: SessionDep) -> ChallengeService:
    return ChallengeService(ChallengeRepository(session))


def get_challenge_employee_service(session: SessionDep) -> ChallengeEmployeeService:
    return ChallengeEmployeeService(ChallengeEmployeeRepository(session), UserPointsRepository(session))


def get_calendar_event_service(session: SessionDep) -> CalendarEventService:
    return CalendarEventService(CalendarEventRepository(session))


def get_achievement_service(session: SessionDep) -> AchievementService:
    return AchievementService(AchievementRepository(session))


def get_user_achievement_service(session: SessionDep) -> UserAchievementService:
    return UserAchievementService(
        UserAchievementRepository(session),
        AchievementRepository(session),
        UserPointsRepository(session),
    )


def get_user_points_service(session: SessionDep) -> UserPointsService:
    return UserPointsService(UserPointsRepository(session))


def get_activity_service(session: SessionDep) -> ActivityService:
    return ActivityService(ActivityRepository(session), UserPointsRepository(session))


def get_team_service(session: SessionDep) -> TeamService:
    return TeamService(TeamRepository(session))


def get_quiz_service(session: SessionDep) -> QuizService:
    return QuizService(QuizRepository(session))


def get_quiz_result_service(session: SessionDep) -> QuizResultService:
    return QuizResultService(QuizResultRepository(session), UserPointsRepository(session))


def get_kb_section_service(session: SessionDep) -> KBSectionService:
    return KBSectionService(KBSectionRepository(session))


def get_kb_article_service(session: SessionDep) -> KBArticleService:
    return KBArticleService(KBArticleRepository(session))


def get_meeting_attendance_service(session: SessionDep) -> MeetingAttendanceService:
    return MeetingAttendanceService(MeetingAttendanceRepository(session))


def get_push_service(session: SessionDep) -> PushService:
    return PushService(PushSubscriptionRepository(session))


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
MentorEmployeeServiceDep = Annotated[MentorEmployeeService, Depends(get_mentor_employee_service)]
NotificationServiceDep = Annotated[NotificationService, Depends(get_notification_service)]
ChallengeServiceDep = Annotated[ChallengeService, Depends(get_challenge_service)]
ChallengeEmployeeServiceDep = Annotated[ChallengeEmployeeService, Depends(get_challenge_employee_service)]
CalendarEventServiceDep = Annotated[CalendarEventService, Depends(get_calendar_event_service)]
AchievementServiceDep = Annotated[AchievementService, Depends(get_achievement_service)]
UserAchievementServiceDep = Annotated[UserAchievementService, Depends(get_user_achievement_service)]
UserPointsServiceDep = Annotated[UserPointsService, Depends(get_user_points_service)]
ActivityServiceDep = Annotated[ActivityService, Depends(get_activity_service)]
TeamServiceDep = Annotated[TeamService, Depends(get_team_service)]
QuizServiceDep = Annotated[QuizService, Depends(get_quiz_service)]
QuizResultServiceDep = Annotated[QuizResultService, Depends(get_quiz_result_service)]
KBSectionServiceDep = Annotated[KBSectionService, Depends(get_kb_section_service)]
KBArticleServiceDep = Annotated[KBArticleService, Depends(get_kb_article_service)]
MeetingAttendanceServiceDep = Annotated[MeetingAttendanceService, Depends(get_meeting_attendance_service)]
PushServiceDep = Annotated[PushService, Depends(get_push_service)]
