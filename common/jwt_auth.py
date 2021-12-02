import jwt
from datetime import datetime, timedelta
from fastapi import Request
from common.logs import logger
from common.config import TOKEN_TIMEOUT
import time
import traceback
from jwt.exceptions import ExpiredSignatureError

SECRET_KEY = "sdifhgsiasfjaofhslio!@#sfsfabc1345666"  # JWY签名所使用的密钥，是私密的，只在服务端保存
ALGORITHM = "HS256"  # 加密算法，我这里使用的是HS256

G_USERS = {
    "user1": {
        "age": 10,
        "email": "test@x.com",
        "password": "123"
    }
}


def get_user(username):
    return G_USERS.get(username, False)


def create_token(username, password):
    user_info = get_user(username)
    token_expires = timedelta(seconds=TOKEN_TIMEOUT)
    if not user_info:
        return False, "user not exist"

    if password != user_info.get("password", False):
        return False, "password error"

    playload = {
        "sub": username,
        "exp": datetime.utcnow() + token_expires
    }
    logger.info(playload)
    token = jwt.encode(playload, SECRET_KEY, algorithm=ALGORITHM)
    return True, token


def jwt_auth(request: Request):
    try:
        token = request.query_params.get("token", False)
        if not token:
            token = request.headers.get("x-auth-token", False)

        if not token:
            return False, "token is required"

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        # exp = payload.get("exp")
        # logger.info("%f,%d" % (time.time(),int(exp)))
        # if int(time.time()) > int(exp):
        #     return False, "token timeout"
        #
        # logger.info(str(payload))
        if not get_user(username):
            return False, "user not exist"

        return True, "success"

    except ExpiredSignatureError as e:
        logger.error(traceback.format_exc())
        return False, "auth fail, token timeout"
    except Exception as e:
        logger.error(traceback.format_exc())
        return False, "auth fail, not allow access"
