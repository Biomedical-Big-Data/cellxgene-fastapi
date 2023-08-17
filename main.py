import uvicorn
from routers import user, project
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
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
    uvicorn.run(app, host="0.0.0.0", port=5050)
