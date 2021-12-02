from pydantic import BaseModel
from fastapi import Request
from fastapi.responses import JSONResponse
from hashlib import sha1
from common.config import API_TIMESTAMP_TIMEOUT
import time

from .logs import logger

G_USERS = {
    "3S2a6b1E": "19e31d2e32a6619e",
    "19e3B02E": "83S3202e32e6619e",
    "28F3B02a": "43S3103g32e6619d",
    "49H2B02c": "53h3233g32b683ad"
}


def api_auth(request: Request):
    app_id = request.query_params.get("appid", False)
    timestamp = request.query_params.get("timestamp", False)
    sign = request.query_params.get("sign", False)

    if not app_id:
        app_id = request.headers.get("x-auth-appid", False)
    if not timestamp:
        timestamp = request.headers.get("x-auth-timestamp", False)
    if not sign:
        sign = request.headers.get("x-auth-sign", False)

    if timestamp and (int(time.time()) - int(timestamp)) > API_TIMESTAMP_TIMEOUT:
        return False, "sign timeout"

    secret = G_USERS.get(app_id, False)
    if not secret:
        return False, "appid not exists"

    uri = request.scope["path"]

    en_str = uri + app_id + timestamp + secret

    s1 = sha1()
    s1.update(en_str.encode("utf-8"))
    # logger.info(s1.hexdigest())

    if s1.hexdigest() != sign:
        return False, "sign error"

    return True, ""
