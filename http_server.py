from controllers.user import usersRouter
from exception_handler import *
from middleware import *
from __init__ import app

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles




limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter

app.mount("/static", StaticFiles(directory="./static"), name="static")
templates = Jinja2Templates(directory="./templates")

@app.on_event("startup")
async def startup_event():
    pass


@app.on_event("shutdown")
async def shutdown_event():
    pass

@app.get('/status')
@limiter.limit("5/minute")
async def index(request: Request):
    return "ok\n"


app.include_router(usersRouter, prefix="/user", tags=['users'])

if __name__ == '__main__':
    import uvicorn

    # print(cpu_count())
    uvicorn.run(app="http_server:app", host="0.0.0.0", port=5006, workers=1, access_log=True, debug=True, use_colors=True,
                reload=True)
