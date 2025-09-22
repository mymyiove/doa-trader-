from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.routes.dashboard import router as dashboard_router
from app.scheduler import setup_scheduler

app = FastAPI()

# ✅ 정적 파일 서빙: /static → web/static/
static_dir = Path(__file__).parent.parent / "web" / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ✅ UI 라우터 등록: /ui/price, /ui/status 등
app.include_router(dashboard_router, prefix="/ui")

# ✅ 스케줄러 등록 (장전/장중/장후 루틴)
setup_scheduler(app)
