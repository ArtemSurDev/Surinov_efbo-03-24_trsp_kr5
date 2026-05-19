from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.params import Query
from typing import Optional
from .websocket_handler import handle_websocket
from .room_manager import room_manager
from .schemas import UserListResponse

app = FastAPI(
    title="WebSocket Chat",
    description="Chat with rooms using WebSocket",
    version="1.0.0"
)


@app.websocket("/ws/rooms/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    username: Optional[str] = Query(None)
):
    await handle_websocket(websocket, room_id, username)


@app.get("/rooms/{room_id}/users", response_model=UserListResponse)
async def get_room_users(room_id: str):
    users = room_manager.get_users(room_id)
    return UserListResponse(room_id=room_id, users=users)


@app.get("/health")
async def health_check():
    return {"status": "ok"}