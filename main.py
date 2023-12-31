import uvicorn
import logging
import asyncio
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.responses import JSONResponse
from orm.schema.response import ResponseMessage
from routers import user, project, admin
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from orm.schema.exception_model import BusinessException

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
app.include_router(admin.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    error_message = ResponseMessage(status="0201", data={}, message=exc.errors())
    return JSONResponse(
        error_message.to_dict(), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    error_message = ResponseMessage(status="0201", data={}, message=exc.detail)
    return JSONResponse(
        error_message.to_dict(), status_code=status.HTTP_401_UNAUTHORIZED
    )


@app.exception_handler(BusinessException)
async def http_business_exception_handler(request: Request, exc: BusinessException) -> JSONResponse:
    error_message = ResponseMessage(status="0201", data={}, message=exc.message)
    return JSONResponse(
        content=error_message.to_dict(), status_code=status.HTTP_200_OK
    )



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
    logging.basicConfig(
        level=logging.INFO,  # 设置记录级别
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # 设置日志格式
    )
    from mqtt_consumer.consumer import Consumer

    consumer = Consumer()

    @app.on_event("startup")
    async def startup_event():
        await consumer.initialize()

    @app.on_event("shutdown")
    async def shutdown_event():
        await consumer.shutdown()

    uvicorn.run(app, host="0.0.0.0", port=5051)
