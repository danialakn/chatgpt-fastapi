from fastapi import FastAPI

from routers import users , health

app = FastAPI()
app.include_router(users.router, tags=["users"])
app.include_router(health.router, tags=["health"])