from fastapi import FastAPI
from api.health import router as health
from api.receipts import router as receipts
from api.inventory import router as inventory
from db.database import init_db

app = FastAPI(title="StockScan Profit ULTRA", version="1.0.0")

@app.on_event("startup")
def startup():
    init_db()

app.include_router(health)
app.include_router(receipts, prefix="/v1")
app.include_router(inventory, prefix="/v1")
