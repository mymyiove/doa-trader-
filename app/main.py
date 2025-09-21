from fastapi import FastAPI
from app.scheduler import start_schedulers
from app.routes import dashboard, health, orders

app = FastAPI(title="DOA Trader", version="0.1")

app.include_router(dashboard.router, prefix="/ui")
app.include_router(health.router, prefix="/health")
app.include_router(orders.router, prefix="/orders")

@app.on_event("startup")
async def boot():
    await start_schedulers()

@app.get("/")
async def root():
    return {"status": "DOA Trader running"}
