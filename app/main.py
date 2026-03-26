from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import (
    users,
    mentor_junior,
    notifications,
    challenges,
    challenge_junior,
    calendar_events,
    achievements,
    user_achievements,
    user_points,
    activities,
    teams,
    quizzes,
    quiz_results,
    kb,
    meeting_attendance,
    auth
)

app = FastAPI(title="Gradorix")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(mentor_junior.router)
app.include_router(notifications.router)
app.include_router(challenges.router)
app.include_router(challenge_junior.router)
app.include_router(calendar_events.router)
app.include_router(achievements.router)
app.include_router(user_achievements.router)
app.include_router(user_points.router)
app.include_router(activities.router)
app.include_router(teams.router)
app.include_router(quizzes.router)
app.include_router(quiz_results.router)
app.include_router(kb.router)
app.include_router(meeting_attendance.router)
app.include_router(auth.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app="app.main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
