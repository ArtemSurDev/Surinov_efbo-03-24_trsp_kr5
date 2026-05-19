from fastapi import FastAPI
from .routers import tasks, users, admin

app = FastAPI(
    title="Task Management API",
    description="API with dependency injection and extended routing",
    version="1.0.0"
)

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


def clear_storage():
    from .storage import get_storage
    get_storage().clear()