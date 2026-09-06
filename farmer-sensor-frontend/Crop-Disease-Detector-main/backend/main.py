"""Vani Network Intelligence - Premium Farmer Dashboard API."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.core.errors import VaniError
from app.db import init_db
from app.services.assistant_service import assistant_service
from app.services.claude_service import claude_service
from app.services.vision_service import vision_service
from app.utils.seed import seed_demo_reports

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("vani")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Clients are constructed once at startup, never per request.
    vision_service.load()
    claude_service.load()
    assistant_service.load()
    seed_demo_reports()
    logger.info("Vani backend ready.")
    yield


app = FastAPI(
    title="Vani Network Intelligence API",
    description="Premium Farmer Dashboard: crop disease detection and AI agricultural assistant.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(VaniError)
async def vani_error_handler(_: Request, exc: VaniError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(RequestValidationError)
async def validation_handler(_: Request, exc: RequestValidationError):
    logger.info("Validation error: %s", exc.errors())
    return JSONResponse(
        status_code=422,
        content={"detail": "That request looked incomplete. Please try again."},
    )


@app.exception_handler(Exception)
async def unhandled_handler(_: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on our side. Please try again."},
    )


app.include_router(api_router)
app.mount("/media", StaticFiles(directory=settings.upload_dir), name="media")


@app.get("/")
def root():
    return {"service": "Vani Network Intelligence", "docs": "/docs"}
