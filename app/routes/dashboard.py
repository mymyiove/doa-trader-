from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.log import audit

router = APIRouter()

# 정적 파일 서빙
static_dir = Path(__file__).parent.parent.parent / "web" / "static"
router.mount("/static", StaticFiles(directory=static_dir), name="static")

# 대시보드 HTML
@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    html_path = Path(__file__).parent.parent.parent / "web" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

# 최근 로그 조회 API
@router.get("/logs")
async def get_logs(limit: int = 50):
    return audit.get_recent(limit)
