import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.auth.utils import decode_token
from app.ws.manager import manager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws")
async def websocket_endpoint(
    ws: WebSocket,
    token: str = Query(...),
) -> None:
    """
    WebSocket endpoint.

    Auth: JWT access token passed as ?token=<jwt>.
    Closes with code 4001 if the token is invalid.

    Supported client → server messages:
      { "type": "ping" }          → server replies { "type": "pong" }
      { "type": "chat_message" }  → not yet implemented, returns an error frame

    Server → client push messages (see wsTypes.ts for full contract):
      { "type": "notification", "payload": { ... } }
    """
    try:
        payload = decode_token(token)
        user_id = int(payload["sub"])
    except Exception:
        await ws.accept()
        await ws.close(code=4001)
        return

    await manager.connect(user_id, ws)
    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type")

            if msg_type == "ping":
                await ws.send_json({"type": "pong"})

            elif msg_type == "chat_message":
                # AI chat is not yet implemented
                await ws.send_json({
                    "type": "error",
                    "payload": {
                        "code": "CHAT_ERROR",
                        "message": "AI chat is not yet implemented",
                    },
                })

    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(user_id)
