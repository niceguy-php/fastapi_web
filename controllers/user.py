from fastapi import APIRouter, status, Request, Body, Query
from fastapi import Depends, HTTPException, Header
from .schemas import WebResponse, UserOut, UserIn, UserType
from typing import Optional, List, Union
from common.redis import g_redis
from common.jwt_auth import create_token
from common.return_data import success,fail

usersRouter = APIRouter()


@usersRouter.post("/create", response_model=WebResponse[UserOut])
def create(user: UserIn):
    return WebResponse(code=0, data=user).dict()


@usersRouter.post("/delete", summary='删除用户', description="如何删除", response_description="test")
def delete():
    pass


@usersRouter.post("/view", responses={
    404: {"model": WebResponse, "description": "The item was not found"},
    "200": {
        "description": "Successful Response",
        "content": {
            "application/json": {
                "schema": {
                    "required": ["name", "price"],
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "price": {"type": "number"},
                        "description": {"type": "string"},
                    },
                }
            }
        }
    },
    "422": {
        "description": "Validation Error",
        "content": {
            "application/json": {
                "example": {"id": "bar", "value": "The bar tenders"}
            }
        }
    }
})
def view():
    pass


@usersRouter.post("/update", openapi_extra={
    "requestBody": {
        "content": {
            "application/json": {
                "schema": {
                    "required": ["name", "price"],
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "price": {"type": "number"},
                        "description": {"type": "string"},
                    },
                }
            }
        },
        "required": True,
    },
}, )
def update(ui: UserIn, uo: UserOut, id: int, id2: int = Body(...), q: List[str] = Query(["foo", "bar"])):
    return ui


@usersRouter.get("/redis_set")
async def redis_set(request: Request):
    test = {
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {
                        "required": ["name", "price"],
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "price": {"type": "number"},
                            "description": {"type": "string"},
                        },
                    }
                }
            },
            "required": True,
        },
    }

    useris = await g_redis.set("auser", str(test))
    return useris


@usersRouter.get("/redis_get")
async def redis_set(request: Request):
    useris = await g_redis.get("auser")
    return useris


@usersRouter.get("/users/{user_type}")
async def get_user(user_type: UserType):
    return {"user_id": user_type, "type": UserType.admin}


@usersRouter.get("/user/")
async def get_user1(user_id: str, name: str, sex: Union[int, str], age: int = 0):
    return {"user_id": user_id, "name": name}


@usersRouter.get("/pass")
async def check_length(
        # 默认值为 None，应该声明为 Optional[str]，当然声明 str 也是可以的。只不过声明为 str，那么默认值应该也是 str
        # 所以如果一个类型允许为空，那么更规范的做法应该是声明为 Optional[类型]。
        password: Optional[str] = Query(None, min_length=6, max_length=15),
        password2: Optional[str] = Query(..., min_length=6, max_length=15)

):
    return {"password": password}


@usersRouter.get("/login")
async def login_get_token(username: str, password: str):
    flag, tokenOrMsg = create_token(username, password)
    if flag:
        return success({"token": tokenOrMsg})
    else:
        return fail(401,tokenOrMsg)


@usersRouter.get("/login",responses={
    422: {},
    # "200": {},
    "200": {
        "description": "Successful Response",
        "content": {
            "application/json": {
                "example": {"code": 0,"message": "success","data": {"token": "xxxxx"}}
            }
        }
    },
    "401": {
        "description": "Validation Error",
        "content": {
            "application/json": {
                "example": {'code': 401, 'message': 'user not exists', 'data': {}}
            }
        }
    }
})
async def login_get_token(username: str, password: str):
    flag, tokenOrMsg = create_token(username, password)
    if flag:
        return success({"token": tokenOrMsg})
    else:
        return fail(401,tokenOrMsg)
