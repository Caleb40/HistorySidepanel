from fastapi import HTTPException


class CustomApplicationException(HTTPException):
    def __init__(
            self,
            *,
            status_code: int,
            detail: str,
            error: str | None = None,
            data: dict | str | None = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error = error or self.__class__.__name__
        self.data = data or {}
