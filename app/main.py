from fastapi import Depends, FastAPI

from .internal import admin
from .routers.apis import fullname, search, pageid

app = FastAPI()



app.include_router(fullname.router)
app.include_router(pageid.router)
app.include_router(search.router)
app.include_router(
    admin.router,
    prefix="",
    tags=["admin"],
    responses={418: {"description": "I'm a teapot"}},
)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}