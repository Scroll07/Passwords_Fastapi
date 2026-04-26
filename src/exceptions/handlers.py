from fastapi.responses import JSONResponse
from fastapi import Request, HTTPException, FastAPI


def exception_response(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def return_exception_response(request: Request, exc: HTTPException):
        return JSONResponse(
            content={"ok": False, "message": str(exc.detail)},
            status_code=exc.status_code,
            headers=exc.headers
        )






