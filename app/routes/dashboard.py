from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

router = APIRouter()

# 정적 파일 서빙 (CSS, JS)
static_dir = Path(__file__).parent.parent.parent / "web" / "static"
router.mount("/static", StaticFiles(directory=static_dir), name="static")

@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    html_path = Path(__file__).parent.parent.parent / "web" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
