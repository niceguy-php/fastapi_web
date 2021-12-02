from fastapi import FastAPI, Body, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from fastapi.exceptions import StarletteHTTPException
import time

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
import traceback

from common.logs import logger
from common.appid_auth import api_auth
from common.jwt_auth import jwt_auth
from common.config import REDIS_DB, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, API_AUTH_ENABLE, API_AUTH_TYPE
# from aioredis import create_redis_pool, Redis


from aredis import StrictRedis
from starlette.responses import StreamingResponse

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="FastAPI Docs Test",
    description="FastAPI Application Params Test",
    version="1.1.1",
    docs_url="/docs"
)

app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.mount("/static", StaticFiles(directory="./static"), name="static")
templates = Jinja2Templates(directory="./templates")


async def get_redis_pool():
    # redis = await create_redis_pool(f"redis://:@"+REDIS_HOST+":"+REDIS_PORT+"/"+REDIS_DB+"?encoding=utf-8")
    # redis = await create_redis_pool((REDIS_HOST, REDIS_PORT), db=REDIS_DB, encoding='utf-8')
    redis = StrictRedis(host='127.0.0.1', port=6379, db=0)
    return redis


@app.middleware("http")
async def add_precess_time_header(request: Request, call_next):
    start_time = time.time()
    current_uri = request.scope["path"]

    allow_uris = ["/docs","/openapi.json","/user/login"]


    if API_AUTH_TYPE == "jwt":
        flag, msg = jwt_auth(request)

    if API_AUTH_TYPE == "appid":
        flag, msg = api_auth(request)

    if API_AUTH_ENABLE and (current_uri not in allow_uris) and not flag:
        return JSONResponse({"code": 401, "message": msg, "data": {}})

    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers['X-Process-Time'] = str(process_time)
    response.headers['valid-count'] = str(1)
    # response.headers['server'] = "www"
    # logger.info(str(response.status_code))
    # if response.status_code == 429:
    #     logger.error(429)
    return response


@app.get('/status')
@limiter.limit("5/minute")
async def index(request: Request):
    return "ok\n"


@app.on_event("startup")
async def startup_event():
    pass
    # rs = StrictRedis(host='127.0.0.1', port=6379, db=0, max_idle_time=2, idle_check_interval=0.1)
    # print(await rs.info())
    # print(await rs.set("aa",10))
    # print(await rs.get("aa"))
    # app.redis = get_redis_pool()
    # app.state.redis = await get_redis_pool()


@app.on_event("shutdown")
async def shutdown_event():
    pass
    # app.state.redis.close()
    # await app.state.redis.wait_closed()


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

    try:
        # logger.error(str(exc.errors()))
        for v in exc.errors():
            # logger.info(str(v))
            # logger.info(str(v["loc"]))
            k1 = "#".join(v["loc"][1:])
            unvalid_info[k1] = v["msg"]
    except Exception as e:
        logger.error(traceback.format_exc())
        return JSONResponse({"code": 500, "message": "server error", "data": {}})

    return JSONResponse({"code": 1003, "message": "参数格式不正确", "data": unvalid_info})


'''
controller routers
'''
from controllers.user import usersRouter

app.include_router(usersRouter, prefix="/user", tags=['users'])

if __name__ == '__main__':
    import uvicorn

    # print(cpu_count())
    uvicorn.run(app="main:app", host="0.0.0.0", port=5005, workers=1, access_log=True, debug=True, use_colors=True,
                reload=True)
