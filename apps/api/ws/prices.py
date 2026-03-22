"""
WebSocket endpoint for real-time price streaming.
"""

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from apps.api.services.ws_manager import manager

router = APIRouter()


@router.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """
    WebSocket endpoint for real-time price updates.

    Client can send:
      {"subscribe": ["AAPL", "MSFT"]}
      {"unsubscribe": ["AAPL"]}

    Server sends:
      {"type": "price_update", "ticker": "AAPL", "price": 182.50, ...}
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if "subscribe" in msg:
                    manager.subscribe(websocket, msg["subscribe"])
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "tickers": list(manager.subscriptions.get(websocket, [])),
                    }))
                elif "unsubscribe" in msg:
                    manager.unsubscribe(websocket, msg["unsubscribe"])
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
