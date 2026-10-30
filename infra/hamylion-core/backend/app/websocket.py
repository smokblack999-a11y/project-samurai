import asyncio
from collections import defaultdict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.connections=defaultdict(set)
        self.lock=asyncio.Lock()

    async def connect(self,project_id,websocket):
        await websocket.accept()
        async with self.lock:
            self.connections[project_id].add(websocket)

    async def disconnect(self,project_id,websocket):
        async with self.lock:
            self.connections[project_id].discard(websocket)
            if not self.connections[project_id]:
                self.connections.pop(project_id,None)

    async def broadcast(self,project_id,event):
        async with self.lock:
            clients=list(self.connections.get(project_id,set()))
        for websocket in clients:
            try:
                await websocket.send_json(event)
            except Exception:
                await self.disconnect(project_id,websocket)

manager=ConnectionManager()
