from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def api_response(
        success: bool = True,
        data: Any = None,
        message: str | None = None,
        status_code: int = 200,
) -> JSONResponse:
    """
    Returns a standardized API response.

    :param success: Indicates success or failure of the operation
    :param data: The payload to send when successful
    :param message: Optional message to include in the response
    :param status_code: HTTP status code
    :return: JSONResponse
    """
    payload = {
        "success": success,
        "data": data,
        "message": message,
    }
    return JSONResponse(
        content=jsonable_encoder(payload),
        status_code=status_code,
    )
