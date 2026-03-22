"""
WebSocket connection manager for real-time price broadcasting.
"""

import json
import asyncio
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.subscriptions: dict[WebSocket, set[str]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.subscriptions[websocket] = set()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        self.subscriptions.pop(websocket, None)

    def subscribe(self, websocket: WebSocket, tickers: list[str]):
        if websocket in self.subscriptions:
            self.subscriptions[websocket].update(tickers)

    def unsubscribe(self, websocket: WebSocket, tickers: list[str]):
        if websocket in self.subscriptions:
            self.subscriptions[websocket] -= set(tickers)

    async def broadcast_price(self, ticker: str, data: dict):
        """Send price update to all subscribers of this ticker."""
        message = json.dumps({"type": "price_update", "ticker": ticker, **data})
        disconnected = []

        for ws in self.active_connections:
            subs = self.subscriptions.get(ws, set())
            if not subs or ticker in subs:  # Empty subs = subscribed to all
                try:
                    await ws.send_text(message)
                except Exception:
                    disconnected.append(ws)

        for ws in disconnected:
            self.disconnect(ws)

    async def broadcast_all(self, stocks: dict):
        """Broadcast all stock updates."""
        for ticker, data in stocks.items():
            await self.broadcast_price(ticker, data)


manager = ConnectionManager()
