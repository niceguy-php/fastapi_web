from fastapi.responses import JSONResponse


def success(data={}):
    return JSONResponse({"code": 0, "message": "success", "data": data})


def fail(code=0,message="fail",data={}):
    return JSONResponse({"code": code, "message": message, "data": data})