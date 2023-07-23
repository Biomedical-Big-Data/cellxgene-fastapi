import uvicorn
from routers import users
from fastapi import Depends, FastAPI, Request, status, HTTPException


app = FastAPI()
app.include_router(users.router)

@app.middleware("http")
async def verify_token(request: Request, call_next):
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},  # OAuth2的规范，如果认证失败，请求头中返回“WWW-Authenticate”
    )
    # 获取请求路径
    path: str = request.get('path')
    # 登录接口、docs文档依赖的接口，不做token校验
    if path.startswith('/login') | path.startswith('/docs') | path.startswith('/openapi'):
        response = await call_next(request)
        return response
    else:
        try:
            # 从header读取token
            authorization: str = request.headers.get('authorization')
            if not authorization:
                response = Response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},  # OAuth2的规范，如果认证失败，请求头中返回“WWW-Authenticate”
                )
                return response
            # 拿到token值
            token = authorization.split(' ')[1]
            # 这个是我自己封装的校验token的逻辑，大家可以自己替换成自己的
            with SessionLocal() as db:
                if secret.verify_token(db, token):
                    logger.info("token验证通过")
                    response = await call_next(request)
                    return response
                else:
                    raise auth_error
        except Exception as e:
            logger.error(e)
            raise auth_error


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5050)
