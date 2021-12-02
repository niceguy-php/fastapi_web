from slowapi.errors import RateLimitExceeded
from fastapi import Request
from starlette.exceptions import HTTPException
from fastapi.exceptions import StarletteHTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from common.logs import logger
from __init__ import app

@app.exception_handler(RateLimitExceeded)
def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    response = JSONResponse(
        {"code": 429, "message": f"Rate limit exceeded: {exc.detail}"}, status_code=429
    )
    response = request.app.state.limiter._inject_headers(
        response, request.state.view_rate_limit
    )
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc):
    return JSONResponse({"code": 500, "message": str(exc.detail), "data": {}})


@app.exception_handler(StarletteHTTPException)
async def not_found(request, exc):
    return JSONResponse({"code": 404, "message": "您要找的页面去火星了..."})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    unvalid_info = {}
    for v in exc.errors():
        logger.info(str(v))
        logger.info(str(v["loc"]))
        k1 = "#".join(v["loc"][1:])
        unvalid_info[k1] = v["msg"]

    return JSONResponse({"code": 1003, "message": "参数格式不正确", "data": unvalid_info})