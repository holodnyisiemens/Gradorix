from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqladmin import Admin
from app.core.database import async_engine
from app.admin.auth import AdminAuth
from app.admin.admin import register_all_models

from app.core.config import settings
from app.routers import (
    users,
    mentor_employee,
    notifications,
    challenges,
    challenge_employee,
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
    auth,
    ws,
    push,
)
from app.minio.init_minio import init_bucket

app = FastAPI(title="Gradorix")

admin = Admin(app, async_engine, authentication_backend=AdminAuth(secret_key="очень-секретный-ключ"), title="Admin Panel", base_url="/admin")

register_all_models(admin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(mentor_employee.router)
app.include_router(notifications.router)
app.include_router(challenges.router)
app.include_router(challenge_employee.router)
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
app.include_router(ws.router)
app.include_router(push.router)


@app.on_event("startup")
def startup():
    init_bucket()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app="app.main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
