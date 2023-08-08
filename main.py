import uvicorn
from routers import user, project
from fastapi import Depends, FastAPI, Request, status, HTTPException
from orm.dependencies import get_db
from utils.auth_util import verify_user_token
from fastapi.responses import RedirectResponse
from starlette.responses import Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user.router)
app.include_router(project.router)


# async def exception_callback(request: Request, exc: Exception):
#     print(request, exc)


@app.middleware("http")
async def verify_token(request: Request, call_next):
    auth_error = Response(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    path: str = request.get("path")
    if (
        path.startswith("/user/login")
        | path.startswith("/docs")
        | path.startswith("/openapi")
        | path.startswith("/user/register")
        | path.startswith("/user/email/verify")
        | path.startswith("/favicon.ico")
        | path.startswith("/static/favicon.ico")
        | path.startswith("/user/password/reset")
        | path.startswith("/user/password/reset/template")
        | path.startswith("/user/password/reset/mail/send")
        | path.startswith("/project")
    ):
        response = await call_next(request)
        return response
    else:
        try:
            token: str = request.headers.get("token", "")
            if not token:
                return auth_error
            verify_result, email_address, verify_message = verify_user_token(
                next(get_db()), token
            )
            if verify_result:
                response = await call_next(request)
                return response
            else:
                return auth_error
                # raise auth_error
        except Exception as e:
            print(e)
            return auth_error


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
