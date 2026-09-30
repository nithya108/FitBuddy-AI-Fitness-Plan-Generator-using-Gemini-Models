from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import init_db
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Create SQLite tables when application starts.
    init_db()

    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "AI-powered personalized fitness plan generator "
        "using FastAPI, SQLite and Google Gemini."
    ),
    lifespan=lifespan
)


# Static files
app.mount(
    "/static",
    StaticFiles(
        directory=str(
            Path(__file__).resolve().parent.parent / "static"
        )
    ),
    name="static"
)


# Application routes
app.include_router(router)