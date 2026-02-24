from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(title="Gradorix")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app="app.main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
