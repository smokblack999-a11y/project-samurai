import asyncio
from collections import defaultdict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.connections=defaultdict(dict)
        self.lock=asyncio.Lock()

    async def connect(self,p,client_id,w):
        await w.accept()
        async with self.lock:
            self.connections[p][client_id]=w

    async def disconnect(self,p,client_id):
        async with self.lock:
            self.connections[p].pop(client_id,None)

    async def clients(self,p):
        async with self.lock:
            return list(self.connections.get(p,{}).items())

    async def broadcast(self,p,event):
        recipients=await self.clients(p)
        delivered=[]
        failed=[]
        for client_id,w in recipients:
            try:
                await w.send_json(event)
                delivered.append(client_id)
            except Exception:
                failed.append(client_id)
                await self.disconnect(p,client_id)
        return delivered, failed

manager=ConnectionManager()
