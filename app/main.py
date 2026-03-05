from fastapi import FastAPI

from app.core.config import settings
from app.routers import users, mentor_junior, notifications, challenges, challenge_junior

app = FastAPI(title="Gradorix")

app.include_router(users.router)
app.include_router(mentor_junior.router)
app.include_router(notifications.router)
app.include_router(challenges.router)
app.include_router(challenge_junior.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app="app.main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
