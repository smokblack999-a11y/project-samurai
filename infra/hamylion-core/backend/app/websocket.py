import asyncio
from collections import defaultdict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.connections=defaultdict(set)
        self.lock=asyncio.Lock()

    async def connect(self,p,w):
        await w.accept()
        async with self.lock:
            self.connections[p].add(w)

    async def disconnect(self,p,w):
        async with self.lock:
            self.connections[p].discard(w)

    async def broadcast(self,p,event):
        async with self.lock:
            clients=list(self.connections.get(p,set()))
        delivered=0
        for w in clients:
            try:
                await w.send_json(event)
                delivered += 1
            except Exception:
                await self.disconnect(p,w)
        return delivered

manager=ConnectionManager()
