from fastapi import WebSocket, WebSocketDisconnect
from .room_manager import room_manager


async def handle_websocket(websocket: WebSocket, room_id: str, username: str):
    if not username or not username.strip():
        await websocket.close(code=1008)
        return

    username = username.strip()

    await room_manager.connect(room_id, username, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "message":
                text = data.get("text", "")

                if len(text) > 300:
                    await room_manager.send_to_user(
                        room_id,
                        username,
                        {
                            "type": "error",
                            "detail": "Message is too long"
                        }
                    )
                else:
                    await room_manager.broadcast(
                        room_id,
                        {
                            "type": "message",
                            "room_id": room_id,
                            "username": username,
                            "text": text
                        }
                    )

    except WebSocketDisconnect:
        room_manager.disconnect(room_id, username)

        await room_manager.broadcast(
            room_id,
            {
                "type": "system",
                "text": f"{username} disconnected from chat",
                "username": "system"
            }
        )