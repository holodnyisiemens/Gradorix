from __future__ import annotations

import asyncio
from typing import Dict

from fastapi import WebSocket


class ConnectionManager:
    """Singleton that tracks active WebSocket connections keyed by user_id."""

    def __init__(self) -> None:
        self._connections: Dict[int, WebSocket] = {}
        self._lock = asyncio.Lock()

    async def connect(self, user_id: int, ws: WebSocket) -> None:
        """Accept the connection and register it. Closes any previous connection for this user."""
        await ws.accept()
        async with self._lock:
            old = self._connections.get(user_id)
            if old is not None:
                try:
                    await old.close(code=1001)
                except Exception:
                    pass
            self._connections[user_id] = ws

    async def disconnect(self, user_id: int) -> None:
        async with self._lock:
            self._connections.pop(user_id, None)

    async def send_to_user(self, user_id: int, message: dict) -> bool:
        """
        Send a JSON message to a connected user.
        Returns True if the message was sent, False if the user is not connected.
        Removes the connection if sending fails.
        """
        ws = self._connections.get(user_id)
        if ws is None:
            return False
        try:
            await ws.send_json(message)
            return True
        except Exception:
            await self.disconnect(user_id)
            return False

    def is_connected(self, user_id: int) -> bool:
        return user_id in self._connections


manager = ConnectionManager()
