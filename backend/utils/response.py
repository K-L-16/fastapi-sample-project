from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
def success_response(message:str = "success", data = None):
    content = {
        "code": 200,
        "message": message,
        "data": data
    }
    #把任何的fastapi，pydantic，orm对象 都要正常响应 -》 code，mesage，data
    return JSONResponse(content=jsonable_encoder(content))