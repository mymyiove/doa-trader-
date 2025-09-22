# app/main.py
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# 시간대 설정
TZ = os.getenv("TIMEZONE", "Asia/Seoul")

app = FastAPI(title="DOA Trader")

# 정적 파일 서빙: /static → web/static
static_dir = Path(__file__).parent.parent / "web" / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 라우터 등록
from app.routes.dashboard import router as dashboard_router
from app.routes.orders import router as orders_router
from app.routes.logs import router as logs_router

app.include_router(dashboard_router, prefix="/ui", tags=["ui"])
app.include_router(orders_router, prefix="/orders", tags=["orders"])
app.include_router(logs_router, prefix="/logs", tags=["logs"])

# 스케줄러 설정
from app.scheduler import setup_scheduler
setup_scheduler(app, timezone=TZ)
