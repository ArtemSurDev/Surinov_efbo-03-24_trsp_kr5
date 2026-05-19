from fastapi import FastAPI
from .routers import tasks

app = FastAPI(
    title="Task Management API",
    description="API for managing tasks with authentication via X-User-Id header",
    version="1.0.0"
)

app.include_router(tasks.router)

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}

def clear_storage():
    from .storage import get_storage
    get_storage().clear()