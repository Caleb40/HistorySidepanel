import logging
from collections.abc import AsyncGenerator, Callable
from contextlib import _AsyncGeneratorContextManager, asynccontextmanager  # noqa
from typing import Any

import anyio
import fastapi
from fastapi import APIRouter
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasic
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError
from starlette.requests import Request
from starlette.responses import JSONResponse

from .exceptions import DatabaseError, NotFoundError, ValidationError
from .exceptions.http_exceptions import CustomApplicationException

security = HTTPBasic()

from .config import (
    AppSettings,
    DatabaseSettings,
    EnvironmentOption,
    EnvironmentSettings,
)
from .db.database import Base, async_engine as engine


# -------------- database --------------
async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# -------------- application --------------
async def set_threadpool_tokens(number_of_tokens: int = 100) -> None:
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = number_of_tokens


def lifespan_factory(
        settings: (
                DatabaseSettings
                | AppSettings
                | EnvironmentSettings
        ),
        create_tables_on_start: bool = True,
) -> Callable[[FastAPI], _AsyncGeneratorContextManager[Any]]:
    """Factory to create a lifespan async context manager for a FastAPI app."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        await set_threadpool_tokens()

        if isinstance(settings, DatabaseSettings) and create_tables_on_start:
            await create_tables()

        yield

    return lifespan


# -------------- Exception Handlers --------------
def setup_exception_handlers(application: FastAPI, settings: Any) -> None:
    """Setup all exception handlers with consistent response format"""

    @application.exception_handler(CustomApplicationException)
    async def custom_application_exception_handler(
            request: Request, exc: CustomApplicationException
    ) -> JSONResponse:
        """Handle custom application exceptions"""
        # Log with appropriate level based on status code
        if exc.status_code >= 500:
            logging.error(f"CustomApplicationException {exc.status_code}: {exc.detail}", exc_info=True)
        else:
            logging.warning(f"CustomApplicationException {exc.status_code}: {exc.detail}")

        error_name = "server_error" if exc.status_code >= 500 else "request_error"

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": (
                    error_name
                    if settings.ENVIRONMENT == EnvironmentOption.PRODUCTION
                    else getattr(exc, "error", type(exc).__name__)
                ),
                "message": (
                    exc.detail
                    if exc.status_code < 500 or settings.ENVIRONMENT != EnvironmentOption.PRODUCTION
                    else "An unexpected error occurred. Please try again later."
                ),
                "status_code": exc.status_code,
                "data": exc.data,
            },
        )

    @application.exception_handler(DatabaseError)
    async def database_error_handler(
            request: Request, exc: DatabaseError
    ) -> JSONResponse:
        """Handle database operation errors"""
        logging.error(f"DatabaseError: {exc.message}", exc_info=True)

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": (
                    "database_error"
                    if settings.ENVIRONMENT == EnvironmentOption.PRODUCTION
                    else type(exc).__name__
                ),
                "message": (
                    "A database error occurred. Please try again later."
                    if settings.ENVIRONMENT == EnvironmentOption.PRODUCTION
                    else exc.message
                ),
                "status_code": exc.status_code,
                "data": {},
            },
        )

    @application.exception_handler(NotFoundError)
    async def not_found_error_handler(
            request: Request, exc: NotFoundError
    ) -> JSONResponse:
        """Handle resource not found errors"""
        logging.info(f"NotFoundError: {exc.message}")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "not_found",
                "message": exc.message,
                "status_code": exc.status_code,
                "data": {},
            },
        )

    @application.exception_handler(ValidationError)
    async def validation_error_handler(
            request: Request, exc: ValidationError
    ) -> JSONResponse:
        """Handle data validation errors"""
        logging.warning(f"ValidationError: {exc.message}")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "validation_error",
                "message": exc.message,
                "status_code": exc.status_code,
                "data": {},
            },
        )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(
            request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle FastAPI request validation errors"""
        # extract the raw list of error dicts
        raw_errors = exc.errors()
        # Turn them into JSON-serializable form
        safe_errors = jsonable_encoder(raw_errors)

        # build human friendly messages
        messages = []
        for err in raw_errors:
            # Handle location items that might be integers (like list indices)
            loc_parts = []
            for loc_item in err["loc"]:
                if isinstance(loc_item, str):
                    loc_parts.append(loc_item.replace("_", " ").title())
                elif isinstance(loc_item, int):
                    loc_parts.append(f"item {loc_item}")

            # Skip body/query/path prefixes for cleaner messages
            filtered_loc = [
                part for part in loc_parts if part not in ("Body", "Query", "Path")
            ]
            field = " ".join(filtered_loc) or "Field"

            if expected := err.get("ctx", {}).get("expected"):
                messages.append(f"{field} must be {expected}")
            else:
                # strip a leading "Value error," if present
                msg = err["msg"].split(",", 1)[-1].strip()
                messages.append(f"{field}: {msg}")

        human_msg = ";; ".join(messages) or "Validation error"

        logging.warning(f"RequestValidationError: {human_msg}")

        return JSONResponse(
            status_code=422,
            content={
                "error": (
                    "validation_error"
                    if settings.ENVIRONMENT == EnvironmentOption.PRODUCTION
                    else safe_errors
                ),
                "message": human_msg,
                "status_code": 422,
                "data": {},
            },
        )

    @application.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle FastAPI HTTP exceptions"""
        # Log full exception details
        if exc.status_code >= 500:
            logging.error(f"HTTPException {exc.status_code}: {exc.detail}", exc_info=True)
        else:
            logging.warning(f"HTTPException {exc.status_code}: {exc.detail}")

        return JSONResponse(
            content={
                "error": (
                    "request_error" if exc.status_code < 500 else "server_error"
                    if settings.ENVIRONMENT == EnvironmentOption.PRODUCTION
                    else getattr(exc, "name", type(exc).__name__)
                ),
                "message": (
                    exc.detail
                    if exc.status_code < 500 or settings.ENVIRONMENT != EnvironmentOption.PRODUCTION
                    else "An unexpected error occurred. Please try again later."
                ),
                "status_code": exc.status_code,
                "data": {},
            },
            status_code=exc.status_code,
        )

    # SQLAlchemy specific exception handlers
    @application.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """Handle database integrity errors (unique constraints, foreign key violations)"""
        logging.error(f"IntegrityError: {str(exc)}", exc_info=True)

        message = "Data integrity error"
        if "unique constraint" in str(exc).lower():
            message = "Duplicate entry found"
        elif "foreign key" in str(exc).lower():
            message = "Referenced resource not found"

        return JSONResponse(
            status_code=409,
            content={
                "error": (
                    "conflict"
                    if settings.ENVIRONMENT == EnvironmentOption.PRODUCTION
                    else "IntegrityError"
                ),
                "message": (
                    message
                    if settings.ENVIRONMENT == EnvironmentOption.PRODUCTION
                    else f"{message}: {str(exc)}"
                ),
                "status_code": 409,
                "data": {},
            },
        )

    @application.exception_handler(NoResultFound)
    async def no_result_found_handler(request: Request, exc: NoResultFound):
        """Handle no result found errors from SQLAlchemy"""
        logging.info(f"NoResultFound: {str(exc)}")

        return JSONResponse(
            status_code=404,
            content={
                "error": "not_found",
                "message": "Requested resource not found",
                "status_code": 404,
                "data": {},
            },
        )

    @application.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        """Handle generic SQLAlchemy errors"""
        logging.error(f"SQLAlchemyError: {str(exc)}", exc_info=True)

        return JSONResponse(
            status_code=500,
            content={
                "error": (
                    "database_error"
                    if settings.ENVIRONMENT == EnvironmentOption.PRODUCTION
                    else "SQLAlchemyError"
                ),
                "message": (
                    "A database error occurred. Please try again later."
                    if settings.ENVIRONMENT == EnvironmentOption.PRODUCTION
                    else f"Database error: {str(exc)}"
                ),
                "status_code": 500,
                "data": {},
            },
        )

    @application.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handle any unhandled exceptions"""
        logging.error(f"Unhandled exception: {str(exc)}", exc_info=True)

        return JSONResponse(
            status_code=500,
            content={
                "error": (
                    "server_error"
                    if settings.ENVIRONMENT == EnvironmentOption.PRODUCTION
                    else type(exc).__name__
                ),
                "message": "An unexpected error occurred. Please try again later.",
                "status_code": 500,
                "data": {},
            },
        )


