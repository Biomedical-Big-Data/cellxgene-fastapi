import uvicorn
from routers import users
from fastapi import Depends, FastAPI, Request, status, HTTPException
from orm.dependencies import get_db
from utils.auth_util import verify_user_token
from fastapi.responses import RedirectResponse
from orm.schema.response import ResponseMessage


app = FastAPI()
app.include_router(users.router)


# async def exception_callback(request: Request, exc: Exception):
#     print(request, exc)


@app.middleware("http")
async def verify_token(request: Request, call_next):
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    path: str = request.get("path")
    if (
        path.startswith("/users/login")
        | path.startswith("/docs")
        | path.startswith("/openapi")
        | path.startswith("/users/register")
        | path.startswith("/users/email/verify")
        | path.startswith("/favicon.ico")
        | path.startswith("/users/password/reset")
        | path.startswith("/users/password/reset/template")
        | path.startswith("/users/password/reset/mail/send")
    ):
        response = await call_next(request)
        return response
    else:
        try:
            token: str = request.headers.get("token", "")
            if not token:
                raise auth_error
            verify_result, email_address, verify_message = verify_user_token(
                next(get_db()), token
            )
            if verify_result:
                response = await call_next(request)
                print('response', response)
                return response
            else:
                raise auth_error
        except Exception as e:
            print(e)
            raise auth_error


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/favicon.ico")
def static_main_action():
    return RedirectResponse("/static/favicon.ico")


if __name__ == "__main__":
    # await verify_token(app)
    uvicorn.run(app, host="0.0.0.0", port=5050)
