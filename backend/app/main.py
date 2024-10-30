import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.watchdog import start_watchdog

logger = logging.getLogger(__name__)


def custom_generate_unique_id(route: APIRoute) -> str:
    """ Generate unique id for a route"""
    return f"{route.tags[0]}-{route.name}"

@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """
    Start watchdog on start up.
    """
    threading.Thread(target=start_watchdog, daemon=True).start()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )



app.include_router(api_router, prefix=settings.API_V1_STR)