# -------------- application factory --------------
def create_application(
        router: APIRouter,
        settings: DatabaseSettings | AppSettings | EnvironmentSettings,
        create_tables_on_start: bool = True,
        **kwargs: Any,
) -> FastAPI:
    """Creates and configures a FastAPI application with enhanced error handling."""

    # Configure application metadata
    if isinstance(settings, AppSettings):
        to_update = {
            "title": settings.APP_NAME,
            "description": settings.APP_DESCRIPTION,
            "contact": {"name": settings.CONTACT_NAME, "email": settings.CONTACT_EMAIL},
            "license_info": {"name": settings.LICENSE_NAME},
        }
        kwargs.update(to_update)

    if isinstance(settings, EnvironmentSettings):
        kwargs.update({"docs_url": None, "redoc_url": None, "openapi_url": None})

    lifespan = lifespan_factory(settings, create_tables_on_start=create_tables_on_start)

    application = FastAPI(lifespan=lifespan, **kwargs)

    # CORS configuration
    origins = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(router)

    # Setup all exception handlers
    setup_exception_handlers(application, settings)

    # Documentation routes for non-production environments
    if isinstance(settings, EnvironmentSettings):
        docs_router = APIRouter()

        @docs_router.get("/docs", include_in_schema=False)
        async def get_redoc_documentation() -> fastapi.responses.HTMLResponse:
            return get_redoc_html(openapi_url="/openapi.json", title="docs")

        @docs_router.get("/openapi.json", include_in_schema=False)
        async def openapi() -> dict[str, Any]:
            out: dict = get_openapi(
                title=application.title,
                version=application.version,
                routes=application.routes,
            )
            return out

        application.include_router(docs_router)

    return application
