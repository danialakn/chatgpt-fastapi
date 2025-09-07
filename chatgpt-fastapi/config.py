from fastapi import FastAPI

from routers import chat_routes, health

app = FastAPI()
app.include_router(chat_routes.router, tags=["Chat"])
app.include_router(health.router, tags=["health"])
