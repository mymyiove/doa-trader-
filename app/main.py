from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.scheduler import start_schedulers
from app.routes import dashboard, health, orders

app = FastAPI(title="DOA Trader", version="1.0")

# 라우터 등록
app.include_router(dashboard.router, prefix="/ui")
app.include_router(health.router, prefix="/health")
app.include_router(orders.router, prefix="/orders")

@app.on_event("startup")
async def boot():
    await start_schedulers()

# 루트("/") 접속 시 /ui/로 리다이렉트
@app.get("/")
async def root():
    return RedirectResponse(url="/ui/")
