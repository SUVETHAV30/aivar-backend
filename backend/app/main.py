from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.routes.agents import router as agents_router
from app.api.routes.auth import router as auth_router
from app.api.routes.baseline import router as baseline_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.drift import router as drift_router
from app.api.routes.monitoring import router as monitoring_router
from app.api.routes.scenarios import router as scenarios_router
from app.api.routes.sessions import router as sessions_router
from app.api.routes.alerts import router as alerts_router
from app.core.config import settings
from app.database import Base, engine
from app.middleware.logging_middleware import LoggingMiddleware
from app.models import *  # noqa: F401,F403
from app.api.routes.debug import router as debug_router

from fastapi.exceptions import RequestValidationError
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.services.logging_service import logger

app = FastAPI(title=settings.app_name)
app.add_middleware(LoggingMiddleware)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(
        f"HTTPException: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        f"Validation Error: {exc.errors()}"
    )
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        f"Unhandled Exception: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
        }
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(agents_router)
app.include_router(scenarios_router)
app.include_router(baseline_router)
app.include_router(monitoring_router)
app.include_router(drift_router)
app.include_router(dashboard_router)
app.include_router(sessions_router)
app.include_router(alerts_router)

app.include_router(debug_router)
Base.metadata.create_all(bind=engine)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "AI Agent Behavioral Baseline Builder API"}
