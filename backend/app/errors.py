import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str):
        self.status, self.code, self.message = status, code, message


def _body(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse({"code": code, "message": message}, status_code=status)


def install(app: FastAPI) -> None:
    """Every error leaves the API as {code, message}."""

    @app.exception_handler(ApiError)
    async def _api(_: Request, e: ApiError):
        return _body(e.status, e.code, e.message)

    @app.exception_handler(HTTPException)
    async def _http(_: Request, e: HTTPException):
        return _body(e.status_code, "http_error", str(e.detail))

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, e: RequestValidationError):
        return _body(422, "validation_error", "; ".join(f"{'.'.join(map(str, x['loc']))}: {x['msg']}" for x in e.errors()))

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, e: Exception):
        # Without this, an unexpected exception bypasses CORSMiddleware (Starlette's
        # ServerErrorMiddleware sits outside it), so the browser reports a bare network
        # error instead of a response the frontend can show the user. Logged explicitly
        # since registering this handler stops Starlette's own traceback logging.
        logging.exception("Unhandled exception")
        return _body(500, "internal_error", "Internal server error")
