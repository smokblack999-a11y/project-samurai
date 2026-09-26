import asyncio
from collections import defaultdict
from dataclasses import dataclass
from fastapi import WebSocket

@dataclass
class Connection:
    id: str
    client_id: str
    websocket: WebSocket

class ConnectionManager:
    def __init__(self):
        self.connections=defaultdict(dict)
        self.lock=asyncio.Lock()

    async def connect(self,project_id,client_id,websocket):
        await websocket.accept()
        connection=Connection("ws_"+client_id,client_id,websocket)
        async with self.lock:
            self.connections[project_id][client_id]=connection
        return connection

    async def disconnect(self,project_id,client_id):
        async with self.lock:
            self.connections[project_id].pop(client_id,None)

    async def get(self,project_id):
        async with self.lock:
            return list(self.connections.get(project_id,{}).values())

    async def find(self,project_id,client_id):
        async with self.lock:
            return self.connections.get(project_id,{}).get(client_id)

manager=ConnectionManager()
