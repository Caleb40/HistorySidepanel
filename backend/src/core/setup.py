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
from starlette.requests import Request
from starlette.responses import JSONResponse

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


# -------------- application --------------
def create_application(
        router: APIRouter,
        settings: (
                DatabaseSettings
                | AppSettings
                | EnvironmentSettings
        ),
        create_tables_on_start: bool = True,
        **kwargs: Any,
) -> FastAPI:
    """Creates and configures a FastAPI application based on the provided settings.

    This function initializes a FastAPI application and configures it with various settings
    and tasks based on the type of the `settings` object provided.

    Parameters
    ----------
    router : APIRouter
        The APIRouter object containing the routes to be included in the FastAPI application.

    settings
        An instance representing the settings for configuring the FastAPI application.
        It determines the configuration applied:

        - AppSettings: Configures basic app metadata like name, description, contact, and license info.
        - DatabaseSettings: Adds event tasks for initializing database tables during startup.
        - EnvironmentSettings: Conditionally sets documentation URLs and integrates custom routes for API documentation
          based on the environment type.

    create_tables_on_start : bool
        A flag to indicate whether to create database tables on application startup.
        Defaults to True.

    **kwargs
        Additional keyword arguments passed directly to the FastAPI constructor.

    Returns
    -------
    FastAPI
        A fully configured FastAPI application instance.

    The function configures the FastAPI application with different features and behaviors
    based on the provided settings. It includes setting up database connections,
    client-side caching, and customizing the API documentation based on the environment settings.
    """
    # --- before creating application ---
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

    origins = [
        # *allowed_origins,
        "http://localhost:3000",
    ]

    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(router)

    @application.exception_handler(CustomApplicationException)
    async def custom_application_exception_handler(
            request: Request, exc: CustomApplicationException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error,
                "message": exc.detail,
                "status_code": exc.status_code,
                "data": exc.data,
            },
        )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(
            request: Request, exc: RequestValidationError
    ) -> JSONResponse:
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

        return JSONResponse(
            status_code=422,
            content={
                "error": safe_errors,
                "message": human_msg,
                "status_code": 422,
                "data": {},
            },
        )

    @application.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # Log full exception details
        logging.error(exc)

        return JSONResponse(
            content={
                "error": (
                    "request_error"
                    if settings.ENVIRONMENT == EnvironmentOption.PRODUCTION
                    else getattr(exc, "name", type(exc).__name__)
                ),
                "message": (
                    exc.detail
                    if exc.status_code < 500
                    else "An unexpected error occurred. Please try again later."
                ),
                "status_code": exc.status_code,
                "data": {},
            },
            status_code=exc.status_code,
        )

    @application.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        # Log full exception with traceback
        logging.error(exc)

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
