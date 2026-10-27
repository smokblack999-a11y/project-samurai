from contextlib import asynccontextmanager

from fastapi import FastAPI
from api.health import router as health
from api.receipts import router as receipts
from api.inventory import router as inventory
from api.actions import router as actions
from db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="StockScan Profit ULTRA",
    version="1.1.0",
    lifespan=lifespan,
)

app.include_router(health)
app.include_router(receipts, prefix="/v1")
app.include_router(inventory, prefix="/v1")
app.include_router(actions, prefix="/v1")
