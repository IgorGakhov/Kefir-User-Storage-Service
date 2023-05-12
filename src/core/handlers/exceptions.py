from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


SERVER_ERROR_MESSAGE: str = 'Что-то пошло не так, мы уже исправляем эту ошибку.'


class ErrorResponseModel(BaseModel):
    code: int
    message: str


class CodelessErrorResponseModel(BaseModel):
    message: str


async def internal_exception_handler(request: Request, exception: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=SERVER_ERROR_MESSAGE
    )


async def client_http_exception_handler(request: Request,
                                        exception: HTTPException):
    if exception.status_code == status.HTTP_400_BAD_REQUEST:
        error = ErrorResponseModel(
            code=exception.status_code,
            message=exception.detail
        )
    else:
        error = CodelessErrorResponseModel(message=exception.detail)
    return JSONResponse(status_code=exception.status_code, content=error.dict())
