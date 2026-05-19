from fastapi import WebSocket
from typing import Dict, Set
import asyncio


class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, room_id: str, username: str, websocket: WebSocket):
        await websocket.accept()

        if room_id not in self.rooms:
            self.rooms[room_id] = {}

        self.rooms[room_id][username] = websocket

        await self.broadcast(
            room_id,
            {
                "type": "system",
                "text": f"{username} connected to chat",
                "username": "system"
            }
        )

    def disconnect(self, room_id: str, username: str):
        if room_id in self.rooms:
            if username in self.rooms[room_id]:
                del self.rooms[room_id][username]

            if not self.rooms[room_id]:
                del self.rooms[room_id]

    async def broadcast(self, room_id: str, message: dict):
        if room_id in self.rooms:
            for username, websocket in self.rooms[room_id].items():
                try:
                    await websocket.send_json(message)
                except:
                    pass

    async def send_to_user(self, room_id: str, username: str, message: dict):
        if room_id in self.rooms and username in self.rooms[room_id]:
            try:
                await self.rooms[room_id][username].send_json(message)
            except:
                pass

    def get_users(self, room_id: str) -> list:
        if room_id in self.rooms:
            return list(self.rooms[room_id].keys())
        return []

    def get_all_rooms(self) -> Dict[str, Set[str]]:
        return {room_id: set(users.keys()) for room_id, users in self.rooms.items()}


room_manager = RoomManager()